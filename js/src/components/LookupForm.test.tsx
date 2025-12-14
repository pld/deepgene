// ABOUTME: Tests for LookupForm component
// ABOUTME: Validates form inputs and submission

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { LookupForm } from './LookupForm';

describe('LookupForm', () => {
  it('should render all form fields', () => {
    const mockSubmit = vi.fn();
    render(<LookupForm onSubmit={mockSubmit} loading={false} />);

    expect(screen.getByLabelText(/rsID/i)).toBeDefined();
    expect(screen.getByLabelText(/Annotation/i)).toBeDefined();
    expect(screen.getByLabelText(/Positional Gene/i)).toBeDefined();
  });

  it('should render submit button', () => {
    const mockSubmit = vi.fn();
    render(<LookupForm onSubmit={mockSubmit} loading={false} />);

    const button = screen.getByRole('button', { name: /Lookup Gene/i });
    expect(button).toBeDefined();
  });

  it('should show loading state on button', () => {
    const mockSubmit = vi.fn();
    render(<LookupForm onSubmit={mockSubmit} loading={true} />);

    const button = screen.getByRole('button', { name: /Looking up/i });
    expect(button).toBeDefined();
    expect(button.hasAttribute('disabled')).toBe(true);
  });

  it('should have intronic as default annotation', () => {
    const mockSubmit = vi.fn();
    render(<LookupForm onSubmit={mockSubmit} loading={false} />);

    const select = screen.getByLabelText(/Annotation/i) as HTMLSelectElement;
    expect(select.value).toBe('intronic');
  });

  it('should call onSubmit with form data', async () => {
    const user = userEvent.setup();
    const mockSubmit = vi.fn();
    render(<LookupForm onSubmit={mockSubmit} loading={false} />);

    const rsidInput = screen.getByLabelText(/rsID/i);
    const geneInput = screen.getByLabelText(/Positional Gene/i);
    const button = screen.getByRole('button', { name: /Lookup Gene/i });

    await user.type(rsidInput, 'rs116515942');
    await user.type(geneInput, 'CTNND2');
    await user.click(button);

    expect(mockSubmit).toHaveBeenCalledWith({
      rsid: 'rs116515942',
      annotation: 'intronic',
      positionalGene: 'CTNND2',
    });
  });
});
