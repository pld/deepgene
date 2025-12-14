// ABOUTME: Tests for main App component
// ABOUTME: Validates API key setup flow and integration

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from './App';

describe('App', () => {
  it('should render API key input on first load', () => {
    render(<App />);
    expect(screen.getByText(/Enter Google AI Studio API Key/i)).toBeDefined();
    expect(screen.getByPlaceholderText(/Enter your Gemini API key/i)).toBeDefined();
  });

  it('should render title and subtitle', () => {
    render(<App />);
    expect(screen.getByText(/DeepGene Research Tool/i)).toBeDefined();
    expect(screen.getByText(/AI-powered gene research/i)).toBeDefined();
  });

  it('should show link to Google AI Studio', () => {
    render(<App />);
    const link = screen.getByText(/Google AI Studio/i);
    expect(link).toBeDefined();
    expect(link.closest('a')?.getAttribute('href')).toBe('https://aistudio.google.com/apikey');
  });
});
