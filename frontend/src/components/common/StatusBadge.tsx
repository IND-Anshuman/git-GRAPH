'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import type { HealthStatus } from '@/types/platform';

// ─── Types ──────────────────────────────────────────────────────────────────

interface StatusBadgeProps {
  status: HealthStatus;
  size?: 'sm' | 'md';
  className?: string;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const STATUS_CONFIG = {
  healthy: {
    dotColor: 'var(--color-success)',
    textColor: 'var(--color-success)',
    bgColor: 'var(--color-success-muted)',
    label: 'Healthy',
  },
  warning: {
    dotColor: 'var(--color-warning)',
    textColor: 'var(--color-warning)',
    bgColor: 'var(--color-warning-muted)',
    label: 'Warning',
  },
  critical: {
    dotColor: 'var(--color-danger)',
    textColor: 'var(--color-danger)',
    bgColor: 'var(--color-danger-muted)',
    label: 'Critical',
  },
  unknown: {
    dotColor: 'var(--color-text-tertiary)',
    textColor: 'var(--color-text-secondary)',
    bgColor: 'rgba(90, 100, 128, 0.12)',
    label: 'Unknown',
  },
} as const satisfies Record<HealthStatus, { dotColor: string; textColor: string; bgColor: string; label: string }>;

const SIZE_CLASSES = {
  sm: {
    padding: '2px 7px',
    fontSize: '0.6875rem', // 11px
    dotSize: '6px',
    gap: '5px',
  },
  md: {
    padding: '3px 9px',
    fontSize: '0.75rem', // 12px
    dotSize: '7px',
    gap: '6px',
  },
} as const;

// ─── Component ───────────────────────────────────────────────────────────────

const StatusBadge = React.memo<StatusBadgeProps>(function StatusBadge({
  status,
  size = 'md',
  className,
}) {
  const config = STATUS_CONFIG[status];
  const sizeConfig = SIZE_CLASSES[size];

  return (
    <span
      role="status"
      aria-label={`Status: ${config.label}`}
      className={cn('inline-flex items-center font-medium', className)}
      style={{
        padding: sizeConfig.padding,
        fontSize: sizeConfig.fontSize,
        gap: sizeConfig.gap,
        background: config.bgColor,
        color: config.textColor,
        borderRadius: 'var(--radius-full)',
        border: `1px solid ${config.dotColor}33`,
        lineHeight: 1,
        letterSpacing: '0.01em',
        whiteSpace: 'nowrap',
        userSelect: 'none',
        transition: 'opacity var(--duration-fast) var(--ease-out)',
      }}
    >
      {/* Colored status dot */}
      <span
        aria-hidden="true"
        style={{
          display: 'inline-block',
          width: sizeConfig.dotSize,
          height: sizeConfig.dotSize,
          borderRadius: 'var(--radius-full)',
          backgroundColor: config.dotColor,
          flexShrink: 0,
          // Pulse animation for warning/critical
          ...(status === 'critical' || status === 'warning'
            ? { animation: 'pulse 2s ease-in-out infinite' }
            : {}),
        }}
      />
      {config.label}
    </span>
  );
});

StatusBadge.displayName = 'StatusBadge';

export default StatusBadge;
export type { StatusBadgeProps };
