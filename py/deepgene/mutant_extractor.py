# ABOUTME: Module for extracting mutation mentions from biomedical text
# ABOUTME: Uses DSPy with Gemini to identify genetic variants, SNPs, and mutations

import logging
import dspy

logger = logging.getLogger(__name__)


class MutantExtraction(dspy.Signature):
    """Extract mutation and variant mentions from biomedical text.

    Identify all genetic mutations, variants, and SNPs mentioned in the text.
    Include rs numbers, protein mutations (p. notation), DNA mutations (c. notation),
    and simple mutation names (e.g., V600E).
    """

    text: str = dspy.InputField(desc="Abstract or paper text to analyze for mutations")
    mutants: list[str] = dspy.OutputField(
        desc="List of all mutation identifiers found: rs numbers (rs116515942), "
             "protein mutations (p.Gly12Asp), DNA mutations (c.35G>A), "
             "simple mutations (V600E), gene variants, SNPs"
    )


class MutantExtractor:
    """Extract mutation mentions from biomedical text using DSPy/Gemini."""

    def __init__(self):
        self.extractor = dspy.ChainOfThought(MutantExtraction)

    def extract_mutants(self, text: str) -> list[str]:
        """
        Extract mutation mentions from text.

        Args:
            text: Abstract or paper text to analyze

        Returns:
            List of mutant identifiers like:
            - "rs116515942"
            - "p.Gly12Asp"
            - "c.35G>A"
            - "V600E"
        """
        if not text or len(text) < 10:
            return []

        try:
            text_sample = text[:2000]

            result = self.extractor(text=text_sample)

            if result.mutants and isinstance(result.mutants, list):
                logger.info(f"Extracted {len(result.mutants)} mutants from text")
                return result.mutants

            return []

        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            return []


_extractor_instance = None


def get_mutant_extractor() -> MutantExtractor:
    """Get cached extractor instance (reuses DSPy configuration)."""
    global _extractor_instance
    if _extractor_instance is None:
        logger.info("Initializing mutant extractor")
        _extractor_instance = MutantExtractor()
    return _extractor_instance
