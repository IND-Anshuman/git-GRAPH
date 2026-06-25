'use client';

import React from 'react';
import { cn } from '@/lib/utils';

type BadgeVariant = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'muted';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const VARIANT_MAP: Record<BadgeVariant, string> = {
  primary: 'bg-[var(--color-primary-muted)] text-[var(--color-primary)] border-[rgba(79,140,255,0.15)]',
  success: 'bg-[var(--color-success-muted)] text-[var(--color-success)] border-[rgba(34,197,94,0.12)]',
  warning: 'bg-[var(--color-warning-muted)] text-[var(--color-warning)] border-[rgba(245,158,11,0.12)]',
  danger: 'bg-[var(--color-danger-muted)] text-[var(--color-danger)] border-[rgba(239,68,68,0.12)]',
  info: 'bg-[var(--color-info-muted)] text-[var(--color-info)] border-[rgba(6,182,212,0.12)]',
  muted: 'bg-white/[0.02] text-[var(--color-text-secondary)] border-white/[0.04]',
};

export default function Badge({ children, variant = 'muted', className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-[var(--radius-xl)] text-[10px] font-semibold uppercase tracking-wider border select-none',
        VARIANT_MAP[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
