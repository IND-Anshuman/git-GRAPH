'use client';

import React from 'react';
import { cn } from '@/lib/utils';

type IndicatorStatus = 'active' | 'warning' | 'critical' | 'inactive';

interface StatusIndicatorProps {
  status?: IndicatorStatus;
  label?: string;
  className?: string;
}

const COLOR_MAP: Record<IndicatorStatus, string> = {
  active: 'bg-[var(--color-success)]',
  warning: 'bg-[var(--color-warning)]',
  critical: 'bg-[var(--color-danger)]',
  inactive: 'bg-[var(--color-text-muted)]',
};

export default function StatusIndicator({ status = 'active', label, className }: StatusIndicatorProps) {
  return (
    <div className={cn('inline-flex items-center gap-2 select-none', className)}>
      <span className="relative flex h-1.5 w-1.5 shrink-0">
        {status !== 'inactive' && (
          <span className={cn(
            'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
            status === 'active' && 'bg-[var(--color-success)]',
            status === 'warning' && 'bg-[var(--color-warning)]',
            status === 'critical' && 'bg-[var(--color-danger)]',
          )} />
        )}
        <span className={cn('relative inline-flex rounded-full h-1.5 w-1.5', COLOR_MAP[status])} />
      </span>
      {label && (
        <span className="text-[9px] uppercase font-bold tracking-[0.16em] text-[var(--color-text-tertiary)] font-mono leading-none">
          {label}
        </span>
      )}
    </div>
  );
}
