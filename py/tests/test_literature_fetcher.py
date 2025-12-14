# ABOUTME: Tests for fetching paper content from scientific literature URLs
# ABOUTME: Validates PubMed API integration and web scraping with mocked HTTP calls

import pytest
from unittest.mock import Mock, patch
from deepgene.literature_fetcher import (
    fetch_paper_content,
    extract_pmid,
    fetch_pubmed_abstract,
    fetch_via_web_scrape,
)


class TestExtractPmid:
    """Test PMID extraction from various URL formats."""

    def test_extract_from_standard_pubmed_url(self):
        """Extract PMID from standard PubMed URL."""
        url = "https://pubmed.ncbi.nlm.nih.gov/26366551/"
        assert extract_pmid(url) == "26366551"

    def test_extract_from_short_pubmed_url(self):
        """Extract PMID from short PubMed URL."""
        url = "https://pubmed.ncbi.nlm.nih.gov/26366551"
        assert extract_pmid(url) == "26366551"

    def test_extract_from_legacy_ncbi_url(self):
        """Extract PMID from legacy NCBI URL format."""
        url = "https://www.ncbi.nlm.nih.gov/pubmed/26366551"
        assert extract_pmid(url) == "26366551"

    def test_extract_from_mobile_url(self):
        """Extract PMID from mobile NCBI URL."""
        url = "https://www.ncbi.nlm.nih.gov/m/pubmed/26366551/"
        assert extract_pmid(url) == "26366551"

    def test_no_pmid_in_doi_url(self):
        """Return None for DOI URLs."""
        url = "https://doi.org/10.1038/nature12345"
        assert extract_pmid(url) is None

    def test_no_pmid_in_journal_url(self):
        """Return None for direct journal URLs."""
        url = "https://www.nature.com/articles/nature12345"
        assert extract_pmid(url) is None

    def test_empty_url(self):
        """Return None for empty URL."""
        url = ""
        assert extract_pmid(url) is None


class TestFetchPubmedAbstract:
    """Test fetching abstracts from PubMed E-utilities API."""

    @patch('deepgene.literature_fetcher.requests.get')
    def test_fetch_successful(self, mock_get):
        """Successfully fetch abstract from PubMed."""
        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0"?>
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
        </PubmedArticleSet>'''
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_pubmed_abstract('12345678')

        assert result is not None
        assert 'test abstract' in result
        assert 'gene mutations' in result
        mock_get.assert_called_once()

    @patch('deepgene.literature_fetcher.requests.get')
    def test_fetch_structured_abstract(self, mock_get):
        """Fetch abstract with labeled sections."""
        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <Abstract>
                            <AbstractText Label="BACKGROUND">Background info.</AbstractText>
                            <AbstractText Label="METHODS">Methods used.</AbstractText>
                            <AbstractText Label="RESULTS">Results found.</AbstractText>
                        </Abstract>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>'''
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_pubmed_abstract('12345678')

        assert result is not None
        assert 'BACKGROUND: Background info' in result
        assert 'METHODS: Methods used' in result
        assert 'RESULTS: Results found' in result

    @patch('deepgene.literature_fetcher.requests.get')
    def test_fetch_no_abstract(self, mock_get):
        """Return None when no abstract found."""
        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <Title>Test Article</Title>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>'''
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_pubmed_abstract('12345678')

        assert result is None

    @patch('deepgene.literature_fetcher.requests.get')
    def test_fetch_timeout(self, mock_get):
        """Handle timeout gracefully."""
        import requests
        mock_get.side_effect = requests.Timeout("Connection timeout")

        result = fetch_pubmed_abstract('12345678')

        assert result is None

    @patch('deepgene.literature_fetcher.requests.get')
    def test_fetch_request_error(self, mock_get):
        """Handle request errors gracefully."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        result = fetch_pubmed_abstract('12345678')

        assert result is None

    @patch('deepgene.literature_fetcher.requests.get')
    def test_fetch_truncates_long_abstract(self, mock_get):
        """Truncate abstracts longer than 2000 characters."""
        long_text = "A" * 3000
        mock_response = Mock()
        mock_response.content = f'''<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <Abstract>
                            <AbstractText>{long_text}</AbstractText>
                        </Abstract>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>'''.encode()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_pubmed_abstract('12345678')

        assert result is not None
        assert len(result) == 2000


class TestFetchViaWebScrape:
    """Test web scraping fallback for non-PubMed URLs."""

    @patch('deepgene.literature_fetcher.requests.get')
    def test_scrape_abstract_by_class(self, mock_get):
        """Successfully scrape abstract using class selector."""
        mock_response = Mock()
        mock_response.content = b'''
        <html>
            <body>
                <div class="abstract">
                    This is the abstract content about mutations and genes in a research paper studying genetic variants and their effects on human health and disease.
                </div>
            </body>
        </html>'''
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_via_web_scrape('https://example.com/paper')

        assert result is not None
        assert 'abstract content' in result
        assert 'mutations and genes' in result

    @patch('deepgene.literature_fetcher.requests.get')
    def test_scrape_abstract_by_meta_tag(self, mock_get):
        """Scrape abstract from meta description tag."""
        mock_response = Mock()
        mock_response.content = b'''
        <html>
            <head>
                <meta name="dc.description" content="Meta tag abstract about genetic variants and SNPs.">
            </head>
        </html>'''
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_via_web_scrape('https://example.com/paper')

        assert result is not None
        assert 'genetic variants' in result
        assert 'SNPs' in result

    @patch('deepgene.literature_fetcher.requests.get')
    def test_scrape_no_abstract_found(self, mock_get):
        """Return None when no abstract found."""
        mock_response = Mock()
        mock_response.content = b'''
        <html>
            <body>
                <p>Short text</p>
            </body>
        </html>'''
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_via_web_scrape('https://example.com/paper')

        assert result is None

    @patch('deepgene.literature_fetcher.requests.get')
    def test_scrape_timeout(self, mock_get):
        """Handle timeout gracefully."""
        import requests
        mock_get.side_effect = requests.Timeout("Connection timeout")

        result = fetch_via_web_scrape('https://example.com/paper')

        assert result is None

    @patch('deepgene.literature_fetcher.requests.get')
    def test_scrape_request_error(self, mock_get):
        """Handle request errors gracefully."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        result = fetch_via_web_scrape('https://example.com/paper')

        assert result is None

    @patch('deepgene.literature_fetcher.requests.get')
    def test_scrape_truncates_long_content(self, mock_get):
        """Truncate scraped content longer than 2000 characters."""
        long_text = "B" * 3000
        mock_response = Mock()
        mock_response.content = f'''
        <html>
            <body>
                <div class="abstract">{long_text}</div>
            </body>
        </html>'''.encode()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_via_web_scrape('https://example.com/paper')

        assert result is not None
        assert len(result) == 2000


class TestFetchPaperContent:
    """Test main fetch_paper_content function."""

    @patch('deepgene.literature_fetcher.fetch_pubmed_abstract')
    def test_fetch_pubmed_url(self, mock_fetch_pubmed):
        """Route PubMed URLs to PubMed fetcher."""
        mock_fetch_pubmed.return_value = "PubMed abstract content"

        result = fetch_paper_content('https://pubmed.ncbi.nlm.nih.gov/26366551/')

        assert result == "PubMed abstract content"
        mock_fetch_pubmed.assert_called_once_with('26366551')

    @patch('deepgene.literature_fetcher.fetch_via_web_scrape')
    def test_fetch_non_pubmed_url(self, mock_web_scrape):
        """Route non-PubMed URLs to web scraper."""
        mock_web_scrape.return_value = "Scraped abstract content"

        result = fetch_paper_content('https://nature.com/articles/12345')

        assert result == "Scraped abstract content"
        mock_web_scrape.assert_called_once()

    @patch('deepgene.literature_fetcher.fetch_pubmed_abstract')
    def test_fetch_handles_exception(self, mock_fetch_pubmed):
        """Return None on exception."""
        mock_fetch_pubmed.side_effect = Exception("Unexpected error")

        result = fetch_paper_content('https://pubmed.ncbi.nlm.nih.gov/26366551/')

        assert result is None
