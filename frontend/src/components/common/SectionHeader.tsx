'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  tag?: string;
  action?: React.ReactNode;
  className?: string;
}

export default function SectionHeader({ title, subtitle, tag, action, className }: SectionHeaderProps) {
  return (
    <div className={cn('flex flex-col gap-1.5 shrink-0', className)}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          {tag && (
            <span className="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--color-primary)] bg-[var(--color-primary-muted)] px-2.5 py-0.5 rounded border border-[rgba(79,140,255,0.15)]">
              {tag}
            </span>
          )}
          <h2 className="text-section-title text-gradient-primary">
            {title}
          </h2>
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>
      {subtitle && (
        <p className="text-xs text-[var(--color-text-secondary)] font-medium max-w-2xl">
          {subtitle}
        </p>
      )}
    </div>
  );
}
