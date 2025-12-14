# ABOUTME: Utility module for parsing gene symbols from positional gene strings
# ABOUTME: Extracts clean gene symbols (e.g., "CTNND2 (delta catenin-2)" → "CTNND2")

import re


def extract_gene_symbol(positional_gene: str) -> str:
    """
    Extract gene symbol from positional gene string.

    Handles common formats:
    - "CTNND2 (delta catenin-2)" → "CTNND2"
    - "BRCA1" → "BRCA1"
    - "TP53 (tumor protein p53)" → "TP53"
    - "FOXL3" → "FOXL3"
    - "WI2-2373I1.2" → "WI2-2373I1.2"

    Args:
        positional_gene: Gene name with optional description

    Returns:
        Gene symbol (first token before space or parenthesis),
        or empty string if input is invalid

    Examples:
        >>> extract_gene_symbol("CTNND2 (delta catenin-2)")
        'CTNND2'
        >>> extract_gene_symbol("WI2-2373I1.2")
        'WI2-2373I1.2'
        >>> extract_gene_symbol("")
        ''
    """
    if not positional_gene:
        return ""

    positional_gene = positional_gene.strip()

    if not positional_gene:
        return ""

    parts = re.split(r'[\s(]', positional_gene, maxsplit=1)
    if parts and parts[0]:
        return parts[0].strip()

    return ""
