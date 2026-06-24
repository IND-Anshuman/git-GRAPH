'use client';

import React from 'react';
import { Boxes, ArrowUpRight, ShieldAlert } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useCapabilities } from '@/hooks/useCapabilities';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorBoundary from '@/components/common/ErrorBoundary';

interface CapabilitySummaryWidgetProps {
  repositoryId: string | null;
}

const TYPE_CONFIG = {
  BUSINESS: { label: 'Business', color: '#4F7CFF' },
  AI: { label: 'AI Intelligence', color: '#8B5CF6' },
  TECHNICAL: { label: 'Technical Core', color: '#10B981' },
  INFRASTRUCTURE: { label: 'Infrastructure', color: '#F97316' },
  SECURITY: { label: 'Security', color: '#EF4444' },
  INTEGRATION: { label: 'Integration', color: '#06B6D4' },
} as const;

function CapabilitySummaryInner({ repositoryId }: CapabilitySummaryWidgetProps) {
  const { data: capabilities = [], isLoading, isError, refetch } = useCapabilities(repositoryId);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[260px] bg-sip-surface border border-[var(--color-border)] rounded-lg p-6">
        <LoadingSpinner size="md" className="mb-2" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Aggregating Capability Inventory...
        </span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-[260px] bg-sip-surface border border-[var(--color-border)] rounded-lg p-6 text-center">
        <ShieldAlert className="w-8 h-8 text-[var(--color-danger)] mb-2" />
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          Inventory Fetch Failed
        </h4>
        <p className="text-xs text-sip-text-secondary mb-4 max-w-[200px]">
          Unable to retrieve capability metadata.
        </p>
        <button
          onClick={() => void refetch()}
          type="button"
          className="px-3 py-1.5 text-xs font-semibold rounded bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary)]/90"
        >
          Retry
        </button>
      </div>
    );
  }

  // Count by capability type
  const counts: Record<string, number> = {
    BUSINESS: 0,
    AI: 0,
    TECHNICAL: 0,
    INFRASTRUCTURE: 0,
    SECURITY: 0,
    INTEGRATION: 0,
  };

  capabilities.forEach((c) => {
    const type = (c.capability_type || '').toUpperCase();
    if (type in counts) {
      counts[type]++;
    } else {
      counts.TECHNICAL++; // Fallback
    }
  });

  const total = capabilities.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.05 }}
      className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-5 flex flex-col justify-between h-[260px]"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[var(--color-border)] pb-3">
        <div className="flex items-center gap-2">
          <Boxes className="w-4 h-4 text-[var(--color-primary)]" />
          <h3 className="text-sm font-bold text-sip-text-primary">Capabilities Inventory</h3>
        </div>
        <Link
          href="/capabilities"
          className="text-xs text-[var(--color-primary)] hover:underline inline-flex items-center gap-0.5"
        >
          Explorer
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Content */}
      <div className="flex items-center gap-6 flex-1 min-w-0">
        {/* Large Total Count */}
        <div className="flex flex-col shrink-0 items-center justify-center border-r border-[var(--color-border)] pr-6 h-full">
          <span className="text-4xl font-extrabold text-sip-text-primary tracking-tight font-mono">
            {total}
          </span>
          <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider mt-1">
            Total Mapped
          </span>
        </div>

        {/* Breakdown bars */}
        <div className="flex-1 flex flex-col gap-2.5 overflow-hidden">
          {Object.entries(counts).map(([typeKey, count]) => {
            const config = TYPE_CONFIG[typeKey as keyof typeof TYPE_CONFIG] || {
              label: typeKey,
              color: '#8B95B0',
            };
            const percentage = total > 0 ? (count / total) * 100 : 0;

            return (
              <div key={typeKey} className="flex flex-col text-xs">
                <div className="flex justify-between items-center mb-1 text-[11px]">
                  <span className="font-semibold text-sip-text-secondary truncate pr-2">
                    {config.label}
                  </span>
                  <span className="font-mono text-sip-text-primary font-bold">{count}</span>
                </div>
                {/* Micro visual bar */}
                <div className="h-1.5 w-full bg-[#161A22] rounded-full overflow-hidden border border-[var(--color-border)]/40">
                  <div
                    className="h-full rounded-full transition-all duration-500 ease-out"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: config.color,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

export default function CapabilitySummaryWidget({ repositoryId }: CapabilitySummaryWidgetProps) {
  return (
    <ErrorBoundary>
      <CapabilitySummaryInner repositoryId={repositoryId} />
    </ErrorBoundary>
  );
}
