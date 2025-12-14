// ABOUTME: Module for fetching paper content from scientific literature URLs
// ABOUTME: Supports PubMed, PMC, DOI, and general web scraping

/**
 * Extract PMID from various URL formats.
 *
 * Examples:
 *   https://pubmed.ncbi.nlm.nih.gov/26366551/ → 26366551
 *   https://www.ncbi.nlm.nih.gov/pubmed/26366551 → 26366551
 */
export function extractPmid(url: string): string | null {
  const patterns = [
    /pubmed\.ncbi\.nlm\.nih\.gov\/(\d+)/,
    /ncbi\.nlm\.nih\.gov\/pubmed\/(\d+)/,
    /ncbi\.nlm\.nih\.gov\/m\/pubmed\/(\d+)/,
    /\/pubmed\/(\d+)/,
  ];

  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) {
      return match[1];
    }
  }

  return null;
}

/**
 * Fetch abstract from PubMed using E-utilities API.
 */
export async function fetchPubmedAbstract(pmid: string): Promise<string | null> {
  const apiUrl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi';
  const params = new URLSearchParams({
    db: 'pubmed',
    id: pmid,
    retmode: 'xml',
    rettype: 'abstract',
  });

  try {
    const response = await fetch(`${apiUrl}?${params}`, {
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      console.warn(`PubMed fetch failed for PMID:${pmid}: ${response.statusText}`);
      return null;
    }

    const xmlText = await response.text();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, 'text/xml');

    const abstractParts: string[] = [];
    const abstractTexts = xmlDoc.querySelectorAll('AbstractText');

    for (const abstractText of abstractTexts) {
      const label = abstractText.getAttribute('Label') || '';
      const text = abstractText.textContent?.trim() || '';

      if (label) {
        abstractParts.push(`${label}: ${text}`);
      } else {
        abstractParts.push(text);
      }
    }

    if (abstractParts.length > 0) {
      const fullAbstract = abstractParts.join(' ');
      return fullAbstract.slice(0, 2000);
    }

    console.warn(`No abstract found for PMID:${pmid}`);
    return null;
  } catch (error) {
    if (error instanceof Error) {
      console.warn(`Error fetching PMID:${pmid}: ${error.message}`);
    }
    return null;
  }
}

/**
 * Attempt to fetch abstract via web scraping.
 */
export async function fetchViaWebScrape(url: string): Promise<string | null> {
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; DeepGene/1.0; Research Tool)',
      },
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      console.warn(`Web scrape failed for ${url}: ${response.statusText}`);
      return null;
    }

    const html = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    const abstractSelectors = [
      '.abstract',
      '.abstract-content',
      '#abstract',
      '.section.abstract',
      'meta[name="dc.description"]',
    ];

    for (const selector of abstractSelectors) {
      if (selector.startsWith('meta')) {
        const metaTag = doc.querySelector<HTMLMetaElement>(selector);
        if (metaTag && metaTag.content) {
          return metaTag.content.slice(0, 2000);
        }
      } else {
        const element = doc.querySelector(selector);
        if (element) {
          const text = element.textContent?.trim() || '';
          if (text.length > 100) {
            return text.slice(0, 2000);
          }
        }
      }
    }

    const paragraphs = doc.querySelectorAll('p');
    for (let i = 0; i < Math.min(5, paragraphs.length); i++) {
      const p = paragraphs[i];
      const text = p.textContent?.trim() || '';
      const classList = Array.from(p.classList);
      const parentClassList = p.parentElement ? Array.from(p.parentElement.classList) : [];

      if (
        text.length > 100 &&
        (classList.includes('abstract') || parentClassList.includes('abstract'))
      ) {
        return text.slice(0, 2000);
      }
    }

    console.warn(`Could not extract abstract from ${url}`);
    return null;
  } catch (error) {
    if (error instanceof Error) {
      console.warn(`Scraping error for ${url}: ${error.message}`);
    }
    return null;
  }
}

/**
 * Fetch paper abstract/content from URL.
 *
 * Handles:
 * - PubMed URLs (https://pubmed.ncbi.nlm.nih.gov/PMID)
 * - PMC URLs (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC...)
 * - DOI URLs (https://doi.org/...)
 * - Direct journal URLs
 */
export async function fetchPaperContent(url: string): Promise<string | null> {
  try {
    const pmid = extractPmid(url);
    if (pmid) {
      console.log(`Fetching PubMed abstract for PMID:${pmid}`);
      return await fetchPubmedAbstract(pmid);
    }

    console.log(`Attempting web scrape of ${url}`);
    return await fetchViaWebScrape(url);
  } catch (error) {
    if (error instanceof Error) {
      console.warn(`Failed to fetch ${url}: ${error.message}`);
    }
    return null;
  }
}
