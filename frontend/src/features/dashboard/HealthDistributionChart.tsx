'use client';

import React from 'react';
import { PieChart as PieIcon, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';
import type { Capability } from '@/types/platform';
import { CHART_COLORS } from '@/lib/constants';
import ErrorBoundary from '@/components/common/ErrorBoundary';

interface HealthDistributionChartProps {
  capabilities: Capability[] | undefined;
  isLoading: boolean;
}

const TYPE_LABELS: Record<string, string> = {
  BUSINESS: 'Business',
  AI: 'AI / ML',
  TECHNICAL: 'Technical Core',
  INFRASTRUCTURE: 'Infrastructure',
  SECURITY: 'Security',
  INTEGRATION: 'Integration',
};

function HealthDistributionInner({ capabilities = [], isLoading }: HealthDistributionChartProps) {
  // Compute chart data
  const chartData = React.useMemo(() => {
    if (!capabilities || capabilities.length === 0) return [];

    const counts: Record<string, number> = {};
    capabilities.forEach((c) => {
      const type = c.capability_type || 'TECHNICAL';
      counts[type] = (counts[type] || 0) + 1;
    });

    return Object.entries(counts).map(([type, count]) => ({
      name: TYPE_LABELS[type] || type,
      value: count,
      rawType: type,
    }));
  }, [capabilities]);

  if (isLoading) {
    return (
      <div className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-5 flex flex-col justify-between h-[300px]">
        {/* Header Skeleton */}
        <div className="flex items-center gap-2 mb-4 border-b border-[var(--color-border)] pb-3">
          <PieIcon className="w-4 h-4 text-sip-text-tertiary" />
          <div className="h-4 w-40 bg-[#161A22] skeleton rounded" />
        </div>
        {/* Chart Skeleton */}
        <div className="flex-1 flex items-center justify-center">
          <div className="w-36 h-36 rounded-full border-8 border-t-[var(--color-primary)] border-r-[#161A22] border-b-[#161A22] border-l-[#161A22] animate-spin" />
        </div>
      </div>
    );
  }

  const showEmpty = chartData.length === 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-5 flex flex-col h-[300px]"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[var(--color-border)] pb-3 shrink-0">
        <div className="flex items-center gap-2">
          <PieIcon className="w-4 h-4 text-[var(--color-primary)]" />
          <h3 className="text-sm font-bold text-sip-text-primary">Capability Distribution</h3>
        </div>
        <span className="text-[10px] font-mono text-sip-text-tertiary uppercase tracking-wider">
          Classification breakdown
        </span>
      </div>

      {/* Chart container */}
      <div className="flex-1 min-h-0 w-full relative">
        {showEmpty ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <PieIcon className="w-8 h-8 text-sip-text-tertiary mb-2" />
            <h4 className="text-xs font-semibold text-sip-text-primary">No Data Available</h4>
            <p className="text-[11px] text-sip-text-secondary max-w-[200px]">
              Distributions will display after capability ingestion is run.
            </p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="45%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={CHART_COLORS[index % CHART_COLORS.length]}
                    stroke="var(--color-bg-surface)"
                    strokeWidth={2}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#161A22',
                  borderColor: 'var(--color-border)',
                  borderRadius: 'var(--radius-lg)',
                }}
                itemStyle={{
                  color: 'var(--color-text-primary)',
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                }}
                labelStyle={{ display: 'none' }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                iconType="circle"
                iconSize={8}
                formatter={(value: string) => (
                  <span className="text-[11px] text-sip-text-secondary font-medium mr-2">
                    {value}
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </motion.div>
  );
}

export default function HealthDistributionChart({
  capabilities,
  isLoading,
}: HealthDistributionChartProps) {
  return (
    <ErrorBoundary>
      <HealthDistributionInner capabilities={capabilities} isLoading={isLoading} />
    </ErrorBoundary>
  );
}
