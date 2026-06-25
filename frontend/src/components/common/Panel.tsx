'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export default function Panel({ children, className, ...props }: PanelProps) {
  return (
    <div
      className={cn(
        'glass-card rounded-[var(--radius-2xl)] overflow-hidden border border-[var(--color-border)] p-6 bg-opacity-40 backdrop-blur-xl transition-all duration-300',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
