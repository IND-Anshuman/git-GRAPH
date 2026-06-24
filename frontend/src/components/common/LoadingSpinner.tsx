'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const SIZE_MAP = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-8 h-8 border-3',
};

export default function LoadingSpinner({
  size = 'md',
  className,
}: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn(
        'rounded-full animate-spin',
        'border-transparent border-t-[var(--color-primary)] border-r-[var(--color-primary)]',
        'border-b-[var(--color-border)] border-l-[var(--color-border)]',
        'motion-reduce:animate-[spin_3s_linear_infinite]', // slow spin for reduced motion
        SIZE_MAP[size],
        className
      )}
    />
  );
}
