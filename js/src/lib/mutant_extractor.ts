// ABOUTME: Module for extracting mutation mentions from biomedical text
// ABOUTME: Uses Vercel AI SDK (model-agnostic) with Gemini to identify genetic variants, SNPs, and mutations

import { generateObject } from 'ai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { z } from 'zod';

let provider: ReturnType<typeof createGoogleGenerativeAI> | null = null;

/**
 * Initialize with API key.
 */
export function initializeAI(key: string): void {
  provider = createGoogleGenerativeAI({ apiKey: key });
}

/**
 * Mutant extraction schema (like DSPy signature).
 */
const MutantExtractionSchema = z.object({
  mutants: z
    .array(z.string())
    .describe(
      'List of all mutation identifiers found: rs numbers (rs116515942), protein mutations (p.Gly12Asp), DNA mutations (c.35G>A), simple mutations (V600E), gene variants, SNPs'
    ),
});

/**
 * Extract mutation mentions from biomedical text.
 *
 * Returns list of mutant identifiers like:
 * - "rs116515942"
 * - "p.Gly12Asp"
 * - "c.35G>A"
 * - "V600E"
 */
export async function extractMutants(text: string): Promise<string[]> {
  if (!text || text.length < 10) {
    return [];
  }

  if (!provider) {
    console.error('Provider not initialized. Call initializeAI() first.');
    return [];
  }

  try {
    const textSample = text.slice(0, 2000);

    const result = await generateObject({
      model: provider('gemini-2.0-flash-exp'),
      schema: MutantExtractionSchema,
      prompt: `Extract all mutation and variant mentions from the following biomedical text.

Identify genetic mutations, variants, and SNPs mentioned in the text.
Include rs numbers (rs116515942), protein mutations (p.Gly12Asp), DNA mutations (c.35G>A), and simple mutation names (V600E).

Text:
${textSample}`,
    });

    const mutants = result.object.mutants;

    if (Array.isArray(mutants) && mutants.length > 0) {
      console.log(`Extracted ${mutants.length} mutants from text`);
      return mutants;
    }

    return [];
  } catch (error) {
    console.error('NER extraction failed:', error);
    return [];
  }
}

let extractorInitialized = false;

/**
 * Get extractor instance (ensures AI is initialized).
 */
export function getExtractor(key: string): { extractMutants: typeof extractMutants } {
  if (!extractorInitialized) {
    console.log('Initializing mutant extractor');
    initializeAI(key);
    extractorInitialized = true;
  }
  return { extractMutants };
}
