// ABOUTME: Tests for gene lookup module
// ABOUTME: Validates schema compatibility with Gemini API

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { initializeGeneLookup, lookupGene } from './gene_lookup';
import type { GeneData } from '../types';

global.fetch = vi.fn();

describe('gene_lookup', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should handle schema validation errors from Gemini API', async () => {
    initializeGeneLookup('test-key');

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({
        error: {
          message: 'GenerateContentRequest.generation_config.response_schema.properties["snps"].properties: should be non-empty for OBJECT type',
        },
      }),
    });

    await expect(
      lookupGene('rs123', 'intronic', 'BRCA1', null, 'test-key')
    ).rejects.toThrow();
  });

  it('should successfully process valid gene lookup', async () => {
    initializeGeneLookup('test-key');

    const mockResponse = {
      function: ['Tumor suppression'],
      diseases: ['Breast cancer'],
      snps: [],
      literature: [],
    };

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        candidates: [
          {
            content: {
              parts: [{ text: JSON.stringify(mockResponse) }],
            },
          },
        ],
      }),
    });

    const result = await lookupGene('rs123', 'intronic', 'BRCA1', null, 'test-key');

    expect(result).toBeDefined();
    expect(result.annotation).toBe('intronic');
    expect(result.positionalGene).toBe('BRCA1');
  });

  it('should include gene data in result when provided', async () => {
    initializeGeneLookup('test-key');

    const geneData: GeneData = {
      geneSymbol: 'BRCA1',
      geneName: 'breast cancer 1',
      summary: 'Test summary',
      source: 'mygene.info',
    };

    const mockResponse = {
      function: ['Tumor suppression'],
      diseases: ['Breast cancer'],
      snps: [],
      literature: [],
    };

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        candidates: [
          {
            content: {
              parts: [{ text: JSON.stringify(mockResponse) }],
            },
          },
        ],
      }),
    });

    const result = await lookupGene('rs123', 'intronic', 'BRCA1', geneData, 'test-key');

    expect(result.geneData).toEqual(geneData);
  });
});
