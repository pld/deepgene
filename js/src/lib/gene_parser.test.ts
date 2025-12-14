// ABOUTME: Tests for gene symbol extraction from positional gene strings
// ABOUTME: Validates parsing logic for various gene name formats

import { describe, it, expect } from 'vitest';
import { extractGeneSymbol } from './gene_parser';

describe('extractGeneSymbol', () => {
  it('should extract symbol from gene with description in parentheses', () => {
    expect(extractGeneSymbol('CTNND2 (delta catenin-2)')).toBe('CTNND2');
  });

  it('should extract symbol from plain gene name', () => {
    expect(extractGeneSymbol('BRCA1')).toBe('BRCA1');
  });

  it('should preserve hyphens in gene symbols', () => {
    expect(extractGeneSymbol('WI2-2373I1.2')).toBe('WI2-2373I1.2');
  });

  it('should preserve dot notation in gene symbols', () => {
    expect(extractGeneSymbol('LOC123.4')).toBe('LOC123.4');
  });

  it('should extract symbol from gene with longer description', () => {
    expect(extractGeneSymbol('TP53 (tumor protein p53)')).toBe('TP53');
  });

  it('should return empty string for empty input', () => {
    expect(extractGeneSymbol('')).toBe('');
  });

  it('should return empty string for whitespace-only input', () => {
    expect(extractGeneSymbol('   ')).toBe('');
  });

  it('should handle leading whitespace correctly', () => {
    expect(extractGeneSymbol('  FOXL3')).toBe('FOXL3');
  });

  it('should handle trailing whitespace correctly', () => {
    expect(extractGeneSymbol('FOXL3  ')).toBe('FOXL3');
  });

  it('should extract symbol when description has multiple spaces', () => {
    expect(extractGeneSymbol('BRCA2 (breast cancer 2, early onset)')).toBe('BRCA2');
  });

  it('should extract symbol when parenthesis appears without space', () => {
    expect(extractGeneSymbol('GENE1(description)')).toBe('GENE1');
  });

  it('should handle gene symbols with numbers', () => {
    expect(extractGeneSymbol('HLA-DRB1')).toBe('HLA-DRB1');
  });

  it('should preserve case in gene symbols', () => {
    expect(extractGeneSymbol('MiR-21')).toBe('MiR-21');
  });
});
