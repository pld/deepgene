# ABOUTME: DSPy module for gene lookup using rsID
# ABOUTME: Defines signatures and modules for querying gene information

import logging
import dspy
from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl
from typing import Literal
from deepgene.gene_data import GeneData
from deepgene.gene_data import format_gene_data_for_llm

logger = logging.getLogger(__name__)



class LiteratureInfo(BaseModel):
    functional_relevance: str = Field(description="Functional relevance of the literature")
    mutants: list[str] = Field(description="Mutants associated with the literature")
    url: HttpUrl = Field(description="URL of the literature")

class SnpInfo(BaseModel):
    genes: list[str] = Field(description="Genes associated with the SNP")
    phenotypes: list[str] = Field(description="Phenotypes associated with the SNP")


class GeneInfo(dspy.Signature):
    """Analyze the given gene and rsID (reference SNP identifier).

    CRITICAL INSTRUCTIONS:
    - Even if the specific rsID is unknown or poorly documented, you MUST provide comprehensive information about the gene itself
    - Include the gene's biological functions, associated diseases, and other well-known SNPs on this gene
    - If you don't have information about the specific rsID, focus on the gene and list other documented SNPs
    - ALWAYS provide gene function and disease information if the gene is known
    - Include related SNPs on the same gene with their phenotypes

    RESPONSE REQUIREMENTS:
    1. function: List the gene's biological functions (REQUIRED - never leave empty for known genes)
    2. diseases: List diseases/conditions associated with the gene (provide if known)
    3. snps: List other known SNPs on this gene with their phenotypes (include the queried rsID if documented, plus other major SNPs on the gene)
    4. literature: ONLY include entries with valid PubMed URLs or DOI URLs. Return empty list if no valid references.

    Remember: Unknown rsID ≠ unknown gene. Provide detailed gene-level information even when the specific rsID lacks documentation.
    """

    rsid: str = dspy.InputField(desc="Reference SNP ID (e.g., rs116515942) - may be unknown, if so provide general gene information")
    annotation: Literal["intronic", "downstream"] = dspy.InputField(desc="Genomic annotation (e.g., intronic, downstream)")
    positional_gene: str = dspy.InputField(desc="Gene name and description")
    gene_database_info: str = dspy.InputField(
        desc="Optional factual gene data from MyGene.info database. If provided, use as context to enhance your response. If empty, provide comprehensive information from your knowledge.",
        default=""
    )
    function: list[str] = dspy.OutputField(desc="Biological function of the gene (REQUIRED - provide detailed list even if rsID is unknown)")
    diseases: list[str]  = dspy.OutputField(desc="Associated diseases or conditions (provide comprehensive list if gene is known)")
    snps: dict[str, SnpInfo] = dspy.OutputField(desc="Known SNPs on this gene with their phenotypes - include queried rsID if documented, plus other major SNPs")
    literature: list[LiteratureInfo] = dspy.OutputField(desc="Literature references with valid PubMed/DOI URLs and functional relevance")


class GeneLookup(dspy.Module):
    """Module for looking up gene information by rsID"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(GeneInfo)

    def forward(self, rsid: str, annotation: str, positional_gene: str, gene_database_info: str = ""):
        """Lookup gene information for the given rsID"""
        result = self.predictor(
            rsid=rsid,
            annotation=annotation,
            positional_gene=positional_gene,
            gene_database_info=gene_database_info
        )
        return result


def enhance_literature_with_extractions(literature: list[LiteratureInfo]) -> list[LiteratureInfo]:
    """
    Fetch paper content and extract real mutants.

    For each LiteratureInfo:
    1. Fetch content from URL
    2. Extract mutants using NER via DSPy
    3. Merge with AI-generated mutants
    4. Update the mutants field

    Args:
        literature: List of LiteratureInfo from Gemini

    Returns:
        Enhanced literature with extracted mutants
    """
    from deepgene.literature_fetcher import fetch_paper_content
    from deepgene.mutant_extractor import get_mutant_extractor

    extractor = get_mutant_extractor()

    enhanced = []
    for lit in literature:
        content = fetch_paper_content(str(lit.url))

        if content:
            extracted_mutants = extractor.extract_mutants(content)

            all_mutants = list(set(lit.mutants + extracted_mutants))

            lit.mutants = all_mutants

        enhanced.append(lit)

    return enhanced


def lookup_gene(rsid: str, annotation: str, positional_gene: str, gene_data: GeneData | None = None) -> dict:
    """
    Helper function to lookup gene information.

    Args:
        rsid: Reference SNP ID
        annotation: Genomic annotation (intronic, downstream, etc.)
        positional_gene: Gene name with description
        gene_data: Optional deterministic data from MyGene.info

    Returns:
        Dict with both deterministic data and AI-generated insights
    """
    gene_context = ""
    if gene_data:
        gene_context = format_gene_data_for_llm(gene_data)

    lookup = GeneLookup()
    result = lookup(
        rsid=rsid,
        annotation=annotation,
        positional_gene=positional_gene,
        gene_database_info=gene_context
    )

    enhanced_literature = result.literature
    if enhanced_literature:
        logger.info(f"Enhancing {len(enhanced_literature)} literature references")
        enhanced_literature = enhance_literature_with_extractions(enhanced_literature)

    return {
        "annotation": annotation,
        "positional_gene": positional_gene,
        "gene_data": gene_data,
        "function": result.function,
        "diseases": result.diseases,
        "snps": result.snps,
        "literature": enhanced_literature,
    }
