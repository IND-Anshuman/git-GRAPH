'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface TrendInfo {
  direction: 'up' | 'down' | 'neutral';
  label: string;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: TrendInfo;
  isLoading?: boolean;
  className?: string;
}

// ─── Sub-components ──────────────────────────────────────────────────────────

function SkeletonBlock({ width, height, className }: { width?: string; height?: string; className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cn('skeleton block', className)}
      style={{
        width: width ?? '100%',
        height: height ?? '1rem',
        borderRadius: 'var(--radius-md)',
        display: 'block',
      }}
    />
  );
}

const TREND_CONFIG = {
  up: {
    Icon: TrendingUp,
    color: 'var(--color-success)',
    label: 'Trending up',
  },
  down: {
    Icon: TrendingDown,
    color: 'var(--color-danger)',
    label: 'Trending down',
  },
  neutral: {
    Icon: Minus,
    color: 'var(--color-text-tertiary)',
    label: 'No change',
  },
} as const;

// ─── Component ───────────────────────────────────────────────────────────────

const MetricCard = React.memo<MetricCardProps>(function MetricCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  isLoading = false,
  className,
}) {
  return (
    <motion.article
      className={cn('surface-card relative flex flex-col gap-3 p-4 overflow-hidden', className)}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0, 0, 0.58, 1] }}
      whileHover={
        isLoading
          ? undefined
          : {
              y: -2,
              boxShadow: 'var(--shadow-lg)',
              transition: { duration: 0.15, ease: [0, 0, 0.58, 1] },
            }
      }
      aria-busy={isLoading}
      aria-label={isLoading ? 'Loading metric' : `${title}: ${value}`}
    >
      {/* Header row: title + icon */}
      <div className="flex items-start justify-between gap-2">
        <span
          style={{
            fontSize: '0.75rem',
            fontWeight: 500,
            color: 'var(--color-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            lineHeight: 1.3,
          }}
        >
          {isLoading ? <SkeletonBlock width="60%" height="11px" /> : title}
        </span>

        {!isLoading && icon && (
          <span
            aria-hidden="true"
            className="flex-shrink-0 flex items-center justify-center"
            style={{
              width: 32,
              height: 32,
              borderRadius: 'var(--radius-lg)',
              background: 'var(--color-bg-surface-elevated)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-primary)',
            }}
          >
            {icon}
          </span>
        )}
      </div>

      {/* Primary value */}
      <div>
        {isLoading ? (
          <SkeletonBlock width="50%" height="28px" />
        ) : (
          <span
            style={{
              fontSize: '1.625rem',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              lineHeight: 1.1,
              letterSpacing: '-0.025em',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {value}
          </span>
        )}
      </div>

      {/* Footer row: subtitle + trend */}
      <div className="flex items-center justify-between gap-2 mt-auto">
        {isLoading ? (
          <SkeletonBlock width="70%" height="11px" />
        ) : (
          <>
            {subtitle && (
              <span
                style={{
                  fontSize: '0.6875rem',
                  color: 'var(--color-text-tertiary)',
                  lineHeight: 1.4,
                }}
              >
                {subtitle}
              </span>
            )}

            {trend && (
              <TrendIndicator trend={trend} />
            )}
          </>
        )}
      </div>
    </motion.article>
  );
});

MetricCard.displayName = 'MetricCard';

// ─── Trend Indicator ─────────────────────────────────────────────────────────

const TrendIndicator = React.memo<{ trend: TrendInfo }>(function TrendIndicator({ trend }) {
  const config = TREND_CONFIG[trend.direction];
  const { Icon } = config;

  return (
    <span
      className="inline-flex items-center gap-1 flex-shrink-0"
      aria-label={`${config.label}: ${trend.label}`}
      style={{
        fontSize: '0.6875rem',
        fontWeight: 500,
        color: config.color,
        lineHeight: 1,
      }}
    >
      <Icon size={12} aria-hidden="true" />
      {trend.label}
    </span>
  );
});

TrendIndicator.displayName = 'TrendIndicator';

export default MetricCard;
export type { MetricCardProps, TrendInfo };
