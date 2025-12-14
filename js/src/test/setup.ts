// ABOUTME: Test setup file for Vitest
// ABOUTME: Configures test environment and global mocks

import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

afterEach(() => {
  cleanup();
});

global.AbortSignal = {
  timeout: vi.fn((_ms: number) => ({
    aborted: false,
    onabort: null,
    reason: undefined,
    throwIfAborted: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(() => true),
  })),
} as unknown as typeof AbortSignal;
