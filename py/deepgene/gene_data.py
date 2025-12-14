# ABOUTME: Module for fetching gene data from MyGene.info API
# ABOUTME: Provides deterministic gene information for use as context in AI queries

import logging
from pydantic import BaseModel
from typing import Literal

logger = logging.getLogger(__name__)


class GeneData(BaseModel):
    """Structured gene data from MyGene.info database"""
    gene_symbol: str
    gene_name: str | None = None
    summary: str | None = None
    go_terms: dict[str, list] | None = None
    pathways: list[str] | None = None
    mim_diseases: list[str] | None = None
    generif: list[str] | None = None
    entrezgene_id: int | None = None
    ensembl_id: str | None = None
    genomic_location: str | None = None
    source: Literal["mygene.info"] = "mygene.info"


MYGENE_FIELDS = (
    'symbol,name,summary,'
    'go.BP,go.MF,go.CC,'
    'pathway.reactome,pathway.wikipathways,pathway.kegg,'
    'MIM,generif,genomic_pos,'
    'entrezgene,ensembl.gene'
)


def fetch_gene_data(gene_symbol: str) -> GeneData | None:
    """
    Fetch gene data from MyGene.info API.

    Args:
        gene_symbol: Gene symbol to query (e.g., "CTNND2", "BRCA1")

    Returns:
        GeneData object if successful, None on error or not found

    Fields requested:
        - symbol, name, summary
        - go (BP, MF, CC)
        - pathway (reactome, wikipathways, kegg)
        - MIM (OMIM disease associations)
        - generif (research summaries)
        - genomic_pos, entrezgene, ensembl.gene
    """
    try:
        import mygene
        mg = mygene.MyGeneInfo()

        query_result = mg.query(
            f'symbol:{gene_symbol}',
            species='human',
            fields='entrezgene',
            size=1
        )

        if not query_result or 'hits' not in query_result or not query_result['hits']:
            logger.warning(f"No data found for gene symbol: {gene_symbol}")
            return None

        gene_id = query_result['hits'][0].get('entrezgene')
        if not gene_id:
            logger.warning(f"No gene ID found for symbol: {gene_symbol}")
            return None

        result = mg.getgene(
            gene_id,
            fields=MYGENE_FIELDS,
            timeout=5
        )

        if not result:
            logger.warning(f"No detailed data found for gene ID: {gene_id}")
            return None

        return parse_mygene_response(result, gene_symbol)

    except TimeoutError:
        logger.warning(f"Timeout fetching data for {gene_symbol}")
        return None
    except Exception as e:
        logger.error(f"Error fetching gene data for {gene_symbol}: {e}")
        return None


def parse_mygene_response(result: dict, gene_symbol: str) -> GeneData:
    """
    Parse MyGene.info API response into GeneData model.

    Args:
        result: Raw response from MyGene.info
        gene_symbol: Original query symbol

    Returns:
        GeneData object with parsed fields
    """
    go_terms = {}
    if 'go' in result:
        go_data = result['go']
        if 'BP' in go_data:
            go_terms['BP'] = [term.get('term', '') for term in go_data['BP'][:10]]
        if 'MF' in go_data:
            go_terms['MF'] = [term.get('term', '') for term in go_data['MF'][:10]]
        if 'CC' in go_data:
            go_terms['CC'] = [term.get('term', '') for term in go_data['CC'][:10]]

    pathways = []
    if 'pathway' in result:
        pathway_data = result['pathway']
        if isinstance(pathway_data, dict):
            for source in ['reactome', 'wikipathways', 'kegg']:
                if source in pathway_data:
                    source_pathways = pathway_data[source]
                    if isinstance(source_pathways, list):
                        for pw in source_pathways:
                            if isinstance(pw, dict) and 'name' in pw:
                                pathways.append(f"{pw['name']} ({source.capitalize()})")
                    elif isinstance(source_pathways, dict) and 'name' in source_pathways:
                        pathways.append(f"{source_pathways['name']} ({source.capitalize()})")

    mim_diseases = []
    if 'MIM' in result:
        mim_data = result['MIM']
        if isinstance(mim_data, list):
            for mim in mim_data[:5]:
                if isinstance(mim, dict):
                    mim_id = mim.get('MIM', '')
                    mim_name = mim.get('name', '')
                    if mim_id or mim_name:
                        mim_diseases.append(f"MIM:{mim_id} - {mim_name}" if mim_id else mim_name)
        elif isinstance(mim_data, dict):
            mim_id = mim_data.get('MIM', '')
            mim_name = mim_data.get('name', '')
            if mim_id or mim_name:
                mim_diseases.append(f"MIM:{mim_id} - {mim_name}" if mim_id else mim_name)

    generif = []
    if 'generif' in result:
        generif_data = result['generif']
        if isinstance(generif_data, list):
            for rif in generif_data[:5]:
                if isinstance(rif, dict):
                    pmid = rif.get('pubmed', '')
                    text = rif.get('text', '')
                    if pmid and text:
                        generif.append(f"PMID:{pmid}: {text[:100]}...")

    ensembl_id = None
    if 'ensembl' in result:
        ensembl_data = result['ensembl']
        if isinstance(ensembl_data, dict):
            ensembl_id = ensembl_data.get('gene')
        elif isinstance(ensembl_data, list) and ensembl_data:
            ensembl_id = ensembl_data[0].get('gene') if isinstance(ensembl_data[0], dict) else None

    genomic_location = None
    if 'genomic_pos' in result:
        gpos = result['genomic_pos']
        if isinstance(gpos, dict):
            chr_num = gpos.get('chr', '')
            start = gpos.get('start', '')
            end = gpos.get('end', '')
            if chr_num and start and end:
                genomic_location = f"chr{chr_num}:{start:,}-{end:,}"
        elif isinstance(gpos, list) and gpos:
            gpos = gpos[0]
            chr_num = gpos.get('chr', '')
            start = gpos.get('start', '')
            end = gpos.get('end', '')
            if chr_num and start and end:
                genomic_location = f"chr{chr_num}:{start:,}-{end:,}"

    return GeneData(
        gene_symbol=result.get('symbol', gene_symbol),
        gene_name=result.get('name'),
        summary=result.get('summary'),
        go_terms=go_terms if go_terms else None,
        pathways=pathways if pathways else None,
        mim_diseases=mim_diseases if mim_diseases else None,
        generif=generif if generif else None,
        entrezgene_id=result.get('entrezgene'),
        ensembl_id=ensembl_id,
        genomic_location=genomic_location,
    )


def format_gene_data_for_llm(gene_data: GeneData) -> str:
    """
    Format GeneData into a structured string for LLM context.

    Args:
        gene_data: Parsed gene data from MyGene.info

    Returns:
        Formatted string with gene information for use as LLM context
    """
    lines = ["GENE DATABASE INFORMATION (MyGene.info):", ""]

    lines.append(f"Gene: {gene_data.gene_symbol}")
    if gene_data.gene_name:
        lines.append(f"Full Name: {gene_data.gene_name}")

    if gene_data.entrezgene_id:
        lines.append(f"NCBI Gene ID: {gene_data.entrezgene_id}")
    if gene_data.ensembl_id:
        lines.append(f"Ensembl ID: {gene_data.ensembl_id}")
    if gene_data.genomic_location:
        lines.append(f"Genomic Location: {gene_data.genomic_location}")

    lines.append("")

    if gene_data.summary:
        lines.append("Summary:")
        lines.append(f"  {gene_data.summary}")
        lines.append("")

    if gene_data.go_terms:
        if 'BP' in gene_data.go_terms and gene_data.go_terms['BP']:
            lines.append("Biological Processes (Gene Ontology):")
            for term in gene_data.go_terms['BP'][:5]:
                lines.append(f"  - {term}")
            lines.append("")

        if 'MF' in gene_data.go_terms and gene_data.go_terms['MF']:
            lines.append("Molecular Functions (Gene Ontology):")
            for term in gene_data.go_terms['MF'][:5]:
                lines.append(f"  - {term}")
            lines.append("")

        if 'CC' in gene_data.go_terms and gene_data.go_terms['CC']:
            lines.append("Cellular Components (Gene Ontology):")
            for term in gene_data.go_terms['CC'][:5]:
                lines.append(f"  - {term}")
            lines.append("")

    if gene_data.pathways:
        lines.append("Known Pathways:")
        for pathway in gene_data.pathways[:8]:
            lines.append(f"  - {pathway}")
        lines.append("")

    if gene_data.mim_diseases:
        lines.append("Disease Associations (OMIM):")
        for disease in gene_data.mim_diseases:
            lines.append(f"  - {disease}")
        lines.append("")

    if gene_data.generif:
        lines.append("Recent Research (GeneRIF):")
        for rif in gene_data.generif[:3]:
            lines.append(f"  - {rif}")
        lines.append("")

    return "\n".join(lines)
