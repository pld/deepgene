# ABOUTME: Tests for mutation extraction from biomedical text using DSPy
# ABOUTME: Validates NER extraction logic with mocked DSPy calls

import pytest
from unittest.mock import Mock, patch
from deepgene.mutant_extractor import MutantExtractor, get_mutant_extractor


class TestMutantExtractor:
    """Test mutation extraction from biomedical text."""

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_mutations_success(self, mock_cot):
        """Successfully extract mutations from text."""
        mock_extractor = Mock()
        mock_result = Mock()
        mock_result.mutants = ['rs116515942', 'p.Gly12Asp', 'V600E']
        mock_extractor.return_value = mock_result
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()
        text = "Study found mutations rs116515942, p.Gly12Asp, and V600E in patients."

        result = extractor.extract_mutants(text)

        assert len(result) == 3
        assert 'rs116515942' in result
        assert 'p.Gly12Asp' in result
        assert 'V600E' in result
        mock_extractor.assert_called_once()

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_from_long_text(self, mock_cot):
        """Truncate long text to 2000 characters before extraction."""
        mock_extractor = Mock()
        mock_result = Mock()
        mock_result.mutants = ['rs12345']
        mock_extractor.return_value = mock_result
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()
        long_text = "A" * 5000 + " rs12345"

        result = extractor.extract_mutants(long_text)

        assert len(result) == 1
        call_args = mock_extractor.call_args
        assert len(call_args.kwargs['text']) == 2000

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_empty_text(self, mock_cot):
        """Return empty list for empty text."""
        mock_extractor = Mock()
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()

        result = extractor.extract_mutants("")

        assert result == []
        mock_extractor.assert_not_called()

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_short_text(self, mock_cot):
        """Return empty list for text shorter than 10 characters."""
        mock_extractor = Mock()
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()

        result = extractor.extract_mutants("short")

        assert result == []
        mock_extractor.assert_not_called()

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_no_mutations_found(self, mock_cot):
        """Return empty list when no mutations found."""
        mock_extractor = Mock()
        mock_result = Mock()
        mock_result.mutants = []
        mock_extractor.return_value = mock_result
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()
        text = "This is a paper about general biology without specific mutations mentioned."

        result = extractor.extract_mutants(text)

        assert result == []

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_none_mutations(self, mock_cot):
        """Return empty list when DSPy returns None for mutants."""
        mock_extractor = Mock()
        mock_result = Mock()
        mock_result.mutants = None
        mock_extractor.return_value = mock_result
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()
        text = "Some text about genetics."

        result = extractor.extract_mutants(text)

        assert result == []

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_handles_exception(self, mock_cot):
        """Return empty list on extraction error."""
        mock_extractor = Mock()
        mock_extractor.side_effect = Exception("DSPy error")
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()
        text = "Text with mutation rs12345."

        result = extractor.extract_mutants(text)

        assert result == []

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_extract_various_mutation_formats(self, mock_cot):
        """Extract different mutation notation formats."""
        mock_extractor = Mock()
        mock_result = Mock()
        mock_result.mutants = [
            'rs116515942',
            'p.Gly12Asp',
            'c.35G>A',
            'V600E',
            'p.Arg175His',
        ]
        mock_extractor.return_value = mock_result
        mock_cot.return_value = mock_extractor

        extractor = MutantExtractor()
        text = "Multiple mutation formats: rs116515942, p.Gly12Asp, c.35G>A, V600E, p.Arg175His."

        result = extractor.extract_mutants(text)

        assert len(result) == 5
        assert 'rs116515942' in result
        assert 'c.35G>A' in result
        assert 'p.Arg175His' in result


class TestGetMutantExtractor:
    """Test singleton extractor instance management."""

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_get_extractor_creates_instance(self, mock_cot):
        """Create extractor instance on first call."""
        import deepgene.mutant_extractor
        deepgene.mutant_extractor._extractor_instance = None

        mock_extractor = Mock()
        mock_cot.return_value = mock_extractor

        extractor = get_mutant_extractor()

        assert extractor is not None
        assert isinstance(extractor, MutantExtractor)

    @patch('deepgene.mutant_extractor.dspy.ChainOfThought')
    def test_get_extractor_reuses_instance(self, mock_cot):
        """Reuse cached extractor instance."""
        import deepgene.mutant_extractor

        mock_extractor = Mock()
        mock_cot.return_value = mock_extractor

        extractor1 = get_mutant_extractor()
        extractor2 = get_mutant_extractor()

        assert extractor1 is extractor2

        deepgene.mutant_extractor._extractor_instance = None
