// ABOUTME: Tests for fetching paper content from scientific literature URLs
// ABOUTME: Validates PubMed API integration and web scraping with mocked fetch calls

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { extractPmid, fetchPubmedAbstract, fetchPaperContent } from './literature_fetcher';

global.fetch = vi.fn();
global.DOMParser = vi.fn().mockImplementation(() => ({
  parseFromString: vi.fn((_str: string, type: string) => {
    if (type === 'text/xml') {
      return {
        querySelectorAll: vi.fn(() => []),
      };
    }
    return {
      querySelector: vi.fn(() => null),
      querySelectorAll: vi.fn(() => []),
    };
  }),
})) as any;

describe('extractPmid', () => {
  it('should extract PMID from standard PubMed URL', () => {
    expect(extractPmid('https://pubmed.ncbi.nlm.nih.gov/26366551/')).toBe('26366551');
  });

  it('should extract PMID from short PubMed URL', () => {
    expect(extractPmid('https://pubmed.ncbi.nlm.nih.gov/26366551')).toBe('26366551');
  });

  it('should extract PMID from legacy NCBI URL', () => {
    expect(extractPmid('https://www.ncbi.nlm.nih.gov/pubmed/26366551')).toBe('26366551');
  });

  it('should extract PMID from mobile URL', () => {
    expect(extractPmid('https://www.ncbi.nlm.nih.gov/m/pubmed/26366551/')).toBe('26366551');
  });

  it('should return null for DOI URLs', () => {
    expect(extractPmid('https://doi.org/10.1038/nature12345')).toBeNull();
  });

  it('should return null for direct journal URLs', () => {
    expect(extractPmid('https://www.nature.com/articles/nature12345')).toBeNull();
  });

  it('should return null for empty URL', () => {
    expect(extractPmid('')).toBeNull();
  });
});

describe('fetchPubmedAbstract', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should successfully fetch abstract from PubMed', async () => {
    const mockXML = `<?xml version="1.0"?>
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <Article>
            <Abstract>
              <AbstractText>This is a test abstract about gene mutations.</AbstractText>
            </Abstract>
          </Article>
        </MedlineCitation>
      </PubmedArticle>
    </PubmedArticleSet>`;

    const mockDoc = {
      querySelectorAll: vi.fn(() => [
        {
          getAttribute: vi.fn(() => null),
          textContent: 'This is a test abstract about gene mutations.',
        },
      ]),
    };

    global.DOMParser = vi.fn(() => ({
      parseFromString: vi.fn(() => mockDoc),
    })) as unknown as typeof DOMParser;

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      text: async () => mockXML,
    });

    const result = await fetchPubmedAbstract('12345678');

    expect(result).not.toBeNull();
    expect(result).toContain('test abstract');
    expect(result).toContain('gene mutations');
  });

  it('should fetch abstract with labeled sections', async () => {
    const mockDoc = {
      querySelectorAll: vi.fn(() => [
        {
          getAttribute: vi.fn(() => 'BACKGROUND'),
          textContent: 'Background info.',
        },
        {
          getAttribute: vi.fn(() => 'METHODS'),
          textContent: 'Methods used.',
        },
      ]),
    };

    global.DOMParser = vi.fn(() => ({
      parseFromString: vi.fn(() => mockDoc),
    })) as unknown as typeof DOMParser;

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      text: async () => '<xml></xml>',
    });

    const result = await fetchPubmedAbstract('12345678');

    expect(result).not.toBeNull();
    expect(result).toContain('BACKGROUND: Background info');
    expect(result).toContain('METHODS: Methods used');
  });

  it('should return null when fetch fails', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      statusText: 'Not Found',
    });

    const result = await fetchPubmedAbstract('12345678');

    expect(result).toBeNull();
  });

  it('should handle timeout errors', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Timeout'));

    const result = await fetchPubmedAbstract('12345678');

    expect(result).toBeNull();
  });

  it('should truncate long abstracts to 2000 characters', async () => {
    const longText = 'A'.repeat(3000);
    const mockDoc = {
      querySelectorAll: vi.fn(() => [
        {
          getAttribute: vi.fn(() => null),
          textContent: longText,
        },
      ]),
    };

    global.DOMParser = vi.fn(() => ({
      parseFromString: vi.fn(() => mockDoc),
    })) as unknown as typeof DOMParser;

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      text: async () => '<xml></xml>',
    });

    const result = await fetchPubmedAbstract('12345678');

    expect(result).not.toBeNull();
    expect(result?.length).toBe(2000);
  });
});

describe('fetchPaperContent', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should route PubMed URLs to PubMed fetcher', async () => {
    const mockDoc = {
      querySelectorAll: vi.fn(() => [
        {
          getAttribute: vi.fn(() => null),
          textContent: 'PubMed abstract content',
        },
      ]),
    };

    global.DOMParser = vi.fn(() => ({
      parseFromString: vi.fn(() => mockDoc),
    })) as unknown as typeof DOMParser;

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      text: async () => '<xml></xml>',
    });

    const result = await fetchPaperContent('https://pubmed.ncbi.nlm.nih.gov/26366551/');

    expect(result).toBe('PubMed abstract content');
  });

  it('should handle errors gracefully', async () => {
    (fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Unexpected error'));

    const result = await fetchPaperContent('https://pubmed.ncbi.nlm.nih.gov/26366551/');

    expect(result).toBeNull();
  });
});
