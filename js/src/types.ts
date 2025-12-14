// ABOUTME: TypeScript types and interfaces for DeepGene application
// ABOUTME: Defines data structures for genes, literature, SNPs, and lookup results

export interface GeneData {
  geneSymbol: string;
  geneName?: string;
  summary?: string;
  goTerms?: {
    BP?: string[];
    MF?: string[];
    CC?: string[];
  };
  pathways?: string[];
  mimDiseases?: string[];
  generif?: string[];
  entrezgeneId?: number;
  ensemblId?: string;
  genomicLocation?: string;
  source: 'mygene.info';
}

export interface SnpInfo {
  id: string;
  genes: string[];
  phenotypes: string[];
}

export interface LiteratureInfo {
  functionalRelevance: string;
  mutants: string[];
  url: string;
}

export interface GeneLookupResult {
  annotation: string;
  positionalGene: string;
  geneData?: GeneData;
  function: string[];
  diseases: string[];
  snps: SnpInfo[];
  literature: LiteratureInfo[];
}

export interface LookupFormData {
  rsid: string;
  annotation: string;
  positionalGene: string;
}
