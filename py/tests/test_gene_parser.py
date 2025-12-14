# ABOUTME: Tests for gene symbol extraction from positional gene strings
# ABOUTME: Validates parsing logic for various gene name formats

import pytest
from deepgene.gene_parser import extract_gene_symbol


class TestExtractGeneSymbol:
    """Test gene symbol extraction from various formats."""

    def test_gene_with_description(self):
        """Extract symbol from gene with description in parentheses."""
        result = extract_gene_symbol("CTNND2 (delta catenin-2)")
        assert result == "CTNND2"

    def test_simple_gene_symbol(self):
        """Extract symbol from plain gene name."""
        result = extract_gene_symbol("BRCA1")
        assert result == "BRCA1"

    def test_gene_with_hyphen(self):
        """Preserve hyphens in gene symbols."""
        result = extract_gene_symbol("WI2-2373I1.2")
        assert result == "WI2-2373I1.2"

    def test_gene_with_dot_notation(self):
        """Preserve dot notation in gene symbols."""
        result = extract_gene_symbol("LOC123.4")
        assert result == "LOC123.4"

    def test_gene_with_longer_description(self):
        """Extract symbol from gene with longer description."""
        result = extract_gene_symbol("TP53 (tumor protein p53)")
        assert result == "TP53"

    def test_empty_string(self):
        """Return empty string for empty input."""
        result = extract_gene_symbol("")
        assert result == ""

    def test_whitespace_only(self):
        """Return empty string for whitespace-only input."""
        result = extract_gene_symbol("   ")
        assert result == ""

    def test_leading_whitespace(self):
        """Handle leading whitespace correctly."""
        result = extract_gene_symbol("  FOXL3")
        assert result == "FOXL3"

    def test_trailing_whitespace(self):
        """Handle trailing whitespace correctly."""
        result = extract_gene_symbol("FOXL3  ")
        assert result == "FOXL3"

    def test_gene_with_spaces_in_description(self):
        """Extract symbol when description has multiple spaces."""
        result = extract_gene_symbol("BRCA2 (breast cancer 2, early onset)")
        assert result == "BRCA2"

    def test_gene_with_parenthesis_only(self):
        """Extract symbol when parenthesis appears without space."""
        result = extract_gene_symbol("GENE1(description)")
        assert result == "GENE1"

    def test_numeric_gene_symbol(self):
        """Handle gene symbols with numbers."""
        result = extract_gene_symbol("HLA-DRB1")
        assert result == "HLA-DRB1"

    def test_mixed_case_symbol(self):
        """Preserve case in gene symbols."""
        result = extract_gene_symbol("MiR-21")
        assert result == "MiR-21"
