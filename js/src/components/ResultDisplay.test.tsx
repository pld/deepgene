// ABOUTME: Tests for ResultDisplay component
// ABOUTME: Validates result rendering and data display

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultDisplay } from './ResultDisplay';
import type { GeneLookupResult, GeneData } from '../types';

describe('ResultDisplay', () => {
  it('should render nothing when result is null', () => {
    const { container } = render(<ResultDisplay result={null} />);
    expect(container.textContent).toBe('');
  });

  it('should render basic result information', () => {
    const result: GeneLookupResult = {
      annotation: 'intronic',
      positionalGene: 'BRCA1',
      function: ['Tumor suppression'],
      diseases: ['Breast cancer'],
      snps: [],
      literature: [],
    };

    render(<ResultDisplay result={result} />);

    expect(screen.getByText(/Gene Research Report/i)).toBeDefined();
    expect(screen.getByText(/intronic/i)).toBeDefined();
    expect(screen.getByText(/BRCA1/i)).toBeDefined();
    expect(screen.getByText(/Tumor suppression/i)).toBeDefined();
    expect(screen.getByText(/Breast cancer/i)).toBeDefined();
  });

  it('should render gene database information when present', () => {
    const geneData: GeneData = {
      geneSymbol: 'TP53',
      geneName: 'tumor protein p53',
      summary: 'This gene encodes a tumor suppressor protein.',
      pathways: ['p53 signaling pathway'],
      genomicLocation: 'chr17:7,661,779-7,687,538',
      source: 'mygene.info',
    };

    const result: GeneLookupResult = {
      annotation: 'intronic',
      positionalGene: 'TP53',
      geneData,
      function: [],
      diseases: [],
      snps: [],
      literature: [],
    };

    render(<ResultDisplay result={result} />);

    expect(screen.getByText(/Gene Database Information/i)).toBeDefined();
    expect(screen.getByText(/TP53/i)).toBeDefined();
    expect(screen.getByText(/tumor protein p53/i)).toBeDefined();
    expect(screen.getByText(/p53 signaling pathway/i)).toBeDefined();
  });

  it('should render SNP information', () => {
    const result: GeneLookupResult = {
      annotation: 'intronic',
      positionalGene: 'GENE1',
      function: [],
      diseases: [],
      snps: [
        {
          id: 'rs12345',
          genes: ['BRCA1', 'BRCA2'],
          phenotypes: ['Breast cancer risk'],
        },
      ],
      literature: [],
    };

    render(<ResultDisplay result={result} />);

    expect(screen.getByText(/rs12345/i)).toBeDefined();
    expect(screen.getByText(/BRCA1, BRCA2/i)).toBeDefined();
    expect(screen.getByText(/Breast cancer risk/i)).toBeDefined();
  });

  it('should render literature with mutants', () => {
    const result: GeneLookupResult = {
      annotation: 'intronic',
      positionalGene: 'BRAF',
      function: [],
      diseases: [],
      snps: [],
      literature: [
        {
          functionalRelevance: 'Study of BRAF mutations in melanoma',
          mutants: ['V600E', 'p.Val600Glu', 'rs123'],
          url: 'https://pubmed.ncbi.nlm.nih.gov/12345678/',
        },
      ],
    };

    render(<ResultDisplay result={result} />);

    expect(screen.getByText(/Study of BRAF mutations/i)).toBeDefined();
    expect(screen.getByText(/3 found/i)).toBeDefined();
    expect(screen.getByText(/V600E, p.Val600Glu, rs123/i)).toBeDefined();
  });

  it('should truncate long mutant lists', () => {
    const mutants = Array.from({ length: 15 }, (_, i) => `rs${i}`);

    const result: GeneLookupResult = {
      annotation: 'intronic',
      positionalGene: 'GENE1',
      function: [],
      diseases: [],
      snps: [],
      literature: [
        {
          functionalRelevance: 'Study',
          mutants,
          url: 'https://example.com',
        },
      ],
    };

    render(<ResultDisplay result={result} />);

    expect(screen.getByText(/15 found/i)).toBeDefined();
    expect(screen.getByText(/and 5 more/i)).toBeDefined();
  });
});
