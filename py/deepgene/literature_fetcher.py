# ABOUTME: Module for fetching paper content from scientific literature URLs
# ABOUTME: Supports PubMed, PMC, DOI, and general web scraping

import logging
import re
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def fetch_paper_content(url: str) -> str | None:
    """
    Fetch paper abstract/content from URL.

    Handles:
    - PubMed URLs (https://pubmed.ncbi.nlm.nih.gov/PMID)
    - PMC URLs (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC...)
    - DOI URLs (https://doi.org/...)
    - Direct journal URLs

    Args:
        url: Paper URL to fetch

    Returns:
        Abstract text or None if fetch fails
    """
    try:
        pmid = extract_pmid(url)
        if pmid:
            logger.info(f"Fetching PubMed abstract for PMID:{pmid}")
            return fetch_pubmed_abstract(pmid)

        logger.info(f"Attempting web scrape of {url}")
        return fetch_via_web_scrape(url)

    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def extract_pmid(url: str) -> str | None:
    """
    Extract PMID from various URL formats.

    Examples:
        https://pubmed.ncbi.nlm.nih.gov/26366551/ → 26366551
        https://www.ncbi.nlm.nih.gov/pubmed/26366551 → 26366551
        https://pubmed.ncbi.nlm.nih.gov/26366551 → 26366551
    """
    patterns = [
        r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)',
        r'ncbi\.nlm\.nih\.gov/pubmed/(\d+)',
        r'ncbi\.nlm\.nih\.gov/m/pubmed/(\d+)',
        r'/pubmed/(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def fetch_pubmed_abstract(pmid: str) -> str | None:
    """
    Fetch abstract from PubMed using E-utilities API.

    Args:
        pmid: PubMed ID

    Returns:
        Abstract text or None if not found
    """
    api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        'db': 'pubmed',
        'id': pmid,
        'retmode': 'xml',
        'rettype': 'abstract'
    }

    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        abstract_parts = []
        for abstract_text in root.findall('.//AbstractText'):
            label = abstract_text.get('Label', '')
            text = ''.join(abstract_text.itertext()).strip()

            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)

        if abstract_parts:
            full_abstract = ' '.join(abstract_parts)
            return full_abstract[:2000]

        logger.warning(f"No abstract found for PMID:{pmid}")
        return None

    except requests.Timeout:
        logger.warning(f"Timeout fetching PMID:{pmid}")
        return None
    except requests.RequestException as e:
        logger.warning(f"Request error fetching PMID:{pmid}: {e}")
        return None
    except ET.ParseError as e:
        logger.warning(f"XML parse error for PMID:{pmid}: {e}")
        return None


def fetch_via_web_scrape(url: str) -> str | None:
    """
    Attempt to fetch abstract via web scraping.

    Args:
        url: URL to scrape

    Returns:
        Abstract text or None if not found
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; DeepGene/1.0; Research Tool)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        abstract_selectors = [
            {'class': 'abstract'},
            {'class': 'abstract-content'},
            {'id': 'abstract'},
            {'class': 'section abstract'},
            {'name': 'dc.description'},
        ]

        for selector in abstract_selectors:
            if 'name' in selector:
                meta_tag = soup.find('meta', selector)
                if meta_tag and meta_tag.get('content'):
                    return meta_tag.get('content')[:2000]
            else:
                element = soup.find('div', selector) or soup.find('section', selector) or soup.find('p', selector)
                if element:
                    text = element.get_text(strip=True)
                    if len(text) > 100:
                        return text[:2000]

        paragraphs = soup.find_all('p')
        for p in paragraphs[:5]:
            text = p.get_text(strip=True)
            if len(text) > 100 and ('abstract' in p.get('class', []) or 'abstract' in str(p.parent.get('class', []))):
                return text[:2000]

        logger.warning(f"Could not extract abstract from {url}")
        return None

    except requests.Timeout:
        logger.warning(f"Timeout scraping {url}")
        return None
    except requests.RequestException as e:
        logger.warning(f"Request error scraping {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Scraping error for {url}: {e}")
        return None
