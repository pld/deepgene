// ABOUTME: React component for gene lookup input form
// ABOUTME: Collects rsID, annotation, and positional gene from user

import { useState, FormEvent } from 'react';
import type { LookupFormData } from '../types';

interface LookupFormProps {
  onSubmit: (data: LookupFormData) => Promise<void>;
  loading: boolean;
}

export function LookupForm({ onSubmit, loading }: LookupFormProps) {
  const [rsid, setRsid] = useState('');
  const [annotation, setAnnotation] = useState('intronic');
  const [positionalGene, setPositionalGene] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onSubmit({ rsid, annotation, positionalGene });
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <div style={styles.formGroup}>
        <label htmlFor="rsid" style={styles.label}>
          rsID:
        </label>
        <input
          id="rsid"
          type="text"
          value={rsid}
          onChange={(e) => setRsid(e.target.value)}
          placeholder="rs116515942"
          required
          style={styles.input}
          disabled={loading}
        />
      </div>

      <div style={styles.formGroup}>
        <label htmlFor="annotation" style={styles.label}>
          Annotation:
        </label>
        <select
          id="annotation"
          value={annotation}
          onChange={(e) => setAnnotation(e.target.value)}
          style={styles.select}
          disabled={loading}
        >
          <option value="intronic">Intronic</option>
          <option value="downstream">Downstream</option>
          <option value="upstream">Upstream</option>
          <option value="exonic">Exonic</option>
        </select>
      </div>

      <div style={styles.formGroup}>
        <label htmlFor="positional-gene" style={styles.label}>
          Positional Gene:
        </label>
        <input
          id="positional-gene"
          type="text"
          value={positionalGene}
          onChange={(e) => setPositionalGene(e.target.value)}
          placeholder="CTNND2 (delta catenin-2)"
          required
          style={styles.input}
          disabled={loading}
        />
      </div>

      <button type="submit" style={styles.button} disabled={loading}>
        {loading ? 'Looking up...' : 'Lookup Gene'}
      </button>
    </form>
  );
}

const styles = {
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
    maxWidth: '600px',
    margin: '0 auto',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  label: {
    fontWeight: 'bold' as const,
    fontSize: '0.9rem',
  },
  input: {
    padding: '0.5rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '1rem',
  },
  select: {
    padding: '0.5rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '1rem',
  },
  button: {
    padding: '0.75rem',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '1rem',
    fontWeight: 'bold' as const,
    cursor: 'pointer',
  },
};
