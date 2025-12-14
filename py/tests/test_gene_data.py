# ABOUTME: Tests for MyGene.info API integration and gene data parsing
# ABOUTME: Validates gene data fetching, parsing, and formatting with mocked API calls

import pytest
from unittest.mock import Mock, patch
from deepgene.gene_data import (
    fetch_gene_data,
    parse_mygene_response,
    format_gene_data_for_llm,
    GeneData,
)


class TestFetchGeneData:
    """Test fetching gene data from MyGene.info API."""

    @patch('mygene.MyGeneInfo')
    def test_fetch_successful(self, mock_mygene_class):
        """Successfully fetch and parse gene data."""
        mock_mg = Mock()
        mock_mygene_class.return_value = mock_mg

        mock_mg.query.return_value = {
            'hits': [{'entrezgene': 1813}]
        }

        mock_mg.getgene.return_value = {
            'symbol': 'CTNND2',
            'name': 'catenin delta 2',
            'summary': 'This gene encodes a protein...',
            'entrezgene': 1813,
        }

        result = fetch_gene_data('CTNND2')

        assert result is not None
        assert result.gene_symbol == 'CTNND2'
        assert result.gene_name == 'catenin delta 2'
        assert result.source == 'mygene.info'
        mock_mg.query.assert_called_once_with(
            'symbol:CTNND2',
            species='human',
            fields='entrezgene',
            size=1
        )

    @patch('mygene.MyGeneInfo')
    def test_fetch_no_results(self, mock_mygene_class):
        """Return None when gene not found."""
        mock_mg = Mock()
        mock_mygene_class.return_value = mock_mg

        mock_mg.query.return_value = {'hits': []}

        result = fetch_gene_data('NOTEXIST')

        assert result is None

    @patch('mygene.MyGeneInfo')
    def test_fetch_no_gene_id(self, mock_mygene_class):
        """Return None when no entrezgene ID in response."""
        mock_mg = Mock()
        mock_mygene_class.return_value = mock_mg

        mock_mg.query.return_value = {
            'hits': [{}]
        }

        result = fetch_gene_data('INVALID')

        assert result is None

    @patch('mygene.MyGeneInfo')
    def test_fetch_timeout(self, mock_mygene_class):
        """Handle timeout gracefully."""
        mock_mg = Mock()
        mock_mygene_class.return_value = mock_mg

        mock_mg.query.side_effect = TimeoutError("Connection timeout")

        result = fetch_gene_data('CTNND2')

        assert result is None

    @patch('mygene.MyGeneInfo')
    def test_fetch_general_exception(self, mock_mygene_class):
        """Handle general exceptions gracefully."""
        mock_mg = Mock()
        mock_mygene_class.return_value = mock_mg

        mock_mg.query.side_effect = Exception("API error")

        result = fetch_gene_data('CTNND2')

        assert result is None


class TestParseMygeneResponse:
    """Test parsing of MyGene.info API responses."""

    def test_parse_basic_response(self):
        """Parse response with basic gene information."""
        response = {
            'symbol': 'BRCA1',
            'name': 'breast cancer 1',
            'summary': 'This gene encodes a tumor suppressor protein.',
            'entrezgene': 672,
        }

        result = parse_mygene_response(response, 'BRCA1')

        assert result.gene_symbol == 'BRCA1'
        assert result.gene_name == 'breast cancer 1'
        assert result.summary == 'This gene encodes a tumor suppressor protein.'
        assert result.entrezgene_id == 672

    def test_parse_with_go_terms(self):
        """Parse response with Gene Ontology terms."""
        response = {
            'symbol': 'TP53',
            'name': 'tumor protein p53',
            'entrezgene': 7157,
            'go': {
                'BP': [
                    {'term': 'apoptotic process'},
                    {'term': 'DNA damage response'},
                ],
                'MF': [
                    {'term': 'DNA binding'},
                ],
                'CC': [
                    {'term': 'nucleus'},
                ],
            }
        }

        result = parse_mygene_response(response, 'TP53')

        assert result.go_terms is not None
        assert 'BP' in result.go_terms
        assert 'apoptotic process' in result.go_terms['BP']
        assert 'DNA binding' in result.go_terms['MF']
        assert 'nucleus' in result.go_terms['CC']

    def test_parse_with_pathways(self):
        """Parse response with pathway information."""
        response = {
            'symbol': 'EGFR',
            'entrezgene': 1956,
            'pathway': {
                'reactome': [
                    {'name': 'EGFR signaling pathway'},
                ],
                'kegg': {
                    'name': 'PI3K-Akt signaling pathway',
                },
            }
        }

        result = parse_mygene_response(response, 'EGFR')

        assert result.pathways is not None
        assert any('EGFR signaling' in p for p in result.pathways)
        assert any('PI3K-Akt' in p for p in result.pathways)

    def test_parse_with_mim_diseases(self):
        """Parse response with OMIM disease associations."""
        response = {
            'symbol': 'BRCA1',
            'entrezgene': 672,
            'MIM': [
                {'MIM': '113705', 'name': 'Breast cancer'},
                {'MIM': '604370', 'name': 'Ovarian cancer'},
            ]
        }

        result = parse_mygene_response(response, 'BRCA1')

        assert result.mim_diseases is not None
        assert len(result.mim_diseases) == 2
        assert any('113705' in d for d in result.mim_diseases)
        assert any('Breast cancer' in d for d in result.mim_diseases)

    def test_parse_with_genomic_location(self):
        """Parse response with genomic location."""
        response = {
            'symbol': 'TP53',
            'entrezgene': 7157,
            'genomic_pos': {
                'chr': '17',
                'start': 7661779,
                'end': 7687538,
            }
        }

        result = parse_mygene_response(response, 'TP53')

        assert result.genomic_location is not None
        assert 'chr17' in result.genomic_location
        assert '7,661,779' in result.genomic_location
        assert '7,687,538' in result.genomic_location

    def test_parse_with_ensembl_id(self):
        """Parse response with Ensembl gene ID."""
        response = {
            'symbol': 'BRCA1',
            'entrezgene': 672,
            'ensembl': {
                'gene': 'ENSG00000012048',
            }
        }

        result = parse_mygene_response(response, 'BRCA1')

        assert result.ensembl_id == 'ENSG00000012048'

    def test_parse_minimal_response(self):
        """Parse response with minimal fields."""
        response = {
            'symbol': 'UNKNOWN',
            'entrezgene': 999999,
        }

        result = parse_mygene_response(response, 'UNKNOWN')

        assert result.gene_symbol == 'UNKNOWN'
        assert result.entrezgene_id == 999999
        assert result.gene_name is None
        assert result.summary is None


class TestFormatGeneDataForLlm:
    """Test formatting gene data for LLM context."""

    def test_format_basic_data(self):
        """Format basic gene data."""
        gene_data = GeneData(
            gene_symbol='BRCA1',
            gene_name='breast cancer 1',
            summary='This gene encodes a tumor suppressor.',
            entrezgene_id=672,
        )

        result = format_gene_data_for_llm(gene_data)

        assert 'GENE DATABASE INFORMATION' in result
        assert 'BRCA1' in result
        assert 'breast cancer 1' in result
        assert 'tumor suppressor' in result
        assert '672' in result

    def test_format_with_pathways(self):
        """Format gene data with pathways."""
        gene_data = GeneData(
            gene_symbol='EGFR',
            pathways=[
                'EGFR signaling (Reactome)',
                'PI3K-Akt signaling (KEGG)',
            ],
        )

        result = format_gene_data_for_llm(gene_data)

        assert 'Known Pathways:' in result
        assert 'EGFR signaling' in result
        assert 'PI3K-Akt' in result

    def test_format_with_diseases(self):
        """Format gene data with disease associations."""
        gene_data = GeneData(
            gene_symbol='TP53',
            mim_diseases=[
                'MIM:191170 - Li-Fraumeni syndrome',
                'MIM:151623 - Breast cancer',
            ],
        )

        result = format_gene_data_for_llm(gene_data)

        assert 'Disease Associations (OMIM):' in result
        assert 'Li-Fraumeni syndrome' in result
        assert '191170' in result

    def test_format_with_go_terms(self):
        """Format gene data with GO terms."""
        gene_data = GeneData(
            gene_symbol='TP53',
            go_terms={
                'BP': ['apoptotic process', 'DNA damage response'],
                'MF': ['DNA binding'],
                'CC': ['nucleus'],
            },
        )

        result = format_gene_data_for_llm(gene_data)

        assert 'Biological Processes' in result
        assert 'apoptotic process' in result
        assert 'Molecular Functions' in result
        assert 'DNA binding' in result
        assert 'Cellular Components' in result
        assert 'nucleus' in result

    def test_format_minimal_data(self):
        """Format minimal gene data."""
        gene_data = GeneData(
            gene_symbol='UNKNOWN',
        )

        result = format_gene_data_for_llm(gene_data)

        assert 'GENE DATABASE INFORMATION' in result
        assert 'UNKNOWN' in result
        assert len(result) > 50
