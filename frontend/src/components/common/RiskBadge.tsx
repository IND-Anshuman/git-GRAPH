'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import type { RiskLevel } from '@/types/platform';

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

const RISK_CONFIG = {
  low: {
    textColor: 'var(--color-success)',
    bgColor: 'rgba(34, 197, 94, 0.12)',
    borderColor: 'rgba(34, 197, 94, 0.25)',
    label: 'Low Risk',
  },
  medium: {
    textColor: 'var(--color-warning)',
    bgColor: 'rgba(245, 158, 11, 0.12)',
    borderColor: 'rgba(245, 158, 11, 0.25)',
    label: 'Medium Risk',
  },
  high: {
    textColor: '#F97316', // Orange-500
    bgColor: 'rgba(249, 115, 22, 0.12)',
    borderColor: 'rgba(249, 115, 22, 0.25)',
    label: 'High Risk',
  },
  critical: {
    textColor: 'var(--color-danger)',
    bgColor: 'rgba(239, 68, 68, 0.12)',
    borderColor: 'rgba(239, 68, 68, 0.25)',
    label: 'Critical Risk',
  },
} as const satisfies Record<RiskLevel, { textColor: string; bgColor: string; borderColor: string; label: string }>;

export default function RiskBadge({ level, className }: RiskBadgeProps) {
  const normalizedLevel = (level.toLowerCase() as RiskLevel) || 'low';
  const config = RISK_CONFIG[normalizedLevel] || RISK_CONFIG.low;

  return (
    <span
      role="status"
      aria-label={`Risk level: ${config.label}`}
      className={cn(
        'inline-flex items-center px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded border select-none',
        className
      )}
      style={{
        color: config.textColor,
        backgroundColor: config.bgColor,
        borderColor: config.borderColor,
      }}
    >
      {normalizedLevel}
    </span>
  );
}
export type { RiskBadgeProps };
