// ABOUTME: Tests for MyGene.info API integration and gene data parsing
// ABOUTME: Validates gene data fetching, parsing, and formatting with mocked API calls

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchGeneData, formatGeneDataForLLM } from './gene_data';
import type { GeneData } from '../types';

global.fetch = vi.fn();

describe('fetchGeneData', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should successfully fetch and parse gene data', async () => {
    (fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ hits: [{ entrezgene: 1813 }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          symbol: 'CTNND2',
          name: 'catenin delta 2',
          summary: 'This gene encodes a protein...',
          entrezgene: 1813,
        }),
      });

    const result = await fetchGeneData('CTNND2');

    expect(result).not.toBeNull();
    expect(result?.geneSymbol).toBe('CTNND2');
    expect(result?.geneName).toBe('catenin delta 2');
    expect(result?.source).toBe('mygene.info');
  });

  it('should return null when gene not found', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ hits: [] }),
    });

    const result = await fetchGeneData('NOTEXIST');

    expect(result).toBeNull();
  });

  it('should return null when no entrezgene ID in response', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ hits: [{}] }),
    });

    const result = await fetchGeneData('INVALID');

    expect(result).toBeNull();
  });

  it('should handle fetch errors gracefully', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Network error'));

    const result = await fetchGeneData('CTNND2');

    expect(result).toBeNull();
  });

  it('should parse GO terms correctly', async () => {
    (fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ hits: [{ entrezgene: 7157 }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          symbol: 'TP53',
          name: 'tumor protein p53',
          entrezgene: 7157,
          go: {
            BP: [{ term: 'apoptotic process' }, { term: 'DNA damage response' }],
            MF: [{ term: 'DNA binding' }],
            CC: [{ term: 'nucleus' }],
          },
        }),
      });

    const result = await fetchGeneData('TP53');

    expect(result?.goTerms).toBeDefined();
    expect(result?.goTerms?.BP).toContain('apoptotic process');
    expect(result?.goTerms?.MF).toContain('DNA binding');
    expect(result?.goTerms?.CC).toContain('nucleus');
  });

  it('should parse pathways correctly', async () => {
    (fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ hits: [{ entrezgene: 1956 }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          symbol: 'EGFR',
          entrezgene: 1956,
          pathway: {
            reactome: [{ name: 'EGFR signaling pathway' }],
            kegg: { name: 'PI3K-Akt signaling pathway' },
          },
        }),
      });

    const result = await fetchGeneData('EGFR');

    expect(result?.pathways).toBeDefined();
    expect(result?.pathways?.some((p) => p.includes('EGFR signaling'))).toBe(true);
    expect(result?.pathways?.some((p) => p.includes('PI3K-Akt'))).toBe(true);
  });

  it('should parse OMIM disease associations correctly', async () => {
    (fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ hits: [{ entrezgene: 672 }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          symbol: 'BRCA1',
          entrezgene: 672,
          MIM: [
            { MIM: '113705', name: 'Breast cancer' },
            { MIM: '604370', name: 'Ovarian cancer' },
          ],
        }),
      });

    const result = await fetchGeneData('BRCA1');

    expect(result?.mimDiseases).toBeDefined();
    expect(result?.mimDiseases?.length).toBe(2);
    expect(result?.mimDiseases?.some((d) => d.includes('113705'))).toBe(true);
    expect(result?.mimDiseases?.some((d) => d.includes('Breast cancer'))).toBe(true);
  });

  it('should parse genomic location correctly', async () => {
    (fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ hits: [{ entrezgene: 7157 }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          symbol: 'TP53',
          entrezgene: 7157,
          genomic_pos: {
            chr: '17',
            start: 7661779,
            end: 7687538,
          },
        }),
      });

    const result = await fetchGeneData('TP53');

    expect(result?.genomicLocation).toBeDefined();
    expect(result?.genomicLocation).toContain('chr17');
    expect(result?.genomicLocation).toContain('7,661,779');
    expect(result?.genomicLocation).toContain('7,687,538');
  });

  it('should parse ensembl ID correctly', async () => {
    (fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ hits: [{ entrezgene: 672 }] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          symbol: 'BRCA1',
          entrezgene: 672,
          ensembl: {
            gene: 'ENSG00000012048',
          },
        }),
      });

    const result = await fetchGeneData('BRCA1');

    expect(result?.ensemblId).toBe('ENSG00000012048');
  });
});

describe('formatGeneDataForLLM', () => {
  it('should format basic gene data', () => {
    const geneData: GeneData = {
      geneSymbol: 'BRCA1',
      geneName: 'breast cancer 1',
      summary: 'This gene encodes a tumor suppressor.',
      entrezgeneId: 672,
      source: 'mygene.info',
    };

    const result = formatGeneDataForLLM(geneData);

    expect(result).toContain('GENE DATABASE INFORMATION');
    expect(result).toContain('BRCA1');
    expect(result).toContain('breast cancer 1');
    expect(result).toContain('tumor suppressor');
    expect(result).toContain('672');
  });

  it('should format gene data with pathways', () => {
    const geneData: GeneData = {
      geneSymbol: 'EGFR',
      pathways: ['EGFR signaling (Reactome)', 'PI3K-Akt signaling (KEGG)'],
      source: 'mygene.info',
    };

    const result = formatGeneDataForLLM(geneData);

    expect(result).toContain('Known Pathways:');
    expect(result).toContain('EGFR signaling');
    expect(result).toContain('PI3K-Akt');
  });

  it('should format gene data with disease associations', () => {
    const geneData: GeneData = {
      geneSymbol: 'TP53',
      mimDiseases: ['MIM:191170 - Li-Fraumeni syndrome', 'MIM:151623 - Breast cancer'],
      source: 'mygene.info',
    };

    const result = formatGeneDataForLLM(geneData);

    expect(result).toContain('Disease Associations (OMIM):');
    expect(result).toContain('Li-Fraumeni syndrome');
    expect(result).toContain('191170');
  });

  it('should format gene data with GO terms', () => {
    const geneData: GeneData = {
      geneSymbol: 'TP53',
      goTerms: {
        BP: ['apoptotic process', 'DNA damage response'],
        MF: ['DNA binding'],
        CC: ['nucleus'],
      },
      source: 'mygene.info',
    };

    const result = formatGeneDataForLLM(geneData);

    expect(result).toContain('Biological Processes');
    expect(result).toContain('apoptotic process');
    expect(result).toContain('Molecular Functions');
    expect(result).toContain('DNA binding');
    expect(result).toContain('Cellular Components');
    expect(result).toContain('nucleus');
  });

  it('should format minimal gene data', () => {
    const geneData: GeneData = {
      geneSymbol: 'UNKNOWN',
      source: 'mygene.info',
    };

    const result = formatGeneDataForLLM(geneData);

    expect(result).toContain('GENE DATABASE INFORMATION');
    expect(result).toContain('UNKNOWN');
    expect(result.length).toBeGreaterThan(50);
  });
});
