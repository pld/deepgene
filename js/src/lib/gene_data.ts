// ABOUTME: Module for fetching gene data from MyGene.info API
// ABOUTME: Provides deterministic gene information for use as context in AI queries

import type { GeneData } from '../types';

const MYGENE_BASE_URL = 'https://mygene.info/v3';
const MYGENE_FIELDS =
  'symbol,name,summary,' +
  'go.BP,go.MF,go.CC,' +
  'pathway.reactome,pathway.wikipathways,pathway.kegg,' +
  'MIM,generif,genomic_pos,' +
  'entrezgene,ensembl.gene';

interface MyGeneQueryResponse {
  hits: Array<{
    entrezgene?: number;
    [key: string]: unknown;
  }>;
}

interface MyGeneDetailResponse {
  symbol?: string;
  name?: string;
  summary?: string;
  entrezgene?: number;
  go?: {
    BP?: Array<{ term: string }>;
    MF?: Array<{ term: string }>;
    CC?: Array<{ term: string }>;
  };
  pathway?: {
    reactome?: Array<{ name: string }> | { name: string };
    wikipathways?: Array<{ name: string }> | { name: string };
    kegg?: Array<{ name: string }> | { name: string };
  };
  MIM?: Array<{ MIM?: string; name?: string }> | { MIM?: string; name?: string };
  generif?: Array<{ pubmed?: number; text?: string }>;
  genomic_pos?:
    | { chr?: string; start?: number; end?: number }
    | Array<{ chr?: string; start?: number; end?: number }>;
  ensembl?: { gene?: string } | Array<{ gene?: string }>;
}

/**
 * Fetch gene data from MyGene.info API.
 *
 * @param geneSymbol - Gene symbol to query (e.g., "CTNND2", "BRCA1")
 * @returns GeneData object if successful, null on error or not found
 */
export async function fetchGeneData(geneSymbol: string): Promise<GeneData | null> {
  try {
    const queryUrl = `${MYGENE_BASE_URL}/query?q=symbol:${encodeURIComponent(
      geneSymbol
    )}&species=human&fields=entrezgene&size=1`;

    const queryResponse = await fetch(queryUrl);
    if (!queryResponse.ok) {
      console.warn(`MyGene.info query failed: ${queryResponse.statusText}`);
      return null;
    }

    const queryData: MyGeneQueryResponse = await queryResponse.json();

    if (!queryData.hits || queryData.hits.length === 0) {
      console.warn(`No data found for gene symbol: ${geneSymbol}`);
      return null;
    }

    const geneId = queryData.hits[0].entrezgene;
    if (!geneId) {
      console.warn(`No gene ID found for symbol: ${geneSymbol}`);
      return null;
    }

    const detailUrl = `${MYGENE_BASE_URL}/gene/${geneId}?fields=${MYGENE_FIELDS}`;
    const detailResponse = await fetch(detailUrl);
    if (!detailResponse.ok) {
      console.warn(`MyGene.info detail fetch failed: ${detailResponse.statusText}`);
      return null;
    }

    const detailData: MyGeneDetailResponse = await detailResponse.json();

    return parseMyGeneResponse(detailData, geneSymbol);
  } catch (error) {
    console.error(`Error fetching gene data for ${geneSymbol}:`, error);
    return null;
  }
}

/**
 * Parse MyGene.info API response into GeneData model.
 */
function parseMyGeneResponse(result: MyGeneDetailResponse, geneSymbol: string): GeneData {
  const goTerms: { BP?: string[]; MF?: string[]; CC?: string[] } = {};

  if (result.go) {
    if (result.go.BP) {
      goTerms.BP = result.go.BP.slice(0, 10).map((term) => term.term);
    }
    if (result.go.MF) {
      goTerms.MF = result.go.MF.slice(0, 10).map((term) => term.term);
    }
    if (result.go.CC) {
      goTerms.CC = result.go.CC.slice(0, 10).map((term) => term.term);
    }
  }

  const pathways: string[] = [];
  if (result.pathway) {
    for (const source of ['reactome', 'wikipathways', 'kegg'] as const) {
      const sourcePathways = result.pathway[source];
      if (sourcePathways) {
        if (Array.isArray(sourcePathways)) {
          for (const pw of sourcePathways) {
            if (pw.name) {
              pathways.push(`${pw.name} (${source.charAt(0).toUpperCase() + source.slice(1)})`);
            }
          }
        } else if (sourcePathways.name) {
          pathways.push(
            `${sourcePathways.name} (${source.charAt(0).toUpperCase() + source.slice(1)})`
          );
        }
      }
    }
  }

  const mimDiseases: string[] = [];
  if (result.MIM) {
    const mimData = Array.isArray(result.MIM) ? result.MIM : [result.MIM];
    for (const mim of mimData.slice(0, 5)) {
      if (mim.MIM || mim.name) {
        mimDiseases.push(mim.MIM && mim.name ? `MIM:${mim.MIM} - ${mim.name}` : mim.name || '');
      }
    }
  }

  const generif: string[] = [];
  if (result.generif && Array.isArray(result.generif)) {
    for (const rif of result.generif.slice(0, 5)) {
      if (rif.pubmed && rif.text) {
        generif.push(`PMID:${rif.pubmed}: ${rif.text.slice(0, 100)}...`);
      }
    }
  }

  let ensemblId: string | undefined;
  if (result.ensembl) {
    if (Array.isArray(result.ensembl) && result.ensembl.length > 0) {
      ensemblId = result.ensembl[0].gene;
    } else if (!Array.isArray(result.ensembl)) {
      ensemblId = result.ensembl.gene;
    }
  }

  let genomicLocation: string | undefined;
  if (result.genomic_pos) {
    const gpos = Array.isArray(result.genomic_pos) ? result.genomic_pos[0] : result.genomic_pos;
    if (gpos.chr && gpos.start && gpos.end) {
      genomicLocation = `chr${gpos.chr}:${gpos.start.toLocaleString()}-${gpos.end.toLocaleString()}`;
    }
  }

  return {
    geneSymbol: result.symbol || geneSymbol,
    geneName: result.name,
    summary: result.summary,
    goTerms: Object.keys(goTerms).length > 0 ? goTerms : undefined,
    pathways: pathways.length > 0 ? pathways : undefined,
    mimDiseases: mimDiseases.length > 0 ? mimDiseases : undefined,
    generif: generif.length > 0 ? generif : undefined,
    entrezgeneId: result.entrezgene,
    ensemblId,
    genomicLocation,
    source: 'mygene.info',
  };
}

/**
 * Format GeneData into a structured string for LLM context.
 */
export function formatGeneDataForLLM(geneData: GeneData): string {
  const lines: string[] = ['GENE DATABASE INFORMATION (MyGene.info):', ''];

  lines.push(`Gene: ${geneData.geneSymbol}`);
  if (geneData.geneName) {
    lines.push(`Full Name: ${geneData.geneName}`);
  }

  if (geneData.entrezgeneId) {
    lines.push(`NCBI Gene ID: ${geneData.entrezgeneId}`);
  }
  if (geneData.ensemblId) {
    lines.push(`Ensembl ID: ${geneData.ensemblId}`);
  }
  if (geneData.genomicLocation) {
    lines.push(`Genomic Location: ${geneData.genomicLocation}`);
  }

  lines.push('');

  if (geneData.summary) {
    lines.push('Summary:');
    lines.push(`  ${geneData.summary}`);
    lines.push('');
  }

  if (geneData.goTerms) {
    if (geneData.goTerms.BP && geneData.goTerms.BP.length > 0) {
      lines.push('Biological Processes (Gene Ontology):');
      for (const term of geneData.goTerms.BP.slice(0, 5)) {
        lines.push(`  - ${term}`);
      }
      lines.push('');
    }

    if (geneData.goTerms.MF && geneData.goTerms.MF.length > 0) {
      lines.push('Molecular Functions (Gene Ontology):');
      for (const term of geneData.goTerms.MF.slice(0, 5)) {
        lines.push(`  - ${term}`);
      }
      lines.push('');
    }

    if (geneData.goTerms.CC && geneData.goTerms.CC.length > 0) {
      lines.push('Cellular Components (Gene Ontology):');
      for (const term of geneData.goTerms.CC.slice(0, 5)) {
        lines.push(`  - ${term}`);
      }
      lines.push('');
    }
  }

  if (geneData.pathways && geneData.pathways.length > 0) {
    lines.push('Known Pathways:');
    for (const pathway of geneData.pathways.slice(0, 8)) {
      lines.push(`  - ${pathway}`);
    }
    lines.push('');
  }

  if (geneData.mimDiseases && geneData.mimDiseases.length > 0) {
    lines.push('Disease Associations (OMIM):');
    for (const disease of geneData.mimDiseases) {
      lines.push(`  - ${disease}`);
    }
    lines.push('');
  }

  if (geneData.generif && geneData.generif.length > 0) {
    lines.push('Recent Research (GeneRIF):');
    for (const rif of geneData.generif.slice(0, 3)) {
      lines.push(`  - ${rif}`);
    }
    lines.push('');
  }

  return lines.join('\n');
}
