'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import SpotlightCard from './SpotlightCard';
import AnimatedCounter from './AnimatedCounter';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    label: string;
  };
  sparklineData?: number[]; // custom data to draw a premium sparkline SVG
  isLoading?: boolean;
  className?: string;
}

export default function MetricCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  sparklineData,
  isLoading = false,
  className,
}: MetricCardProps) {
  // Generate sparkline path if data is provided
  const sparklinePath = React.useMemo(() => {
    if (!sparklineData || sparklineData.length < 2) return '';
    const width = 80;
    const height = 24;
    const padding = 2;
    const min = Math.min(...sparklineData);
    const max = Math.max(...sparklineData);
    const range = max - min === 0 ? 1 : max - min;

    const points = sparklineData.map((val, i) => {
      const x = (i / (sparklineData.length - 1)) * (width - padding * 2) + padding;
      const y = height - ((val - min) / range) * (height - padding * 2) - padding;
      return `${x},${y}`;
    });

    return `M ${points.join(' L ')}`;
  }, [sparklineData]);

  const trendColor = trend
    ? trend.direction === 'up'
      ? 'text-[var(--color-success)]'
      : trend.direction === 'down'
      ? 'text-[var(--color-danger)]'
      : 'text-[var(--color-text-tertiary)]'
    : '';

  return (
    <SpotlightCard
      className={cn('p-5 flex flex-col gap-3 min-h-[120px]', className)}
      glowColor="rgba(0, 240, 255, 0.18)"
      cornerBrackets
    >
      {/* Title & Icon */}
      <div className="flex items-center justify-between gap-2 shrink-0">
        <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-[var(--color-text-tertiary)] font-mono leading-none">
          {isLoading ? (
            <span className="skeleton block h-3 w-20 rounded" />
          ) : (
            title
          )}
        </span>
        {!isLoading && icon && (
          <span className="text-[var(--color-text-tertiary)] flex items-center justify-center shrink-0 w-5 h-5">
            {icon}
          </span>
        )}
      </div>

      {/* Main Metric Value */}
      <div className="flex items-baseline justify-between gap-4 mt-1">
        {isLoading ? (
          <span className="skeleton block h-9 w-24 rounded" />
        ) : (
          <span className="text-3xl font-extrabold tracking-tight text-[var(--color-text-primary)] font-mono tabular-nums leading-none">
            {typeof value === 'number' ? <AnimatedCounter value={value} /> : value}
          </span>
        )}

        {/* Sparkline (if provided) */}
        {!isLoading && sparklinePath && (
          <svg className="w-20 h-6 shrink-0 overflow-visible" aria-hidden="true">
            <path
              d={sparklinePath}
              fill="none"
              stroke="var(--color-primary)"
              strokeWidth={1.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              className="opacity-75"
              style={{
                filter: 'drop-shadow(0 0 2px rgba(79, 140, 255, 0.3))',
              }}
            />
          </svg>
        )}
      </div>

      {/* Subtitle & Trend */}
      <div className="flex items-center justify-between gap-2 mt-auto text-[10px] font-medium leading-none">
        {isLoading ? (
          <span className="skeleton block h-2.5 w-32 rounded" />
        ) : (
          <>
            {subtitle && (
              <span className="text-[var(--color-text-tertiary)] truncate">
                {subtitle}
              </span>
            )}
            {trend && (
              <span className={cn('font-mono shrink-0 flex items-center gap-0.5', trendColor)}>
                {trend.direction === 'up' && '↑'}
                {trend.direction === 'down' && '↓'}
                {trend.label}
              </span>
            )}
          </>
        )}
      </div>
    </SpotlightCard>
  );
}
