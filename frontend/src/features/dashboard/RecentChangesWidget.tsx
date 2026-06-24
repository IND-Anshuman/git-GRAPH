'use client';

import React from 'react';
import { Clock, ChevronRight, ShieldAlert } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useUIStore } from '@/stores';
import { formatRelativeDate } from '@/lib/utils';
import type { Capability, RiskLevel } from '@/types/platform';
import RiskBadge from '@/components/common/RiskBadge';
import ErrorBoundary from '@/components/common/ErrorBoundary';

interface RecentChangesWidgetProps {
  capabilities: Capability[] | undefined;
  isLoading: boolean;
}

function RecentChangesInner({ capabilities = [], isLoading }: RecentChangesWidgetProps) {
  const router = useRouter();
  const setSelectedCapabilityId = useUIStore((s) => s.setSelectedCapabilityId);

  // Sort capabilities by created_at descending and get top 10
  const sortedCapabilities = React.useMemo(() => {
    if (!capabilities) return [];
    return [...capabilities]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10);
  }, [capabilities]);

  const handleRowClick = (id: string) => {
    setSelectedCapabilityId(id);
    router.push('/capabilities');
  };

  const getRiskLevel = (score: number): RiskLevel => {
    if (score >= 0.8) return 'critical';
    if (score >= 0.6) return 'high';
    if (score >= 0.3) return 'medium';
    return 'low';
  };

  if (isLoading) {
    return (
      <div className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-5 flex flex-col justify-between h-auto min-h-[300px]">
        {/* Header Skeleton */}
        <div className="flex items-center gap-2 mb-4 border-b border-[var(--color-border)] pb-3">
          <Clock className="w-4 h-4 text-sip-text-tertiary" />
          <div className="h-4 w-28 bg-[#161A22] skeleton rounded" />
        </div>
        {/* Rows Skeletons */}
        <div className="flex-1 flex flex-col gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex justify-between items-center py-1">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-4 h-4 bg-[#161A22] skeleton rounded-full" />
                <div className="flex flex-col gap-1.5 flex-1">
                  <div className="h-3 w-1/2 bg-[#161A22] skeleton rounded" />
                  <div className="h-2 w-1/4 bg-[#161A22] skeleton rounded" />
                </div>
              </div>
              <div className="h-4 w-12 bg-[#161A22] skeleton rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const showEmpty = sortedCapabilities.length === 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.15 }}
      className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-5 flex flex-col h-auto min-h-[300px]"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[var(--color-border)] pb-3 shrink-0">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-[var(--color-primary)]" />
          <h3 className="text-sm font-bold text-sip-text-primary">Recent Changes</h3>
        </div>
        <span className="text-[10px] font-mono text-sip-text-tertiary uppercase tracking-wider">
          Timeline activity
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto max-h-[300px] pr-1">
        {showEmpty ? (
          <div className="flex flex-col items-center justify-center h-[200px] text-center">
            <Clock className="w-8 h-8 text-sip-text-tertiary mb-2" />
            <h4 className="text-xs font-semibold text-sip-text-primary">No Recent Changes</h4>
            <p className="text-[11px] text-sip-text-secondary max-w-[200px]">
              New or updated capabilities will appear here.
            </p>
          </div>
        ) : (
          <ul role="list" className="flex flex-col divide-y divide-[var(--color-border)]/40">
            {sortedCapabilities.map((cap) => {
              const riskLevel = getRiskLevel(cap.risk_score);
              return (
                <li key={cap.id}>
                  <button
                    type="button"
                    onClick={() => handleRowClick(cap.id)}
                    className="w-full flex items-center justify-between py-3 text-left hover:bg-[var(--color-bg-surface-elevated)]/60 px-2 rounded-md transition-colors duration-150 group"
                  >
                    <div className="flex flex-col gap-1 min-w-0 pr-4">
                      <span className="text-xs font-semibold text-sip-text-primary truncate group-hover:text-[var(--color-primary)] transition-colors">
                        {cap.name}
                      </span>
                      <div className="flex items-center gap-2 text-[10px] text-sip-text-secondary">
                        <span className="font-mono text-sip-text-muted px-1.5 py-0.2 bg-[#161A22] rounded border border-[var(--color-border)]/30">
                          {cap.capability_type}
                        </span>
                        <span>•</span>
                        <span>{formatRelativeDate(cap.created_at)}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <RiskBadge level={riskLevel} />
                      <ChevronRight className="w-3.5 h-3.5 text-sip-text-tertiary group-hover:text-sip-text-secondary transition-colors" />
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </motion.div>
  );
}

export default function RecentChangesWidget({ capabilities, isLoading }: RecentChangesWidgetProps) {
  return (
    <ErrorBoundary>
      <RecentChangesInner capabilities={capabilities} isLoading={isLoading} />
    </ErrorBoundary>
  );
}
