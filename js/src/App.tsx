// ABOUTME: Main React application component for DeepGene
// ABOUTME: Manages state and coordinates gene lookup workflow

import { useState } from 'react';
import { LookupForm } from './components/LookupForm';
import { ResultDisplay } from './components/ResultDisplay';
import { lookupGene } from './lib/gene_lookup';
import { fetchGeneData } from './lib/gene_data';
import { extractGeneSymbol } from './lib/gene_parser';
import type { LookupFormData, GeneLookupResult } from './types';

export function App() {
  const [result, setResult] = useState<GeneLookupResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [apiKeySet, setApiKeySet] = useState(false);
  const [statusMessages, setStatusMessages] = useState<string[]>([]);

  const handleApiKeySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (apiKey.trim()) {
      setApiKeySet(true);
      setError(null);
    } else {
      setError('Please enter a valid API key');
    }
  };

  const addStatusMessage = (message: string) => {
    setStatusMessages((prev) => [...prev, message]);
  };

  const handleLookup = async (data: LookupFormData) => {
    setLoading(true);
    setError(null);
    setStatusMessages([]);
    setResult(null);

    try {
      // Test API connectivity
      addStatusMessage('Testing Gemini API connectivity...');
      try {
        const testResponse = await fetch(
          'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'x-goog-api-key': apiKey,
            },
            body: JSON.stringify({
              contents: [{ parts: [{ text: 'test' }] }],
            }),
          }
        );
        if (testResponse.ok) {
          addStatusMessage('✓ Gemini API is reachable');
        } else {
          addStatusMessage(`⚠ API test returned status ${testResponse.status}`);
          console.warn('[API TEST] Response:', await testResponse.text());
        }
      } catch (testErr) {
        addStatusMessage(`⚠ API connectivity test failed: ${testErr instanceof Error ? testErr.message : 'Unknown error'}`);
        console.error('[API TEST] Failed:', testErr);
      }

      const geneSymbol = extractGeneSymbol(data.positionalGene);
      let geneData = null;

      if (geneSymbol) {
        addStatusMessage(`Fetching ${geneSymbol} from MyGene.info...`);
        geneData = await fetchGeneData(geneSymbol);
        if (geneData) {
          addStatusMessage('✓ Database data retrieved');
        } else {
          addStatusMessage('⚠ No database data found, proceeding with AI-only mode');
        }
      }

      addStatusMessage('Analyzing with Gemini AI...');
      const lookupResult = await lookupGene(
        data.rsid,
        data.annotation,
        data.positionalGene,
        geneData,
        apiKey,
        addStatusMessage
      );

      setResult(lookupResult);
      addStatusMessage('✓ Lookup complete');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during lookup');
      console.error('Lookup error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!apiKeySet) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h1 style={styles.title}>DeepGene Research Tool</h1>
          <p style={styles.subtitle}>AI-powered gene research with database integration</p>
        </div>

        <div style={styles.apiKeyContainer}>
          <h2 style={styles.apiKeyHeading}>Enter Google AI Studio API Key</h2>
          <form onSubmit={handleApiKeySubmit} style={styles.apiKeyForm}>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your Gemini API key"
              style={styles.apiKeyInput}
              required
            />
            <button type="submit" style={styles.apiKeyButton}>
              Start
            </button>
          </form>
          {error && <div style={styles.error}>{error}</div>}
          <p style={styles.apiKeyHelp}>
            Get your API key from{' '}
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noopener noreferrer"
              style={styles.link}
            >
              Google AI Studio
            </a>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>DeepGene Research Tool</h1>
        <p style={styles.subtitle}>AI-powered gene research with database integration</p>
      </div>

      <LookupForm onSubmit={handleLookup} loading={loading} />

      {error && (
        <div style={styles.error}>
          <h3 style={{ margin: '0 0 0.5rem 0' }}>Error</h3>
          <div>{error}</div>
          <details style={{ marginTop: '0.5rem' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>Debug Details</summary>
            <pre style={{ marginTop: '0.5rem', fontSize: '0.85rem', overflow: 'auto', maxHeight: '200px' }}>
              {error}
              {'\n\nCheck browser console (F12) for full error stack and schema validation details.'}
            </pre>
          </details>
        </div>
      )}

      {statusMessages.length > 0 && (
        <div style={styles.statusContainer}>
          <h3 style={styles.statusHeading}>Progress</h3>
          <div style={styles.statusList}>
            {statusMessages.map((msg, idx) => (
              <div key={idx} style={styles.statusMessage}>
                {msg}
              </div>
            ))}
          </div>
        </div>
      )}

      <ResultDisplay result={result} />
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    padding: '2rem',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  header: {
    textAlign: 'center' as const,
    marginBottom: '2rem',
  },
  title: {
    fontSize: '2.5rem',
    color: '#333',
    marginBottom: '0.5rem',
  },
  subtitle: {
    fontSize: '1.1rem',
    color: '#666',
  },
  apiKeyContainer: {
    maxWidth: '500px',
    margin: '2rem auto',
    padding: '2rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#f9f9f9',
  },
  apiKeyHeading: {
    fontSize: '1.5rem',
    marginBottom: '1rem',
    textAlign: 'center' as const,
  },
  apiKeyForm: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
  },
  apiKeyInput: {
    padding: '0.75rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '1rem',
  },
  apiKeyButton: {
    padding: '0.75rem',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '1rem',
    fontWeight: 'bold' as const,
    cursor: 'pointer',
  },
  apiKeyHelp: {
    marginTop: '1rem',
    fontSize: '0.9rem',
    textAlign: 'center' as const,
    color: '#666',
  },
  link: {
    color: '#007bff',
    textDecoration: 'none',
  },
  error: {
    maxWidth: '600px',
    margin: '1rem auto',
    padding: '1rem',
    backgroundColor: '#fee',
    border: '1px solid #fcc',
    borderRadius: '4px',
    color: '#c00',
  },
  loading: {
    maxWidth: '600px',
    margin: '1rem auto',
    padding: '1rem',
    textAlign: 'center' as const,
    fontSize: '1.1rem',
    color: '#007bff',
  },
  statusContainer: {
    maxWidth: '700px',
    margin: '1.5rem auto',
    padding: '1.5rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#f9f9f9',
  },
  statusHeading: {
    fontSize: '1.2rem',
    marginBottom: '1rem',
    color: '#333',
  },
  statusList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  statusMessage: {
    padding: '0.5rem',
    fontSize: '0.95rem',
    color: '#555',
    backgroundColor: '#fff',
    border: '1px solid #e0e0e0',
    borderRadius: '4px',
    fontFamily: 'monospace',
  },
};
