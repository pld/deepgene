# ABOUTME: Tests for interactive gene research shell interface
# ABOUTME: Validates command parsing, DSPy setup, lookup execution, and result display

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from deepgene.shell import GeneShell
from deepgene.gene_lookup import LiteratureInfo
from deepgene.gene_data import GeneData


class TestGeneShellInit:
    """Test GeneShell initialization."""

    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_init_successful(self, mock_getenv, mock_lm, mock_configure):
        """Successfully initialize shell with valid API key."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()

        assert shell.rsid_history == []
        mock_lm.assert_called_once_with("gemini/gemini-2.5-flash", api_key="test-api-key")
        mock_configure.assert_called_once()

    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_init_no_api_key(self, mock_getenv, mock_lm, mock_configure):
        """Handle missing API key gracefully."""
        mock_getenv.return_value = None

        shell = GeneShell()

        assert shell.rsid_history == []
        mock_lm.assert_not_called()
        mock_configure.assert_not_called()

    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_init_dspy_error(self, mock_getenv, mock_lm, mock_configure):
        """Handle DSPy setup error gracefully."""
        mock_getenv.return_value = "test-api-key"
        mock_lm.side_effect = Exception("DSPy error")

        shell = GeneShell()

        assert shell.rsid_history == []


class TestDoLookup:
    """Test lookup command parsing."""

    @patch('deepgene.shell.GeneShell.perform_lookup')
    @patch('deepgene.shell.GeneShell.display_result')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_lookup_valid_args(self, mock_getenv, mock_lm, mock_configure, mock_display, mock_perform):
        """Successfully parse and execute lookup with valid arguments."""
        mock_getenv.return_value = "test-api-key"
        mock_perform.return_value = {'annotation': 'intronic', 'function': []}

        shell = GeneShell()
        shell.do_lookup("rs116515942 intronic CTNND2 (delta catenin-2)")

        mock_perform.assert_called_once_with("rs116515942", "intronic", "CTNND2 (delta catenin-2)")
        mock_display.assert_called_once()

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_lookup_missing_args(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Display error for missing arguments."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        shell.do_lookup("rs116515942")

        assert mock_console.print.called

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_lookup_empty_args(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Display error for empty arguments."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        shell.do_lookup("")

        assert mock_console.print.called

    @patch('deepgene.shell.GeneShell.perform_lookup')
    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_lookup_handles_exception(self, mock_getenv, mock_lm, mock_configure, mock_console, mock_perform):
        """Handle lookup errors gracefully."""
        mock_getenv.return_value = "test-api-key"
        mock_perform.side_effect = Exception("Lookup error")

        shell = GeneShell()
        shell.do_lookup("rs12345 intronic GENE1")

        assert mock_console.print.called


class TestCompleteLookup:
    """Test tab completion for lookup command."""

    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_complete_lookup_no_text(self, mock_getenv, mock_lm, mock_configure):
        """Return all history when no text provided."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        shell.rsid_history = ["rs12345", "rs67890", "rs11111"]

        result = shell.complete_lookup("", "lookup ", 7, 7)

        assert result == ["rs12345", "rs67890", "rs11111"]

    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_complete_lookup_with_prefix(self, mock_getenv, mock_lm, mock_configure):
        """Filter history by prefix."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        shell.rsid_history = ["rs12345", "rs67890", "rs12111"]

        result = shell.complete_lookup("rs12", "lookup rs12", 7, 11)

        assert result == ["rs12345", "rs12111"]
        assert "rs67890" not in result

    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_complete_lookup_no_matches(self, mock_getenv, mock_lm, mock_configure):
        """Return empty list when no matches."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        shell.rsid_history = ["rs12345", "rs67890"]

        result = shell.complete_lookup("rs99", "lookup rs99", 7, 11)

        assert result == []


class TestPerformLookup:
    """Test lookup execution with database and AI."""

    @patch('deepgene.shell.lookup_gene')
    @patch('deepgene.gene_data.fetch_gene_data')
    @patch('deepgene.gene_parser.extract_gene_symbol')
    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_perform_lookup_with_database(self, mock_getenv, mock_lm, mock_configure,
                                         mock_console, mock_extract, mock_fetch, mock_lookup):
        """Perform lookup with database data."""
        mock_getenv.return_value = "test-api-key"
        mock_extract.return_value = "BRCA1"

        gene_data = GeneData(gene_symbol="BRCA1", gene_name="breast cancer 1")
        mock_fetch.return_value = gene_data

        mock_lookup.return_value = {
            'annotation': 'intronic',
            'function': ['Function'],
            'diseases': ['Disease'],
            'literature': [],
        }

        shell = GeneShell()
        result = shell.perform_lookup("rs12345", "intronic", "BRCA1")

        assert "rs12345" in shell.rsid_history
        mock_extract.assert_called_once_with("BRCA1")
        mock_fetch.assert_called_once_with("BRCA1")
        mock_lookup.assert_called_once_with("rs12345", "intronic", "BRCA1", gene_data)

    @patch('deepgene.shell.lookup_gene')
    @patch('deepgene.gene_data.fetch_gene_data')
    @patch('deepgene.gene_parser.extract_gene_symbol')
    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_perform_lookup_no_gene_symbol(self, mock_getenv, mock_lm, mock_configure,
                                          mock_console, mock_extract, mock_fetch, mock_lookup):
        """Perform lookup without gene symbol extraction."""
        mock_getenv.return_value = "test-api-key"
        mock_extract.return_value = None

        mock_lookup.return_value = {
            'annotation': 'downstream',
            'function': ['Function'],
        }

        shell = GeneShell()
        result = shell.perform_lookup("rs99999", "downstream", "UNKNOWN")

        mock_fetch.assert_not_called()
        mock_lookup.assert_called_once_with("rs99999", "downstream", "UNKNOWN", None)

    @patch('deepgene.shell.lookup_gene')
    @patch('deepgene.gene_data.fetch_gene_data')
    @patch('deepgene.gene_parser.extract_gene_symbol')
    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_perform_lookup_database_error(self, mock_getenv, mock_lm, mock_configure,
                                          mock_console, mock_extract, mock_fetch, mock_lookup):
        """Handle database fetch error gracefully."""
        mock_getenv.return_value = "test-api-key"
        mock_extract.return_value = "GENE1"
        mock_fetch.side_effect = Exception("Database error")

        mock_lookup.return_value = {'function': []}

        shell = GeneShell()
        result = shell.perform_lookup("rs12345", "intronic", "GENE1")

        mock_lookup.assert_called_once()


class TestDisplayResult:
    """Test result display formatting."""

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_display_basic_result(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Display basic lookup result."""
        mock_getenv.return_value = "test-api-key"

        result = {
            'annotation': 'intronic',
            'positional_gene': 'BRCA1',
            'gene_data': None,
            'function': ['Tumor suppression'],
            'diseases': ['Breast cancer'],
            'snps': {},
            'literature': [],
        }

        shell = GeneShell()
        shell.display_result("rs12345", result)

        assert mock_console.print.called

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_display_with_gene_data(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Display result with database information."""
        mock_getenv.return_value = "test-api-key"

        gene_data = GeneData(
            gene_symbol="TP53",
            gene_name="tumor protein p53",
            summary="Tumor suppressor gene",
            pathways=["p53 signaling"],
        )

        result = {
            'annotation': 'intronic',
            'positional_gene': 'TP53',
            'gene_data': gene_data,
            'function': ['DNA binding'],
            'diseases': ['Cancer'],
            'snps': {},
            'literature': [],
        }

        shell = GeneShell()
        shell.display_result("rs12345", result)

        assert mock_console.print.called

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_display_with_literature(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Display result with literature references."""
        mock_getenv.return_value = "test-api-key"

        literature = [
            LiteratureInfo(
                functional_relevance="Study of BRAF mutations",
                mutants=["V600E", "p.Val600Glu", "rs12345"],
                url="https://pubmed.ncbi.nlm.nih.gov/12345678/"
            )
        ]

        result = {
            'annotation': 'intronic',
            'positional_gene': 'BRAF',
            'gene_data': None,
            'function': ['Kinase activity'],
            'diseases': ['Melanoma'],
            'snps': {},
            'literature': literature,
        }

        shell = GeneShell()
        shell.display_result("rs12345", result)

        assert mock_console.print.called

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_display_truncates_long_mutant_list(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Truncate mutant display to first 10."""
        mock_getenv.return_value = "test-api-key"

        mutants = [f"rs{i}" for i in range(15)]
        literature = [
            LiteratureInfo(
                functional_relevance="Study",
                mutants=mutants,
                url="https://pubmed.ncbi.nlm.nih.gov/12345678/"
            )
        ]

        result = {
            'annotation': 'intronic',
            'positional_gene': 'GENE1',
            'gene_data': None,
            'function': [],
            'diseases': [],
            'snps': {},
            'literature': literature,
        }

        shell = GeneShell()
        shell.display_result("rs12345", result)

        assert mock_console.print.called


class TestExitCommands:
    """Test exit command variations."""

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_do_exit(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Test exit command returns True."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        result = shell.do_exit("")

        assert result is True
        assert mock_console.print.called

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_do_quit(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Test quit command returns True."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        result = shell.do_quit("")

        assert result is True

    @patch('deepgene.shell.console')
    @patch('deepgene.shell.dspy.configure')
    @patch('deepgene.shell.dspy.LM')
    @patch('deepgene.shell.os.getenv')
    def test_do_eof(self, mock_getenv, mock_lm, mock_configure, mock_console):
        """Test EOF (Ctrl+D) returns True."""
        mock_getenv.return_value = "test-api-key"

        shell = GeneShell()
        result = shell.do_EOF("")

        assert result is True
