// ABOUTME: React component for displaying gene lookup results
// ABOUTME: Shows gene data, functions, diseases, SNPs, and literature

import type { GeneLookupResult } from '../types';

interface ResultDisplayProps {
  result: GeneLookupResult | null;
}

export function ResultDisplay({ result }: ResultDisplayProps) {
  if (!result) {
    return null;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Gene Research Report</h2>

      <div style={styles.section}>
        <strong>Annotation:</strong> {result.annotation}
      </div>

      <div style={styles.section}>
        <strong>Positional Gene:</strong> {result.positionalGene}
      </div>

      {result.geneData && (
        <div style={styles.section}>
          <h3 style={styles.subheading}>Gene Database Information (MyGene.info)</h3>

          {result.geneData.geneName && (
            <div>
              <strong>Gene:</strong> {result.geneData.geneSymbol} - {result.geneData.geneName}
            </div>
          )}

          {result.geneData.summary && (
            <div style={styles.summary}>
              <strong>Summary:</strong> {result.geneData.summary.slice(0, 200)}...
            </div>
          )}

          {result.geneData.pathways && result.geneData.pathways.length > 0 && (
            <div>
              <strong>Pathways:</strong>
              <ul style={styles.list}>
                {result.geneData.pathways.slice(0, 5).map((pathway, idx) => (
                  <li key={idx}>{pathway}</li>
                ))}
              </ul>
            </div>
          )}

          {result.geneData.mimDiseases && result.geneData.mimDiseases.length > 0 && (
            <div>
              <strong>OMIM Diseases:</strong>
              <ul style={styles.list}>
                {result.geneData.mimDiseases.slice(0, 3).map((disease, idx) => (
                  <li key={idx}>{disease}</li>
                ))}
              </ul>
            </div>
          )}

          {result.geneData.genomicLocation && (
            <div>
              <strong>Location:</strong> {result.geneData.genomicLocation}
            </div>
          )}
        </div>
      )}

      <div style={styles.section}>
        <h3 style={styles.subheading}>Function (AI Analysis)</h3>
        {Array.isArray(result.function) && result.function.length > 0 ? (
          <ul style={styles.list}>
            {result.function.map((func, idx) => (
              <li key={idx}>{func}</li>
            ))}
          </ul>
        ) : (
          <div>{String(result.function)}</div>
        )}
      </div>

      <div style={styles.section}>
        <h3 style={styles.subheading}>Associated Diseases (AI Analysis)</h3>
        {Array.isArray(result.diseases) && result.diseases.length > 0 ? (
          <ul style={styles.list}>
            {result.diseases.map((disease, idx) => (
              <li key={idx}>{disease}</li>
            ))}
          </ul>
        ) : (
          <div>{String(result.diseases)}</div>
        )}
      </div>

      <div style={styles.section}>
        <h3 style={styles.subheading}>Associated SNPs (AI Analysis)</h3>
        {Array.isArray(result.snps) && result.snps.length > 0 ? (
          <div>
            {result.snps.map((snpInfo) => (
              <div key={snpInfo.id} style={styles.snpEntry}>
                <strong>{snpInfo.id}</strong>
                {snpInfo.genes && snpInfo.genes.length > 0 && <div>Genes: {snpInfo.genes.join(', ')}</div>}
                {snpInfo.phenotypes && snpInfo.phenotypes.length > 0 && <div>Phenotypes: {snpInfo.phenotypes.join(', ')}</div>}
              </div>
            ))}
          </div>
        ) : (
          <div>None</div>
        )}
      </div>

      <div style={styles.section}>
        <h3 style={styles.subheading}>Literature & References (AI + NER Analysis)</h3>
        {Array.isArray(result.literature) && result.literature.length > 0 ? (
          <div>
            {result.literature.map((lit, idx) => (
              <div key={idx} style={styles.literatureEntry}>
                <div>
                  <strong>[{idx + 1}]</strong> {lit.functionalRelevance}
                </div>
                {lit.mutants && lit.mutants.length > 0 && (
                  <div style={styles.mutants}>
                    Mutants ({lit.mutants.length} found): {lit.mutants.slice(0, 10).join(', ')}
                    {lit.mutants.length > 10 && ` ... and ${lit.mutants.length - 10} more`}
                  </div>
                )}
                <div>
                  <a href={lit.url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                    {lit.url}
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div>None</div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '2rem auto',
    padding: '1.5rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#f9f9f9',
  },
  heading: {
    fontSize: '1.5rem',
    marginBottom: '1rem',
    color: '#333',
  },
  subheading: {
    fontSize: '1.2rem',
    marginTop: '1rem',
    marginBottom: '0.5rem',
    color: '#555',
  },
  section: {
    marginBottom: '1.5rem',
  },
  summary: {
    marginTop: '0.5rem',
    lineHeight: '1.6',
  },
  list: {
    marginTop: '0.5rem',
    paddingLeft: '1.5rem',
  },
  snpEntry: {
    marginBottom: '1rem',
    paddingLeft: '1rem',
  },
  literatureEntry: {
    marginBottom: '1.5rem',
    paddingLeft: '1rem',
  },
  mutants: {
    fontSize: '0.9rem',
    color: '#666',
    marginTop: '0.25rem',
  },
  link: {
    color: '#007bff',
    textDecoration: 'none',
  },
};
