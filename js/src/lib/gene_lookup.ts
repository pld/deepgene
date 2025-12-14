// ABOUTME: Module for gene lookup using Vercel AI SDK (model-agnostic)
// ABOUTME: Defines structured schemas (like DSPy signatures) for querying gene information

import { generateObject } from 'ai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { z } from 'zod';
import type { GeneData, GeneLookupResult } from '../types';
import { formatGeneDataForLLM } from './gene_data';
import { fetchPaperContent } from './literature_fetcher';
import { extractMutants } from './mutant_extractor';

let provider: ReturnType<typeof createGoogleGenerativeAI> | null = null;

/**
 * Initialize AI SDK with API key.
 */
export function initializeGeneLookup(key: string): void {
  provider = createGoogleGenerativeAI({ apiKey: key });
}

/**
 * Gene information schema (like DSPy signature).
 */
const GeneInfoSchema = z.object({
  function: z.array(z.string()).default([]).describe('Biological function of the gene (provide detailed list)'),
  diseases: z
    .array(z.string())
    .default([])
    .describe('Associated diseases or conditions (provide comprehensive list)'),
  snps: z
    .array(
      z.object({
        id: z.string().describe('SNP identifier (e.g., rs12345)'),
        genes: z.array(z.string()).default([]).describe('Genes associated with the SNP'),
        phenotypes: z.array(z.string()).default([]).describe('Phenotypes associated with the SNP'),
      })
    )
    .default([])
    .describe('Associated SNPs with genes and phenotypes'),
  literature: z
    .array(
      z.object({
        functionalRelevance: z.string().describe('Functional relevance of the literature'),
        mutants: z.array(z.string()).default([]).describe('Mutants associated with the literature'),
        url: z.string().describe('URL of the literature (PubMed or journal URL, or empty string if none available)'),
      })
    )
    .default([])
    .describe('Literature references with PMIDs/URLs and functional relevance. If no literature is available, return an empty array instead of creating entries with placeholder URLs.'),
});

/**
 * Enhance literature with extracted mutants from paper content.
 */
async function enhanceLiteratureWithExtractions(
  literature: Array<{
    functionalRelevance: string;
    mutants: string[];
    url: string;
  }>,
  onProgress?: (message: string) => void
): Promise<
  Array<{
    functionalRelevance: string;
    mutants: string[];
    url: string;
  }>
> {
  const enhanced = [];

  for (let i = 0; i < literature.length; i++) {
    const lit = literature[i];
    onProgress?.(`Fetching paper ${i + 1}/${literature.length}: ${lit.url}`);
    const content = await fetchPaperContent(lit.url);

    if (content) {
      onProgress?.(`Extracting mutants from paper ${i + 1}/${literature.length}`);
      const extractedMutants = await extractMutants(content);

      const allMutants = Array.from(new Set([...lit.mutants, ...extractedMutants]));

      enhanced.push({
        ...lit,
        mutants: allMutants,
      });
    } else {
      enhanced.push(lit);
    }
  }

  return enhanced;
}

/**
 * Main gene lookup function using Vercel AI SDK (model-agnostic).
 *
 * This function uses structured output schemas (similar to DSPy signatures)
 * to get reliable, typed responses from any supported AI model.
 */
export async function lookupGene(
  rsid: string,
  annotation: string,
  positionalGene: string,
  geneData?: GeneData | null,
  key?: string,
  onProgress?: (message: string) => void
): Promise<GeneLookupResult> {
  if (!provider && key) {
    initializeGeneLookup(key);
  }

  if (!provider) {
    throw new Error('Provider not initialized. Provide key to lookupGene()');
  }

  const geneContext = geneData ? formatGeneDataForLLM(geneData) : '';

  const prompt = `You are a genetics research assistant. Analyze the given gene and rsID (reference SNP identifier).

CRITICAL INSTRUCTIONS:
- Even if the specific rsID is unknown or poorly documented, you MUST provide comprehensive information about the gene itself
- Include the gene's biological functions, associated diseases, and other well-known SNPs on this gene
- If you don't have information about the specific rsID, focus on the gene (${positionalGene}) and list other documented SNPs
- ALWAYS provide gene function and disease information if the gene is known
- Include related SNPs on the same gene with their phenotypes

Input:
- rsID: ${rsid} (may be unknown - if so, provide general gene information)
- Annotation: ${annotation}
- Positional Gene: ${positionalGene}
- Gene Database Info:
${geneContext || 'No database info provided'}

RESPONSE REQUIREMENTS:
1. function: List the gene's biological functions (REQUIRED - never leave empty for known genes)
2. diseases: List diseases/conditions associated with the gene (provide if known)
3. snps: List other known SNPs on this gene with their phenotypes (include the queried rsID if documented, plus other major SNPs on the gene)
4. literature: ONLY include entries with valid PubMed URLs (https://pubmed.ncbi.nlm.nih.gov/...) or DOI URLs. Return empty array if no valid references.

Remember: Unknown rsID ≠ unknown gene. Provide detailed gene-level information even when the specific rsID lacks documentation.`;

  try {
    onProgress?.('Calling Gemini API...');
    console.log('[DEBUG] Gemini request:', { rsid, annotation, positionalGene, hasGeneData: !!geneData });
    console.log('[DEBUG] Prompt being sent:', prompt);

    const result = await generateObject({
      model: provider('gemini-2.0-flash-exp'),
      schema: GeneInfoSchema,
      prompt,
    });

    console.log('[DEBUG] Full API result metadata:', {
      finishReason: result.finishReason,
      usage: result.usage,
      warnings: result.warnings,
      response: result.response,
    });
    console.log('[DEBUG] Full Gemini response object:', result.object);
    console.log('[DEBUG] Gemini response received:', {
      functionsCount: result.object.function?.length || 0,
      diseasesCount: result.object.diseases?.length || 0,
      snpsCount: result.object.snps?.length || 0,
      literatureCount: result.object.literature?.length || 0,
    });
    onProgress?.('✓ Gemini API response received');

    let literatureList = result.object.literature || [];

    // Filter out invalid literature entries (those without proper URLs)
    const validLiterature = literatureList.filter((lit) => {
      try {
        new URL(lit.url);
        return true;
      } catch {
        console.warn(`Skipping invalid literature URL: ${lit.url}`);
        return false;
      }
    });

    let enhancedLiterature = validLiterature;
    if (enhancedLiterature.length > 0) {
      onProgress?.(`Enhancing ${enhancedLiterature.length} literature references`);
      enhancedLiterature = await enhanceLiteratureWithExtractions(enhancedLiterature, onProgress);
    }

    return {
      annotation,
      positionalGene,
      geneData: geneData || undefined,
      function: result.object.function || [],
      diseases: result.object.diseases || [],
      snps: result.object.snps || [],
      literature: enhancedLiterature.map((lit) => ({
        functionalRelevance: lit.functionalRelevance,
        mutants: lit.mutants,
        url: lit.url,
      })),
    };
  } catch (error) {
    console.error('[ERROR] Gene lookup failed:', error);
    onProgress?.('✗ Gemini API call failed - check console for details');

    if (error instanceof Error) {
      console.error('[ERROR] Error name:', error.name);
      console.error('[ERROR] Error message:', error.message);
      console.error('[ERROR] Error stack:', error.stack);

      if ('cause' in error && error.cause) {
        console.error('[ERROR] Error cause:', error.cause);
      }

      // Log schema validation errors specifically
      if (error.message.includes('schema') || error.message.includes('validation')) {
        console.error('[SCHEMA ERROR] Response did not match expected schema');
        console.error('[SCHEMA ERROR] This could be a Gemini API response format issue');
      }
    }

    throw error;
  }
}
