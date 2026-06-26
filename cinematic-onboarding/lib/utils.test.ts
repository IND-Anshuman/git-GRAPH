import { describe, it, expect } from 'vitest';

describe('Project Setup', () => {
  it('should have working test environment', () => {
    expect(true).toBe(true);
  });

  it('should support TypeScript', () => {
    const value: number = 42;
    expect(value).toBe(42);
  });
});
