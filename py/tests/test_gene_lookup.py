# ABOUTME: Tests for gene lookup using DSPy and literature enhancement
# ABOUTME: Validates gene information retrieval and literature mutant extraction

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import HttpUrl
from deepgene.gene_lookup import (
    LiteratureInfo,
    SnpInfo,
    GeneLookup,
    enhance_literature_with_extractions,
    lookup_gene,
)
from deepgene.gene_data import GeneData


class TestLiteratureInfo:
    """Test LiteratureInfo Pydantic model."""

    def test_create_literature_info(self):
        """Create LiteratureInfo with valid data."""
        lit = LiteratureInfo(
            functional_relevance="Study of BRCA1 mutations in breast cancer",
            mutants=["rs116515942", "p.Gly12Asp"],
            url="https://pubmed.ncbi.nlm.nih.gov/12345678/"
        )

        assert lit.functional_relevance == "Study of BRCA1 mutations in breast cancer"
        assert len(lit.mutants) == 2
        assert "rs116515942" in lit.mutants
        assert str(lit.url) == "https://pubmed.ncbi.nlm.nih.gov/12345678/"

    def test_literature_info_url_validation(self):
        """Validate URL field."""
        with pytest.raises(Exception):
            LiteratureInfo(
                functional_relevance="Test",
                mutants=[],
                url="not-a-valid-url"
            )


class TestSnpInfo:
    """Test SnpInfo Pydantic model."""

    def test_create_snp_info(self):
        """Create SnpInfo with valid data."""
        snp = SnpInfo(
            genes=["BRCA1", "BRCA2"],
            phenotypes=["Breast cancer", "Ovarian cancer"]
        )

        assert len(snp.genes) == 2
        assert "BRCA1" in snp.genes
        assert len(snp.phenotypes) == 2
        assert "Breast cancer" in snp.phenotypes


class TestGeneLookup:
    """Test GeneLookup DSPy module."""

    @patch('deepgene.gene_lookup.dspy.ChainOfThought')
    def test_forward_basic(self, mock_cot):
        """Test basic gene lookup."""
        mock_predictor = Mock()
        mock_result = Mock()
        mock_result.function = ["Cell adhesion", "Signal transduction"]
        mock_result.diseases = ["Cancer", "Developmental disorders"]
        mock_result.snps = {}
        mock_result.literature = []
        mock_predictor.return_value = mock_result
        mock_cot.return_value = mock_predictor

        lookup = GeneLookup()
        result = lookup.forward(
            rsid="rs116515942",
            annotation="intronic",
            positional_gene="CTNND2 (delta catenin-2)",
            gene_database_info=""
        )

        assert result.function == ["Cell adhesion", "Signal transduction"]
        assert result.diseases == ["Cancer", "Developmental disorders"]
        mock_predictor.assert_called_once()

    @patch('deepgene.gene_lookup.dspy.ChainOfThought')
    def test_forward_with_database_info(self, mock_cot):
        """Test lookup with database context."""
        mock_predictor = Mock()
        mock_result = Mock()
        mock_result.function = ["Adhesion"]
        mock_result.diseases = ["Cancer"]
        mock_result.snps = {}
        mock_result.literature = []
        mock_predictor.return_value = mock_result
        mock_cot.return_value = mock_predictor

        lookup = GeneLookup()
        database_info = "Gene: BRCA1\nSummary: Tumor suppressor..."

        result = lookup.forward(
            rsid="rs12345",
            annotation="downstream",
            positional_gene="BRCA1",
            gene_database_info=database_info
        )

        assert result is not None
        call_kwargs = mock_predictor.call_args.kwargs
        assert call_kwargs['gene_database_info'] == database_info


class TestEnhanceLiteratureWithExtractions:
    """Test literature enhancement with mutant extraction."""

    @patch('deepgene.mutant_extractor.get_mutant_extractor')
    @patch('deepgene.literature_fetcher.fetch_paper_content')
    def test_enhance_literature_success(self, mock_fetch, mock_get_extractor):
        """Successfully enhance literature with extracted mutants."""
        mock_extractor = Mock()
        mock_extractor.extract_mutants.return_value = ['p.Val600Glu', 'c.1799T>A']
        mock_get_extractor.return_value = mock_extractor

        mock_fetch.return_value = "Abstract text with mutations p.Val600Glu and c.1799T>A"

        lit_list = [
            LiteratureInfo(
                functional_relevance="Study of BRAF mutations",
                mutants=["V600E"],
                url="https://pubmed.ncbi.nlm.nih.gov/12345678/"
            )
        ]

        result = enhance_literature_with_extractions(lit_list)

        assert len(result) == 1
        assert len(result[0].mutants) == 3
        assert 'V600E' in result[0].mutants
        assert 'p.Val600Glu' in result[0].mutants
        assert 'c.1799T>A' in result[0].mutants

    @patch('deepgene.mutant_extractor.get_mutant_extractor')
    @patch('deepgene.literature_fetcher.fetch_paper_content')
    def test_enhance_literature_no_content(self, mock_fetch, mock_get_extractor):
        """Keep AI mutants when paper content unavailable."""
        mock_extractor = Mock()
        mock_get_extractor.return_value = mock_extractor

        mock_fetch.return_value = None

        lit_list = [
            LiteratureInfo(
                functional_relevance="Study",
                mutants=["rs12345"],
                url="https://example.com/paper"
            )
        ]

        result = enhance_literature_with_extractions(lit_list)

        assert len(result) == 1
        assert result[0].mutants == ["rs12345"]
        mock_extractor.extract_mutants.assert_not_called()

    @patch('deepgene.mutant_extractor.get_mutant_extractor')
    @patch('deepgene.literature_fetcher.fetch_paper_content')
    def test_enhance_multiple_papers(self, mock_fetch, mock_get_extractor):
        """Enhance multiple literature references."""
        mock_extractor = Mock()
        mock_extractor.extract_mutants.side_effect = [
            ['p.Gly12Asp'],
            ['rs116515942', 'V600E']
        ]
        mock_get_extractor.return_value = mock_extractor

        mock_fetch.side_effect = [
            "Paper 1 abstract",
            "Paper 2 abstract"
        ]

        lit_list = [
            LiteratureInfo(
                functional_relevance="Paper 1",
                mutants=["AI1"],
                url="https://pubmed.ncbi.nlm.nih.gov/11111111/"
            ),
            LiteratureInfo(
                functional_relevance="Paper 2",
                mutants=["AI2"],
                url="https://pubmed.ncbi.nlm.nih.gov/22222222/"
            )
        ]

        result = enhance_literature_with_extractions(lit_list)

        assert len(result) == 2
        assert 'p.Gly12Asp' in result[0].mutants
        assert 'AI1' in result[0].mutants
        assert 'rs116515942' in result[1].mutants
        assert 'V600E' in result[1].mutants
        assert 'AI2' in result[1].mutants

    @patch('deepgene.mutant_extractor.get_mutant_extractor')
    @patch('deepgene.literature_fetcher.fetch_paper_content')
    def test_enhance_removes_duplicates(self, mock_fetch, mock_get_extractor):
        """Remove duplicate mutants after merging."""
        mock_extractor = Mock()
        mock_extractor.extract_mutants.return_value = ['rs12345', 'V600E']
        mock_get_extractor.return_value = mock_extractor

        mock_fetch.return_value = "Abstract text"

        lit_list = [
            LiteratureInfo(
                functional_relevance="Study",
                mutants=["rs12345"],
                url="https://pubmed.ncbi.nlm.nih.gov/12345678/"
            )
        ]

        result = enhance_literature_with_extractions(lit_list)

        assert len(result) == 1
        mutant_count = result[0].mutants.count('rs12345')
        assert mutant_count == 1


class TestLookupGene:
    """Test main lookup_gene function."""

    @patch('deepgene.gene_lookup.GeneLookup')
    @patch('deepgene.gene_lookup.enhance_literature_with_extractions')
    @patch('deepgene.gene_lookup.format_gene_data_for_llm')
    def test_lookup_gene_with_database(self, mock_format, mock_enhance, mock_lookup_class):
        """Lookup gene with database context."""
        mock_format.return_value = "Formatted gene data"

        mock_lookup_instance = Mock()
        mock_result = Mock()
        mock_result.function = ["Function"]
        mock_result.diseases = ["Disease"]
        mock_result.snps = {}
        mock_result.literature = []
        mock_lookup_instance.return_value = mock_result
        mock_lookup_class.return_value = mock_lookup_instance

        mock_enhance.return_value = []

        gene_data = GeneData(
            gene_symbol="BRCA1",
            gene_name="breast cancer 1"
        )

        result = lookup_gene(
            rsid="rs116515942",
            annotation="intronic",
            positional_gene="BRCA1",
            gene_data=gene_data
        )

        assert result['annotation'] == "intronic"
        assert result['positional_gene'] == "BRCA1"
        assert result['gene_data'] == gene_data
        assert result['function'] == ["Function"]
        mock_format.assert_called_once_with(gene_data)

    @patch('deepgene.gene_lookup.GeneLookup')
    @patch('deepgene.gene_lookup.enhance_literature_with_extractions')
    def test_lookup_gene_without_database(self, mock_enhance, mock_lookup_class):
        """Lookup gene without database context."""
        mock_lookup_instance = Mock()
        mock_result = Mock()
        mock_result.function = ["Function"]
        mock_result.diseases = ["Disease"]
        mock_result.snps = {}
        mock_result.literature = []
        mock_lookup_instance.return_value = mock_result
        mock_lookup_class.return_value = mock_lookup_instance

        mock_enhance.return_value = []

        result = lookup_gene(
            rsid="rs12345",
            annotation="downstream",
            positional_gene="UNKNOWN",
            gene_data=None
        )

        assert result['gene_data'] is None
        call_kwargs = mock_lookup_instance.call_args.kwargs
        assert call_kwargs['gene_database_info'] == ""

    @patch('deepgene.gene_lookup.GeneLookup')
    @patch('deepgene.gene_lookup.enhance_literature_with_extractions')
    def test_lookup_gene_enhances_literature(self, mock_enhance, mock_lookup_class):
        """Enhance literature if returned by AI."""
        mock_lookup_instance = Mock()

        lit_list = [
            LiteratureInfo(
                functional_relevance="Study",
                mutants=["AI"],
                url="https://example.com"
            )
        ]

        enhanced_lit = [
            LiteratureInfo(
                functional_relevance="Study",
                mutants=["AI", "Extracted"],
                url="https://example.com"
            )
        ]

        mock_result = Mock()
        mock_result.function = ["Function"]
        mock_result.diseases = ["Disease"]
        mock_result.snps = {}
        mock_result.literature = lit_list
        mock_lookup_instance.return_value = mock_result
        mock_lookup_class.return_value = mock_lookup_instance

        mock_enhance.return_value = enhanced_lit

        result = lookup_gene(
            rsid="rs12345",
            annotation="intronic",
            positional_gene="GENE1",
            gene_data=None
        )

        assert result['literature'] == enhanced_lit
        mock_enhance.assert_called_once_with(lit_list)

    @patch('deepgene.gene_lookup.GeneLookup')
    @patch('deepgene.gene_lookup.enhance_literature_with_extractions')
    def test_lookup_gene_no_literature(self, mock_enhance, mock_lookup_class):
        """Skip enhancement when no literature returned."""
        mock_lookup_instance = Mock()
        mock_result = Mock()
        mock_result.function = ["Function"]
        mock_result.diseases = ["Disease"]
        mock_result.snps = {}
        mock_result.literature = []
        mock_lookup_instance.return_value = mock_result
        mock_lookup_class.return_value = mock_lookup_instance

        mock_enhance.return_value = []

        result = lookup_gene(
            rsid="rs12345",
            annotation="intronic",
            positional_gene="GENE1",
            gene_data=None
        )

        assert result['literature'] == []
        mock_enhance.assert_not_called()
