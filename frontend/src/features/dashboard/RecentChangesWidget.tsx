'use client';

import React from 'react';
import { Clock, ChevronRight, AlertTriangle, ShieldCheck, GitCommit, User } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useUIStore } from '@/stores';
import { formatRelativeDate } from '@/lib/utils';
import type { Capability, RiskLevel } from '@/types/platform';
import ErrorBoundary from '@/components/common/ErrorBoundary';
import SpotlightCard from '@/components/common/SpotlightCard';
import Badge from '@/components/common/Badge';

interface RecentChangesWidgetProps {
  capabilities: Capability[] | undefined;
  isLoading: boolean;
}

function RecentChangesInner({ capabilities = [], isLoading }: RecentChangesWidgetProps) {
  const router = useRouter();
  const setSelectedCapabilityId = useUIStore((s) => s.setSelectedCapabilityId);

  // Sort capabilities by created_at descending and get top 5
  const sortedCapabilities = React.useMemo(() => {
    if (!capabilities) return [];
    return [...capabilities]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);
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

  const showEmpty = sortedCapabilities.length === 0;

  if (isLoading) {
    return (
      <div className="glass-card p-5 flex flex-col justify-between h-[320px]">
        {/* Header Skeleton */}
        <div className="flex items-center gap-2 mb-4 border-b border-[var(--color-border)] pb-3 shrink-0">
          <Clock className="w-4 h-4 text-sip-text-tertiary" />
          <div className="h-4 w-28 bg-[#161A22] skeleton rounded" />
        </div>
        {/* Rows Skeletons */}
        <div className="flex-1 flex flex-col gap-3 overflow-hidden">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex justify-between items-center py-2">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-5 h-5 bg-[#161A22] skeleton rounded-full" />
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

  return (
    <SpotlightCard
      className="p-5 flex flex-col h-[320px]"
      glowColor="rgba(57, 255, 20, 0.15)"
      cornerBrackets
    >
      {/* Header */}
      <div
        className="flex items-center justify-between pb-3 shrink-0"
        style={{ borderBottom: '1px solid rgba(0,240,255,0.1)' }}
      >
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-[var(--color-text-tertiary)] font-mono leading-none">
            System Intelligence Timeline
          </span>
        </div>
        <span className="text-[9px] uppercase font-bold tracking-widest text-[var(--color-text-tertiary)] font-mono">
          Change Activity
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto mt-4 pr-1 scrollbar-thin relative">
        {showEmpty ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-6">
            <Clock className="w-8 h-8 text-sip-text-tertiary mb-2" />
            <h4 className="text-xs font-semibold text-sip-text-primary">No Activity Snapshots</h4>
            <p className="text-[11px] text-sip-text-secondary max-w-[200px]">
              New code modifications or intelligence releases will stream here.
            </p>
          </div>
        ) : (
          <div className="relative pl-6 border-l ml-3 flex flex-col gap-6" style={{ borderColor: 'rgba(0,240,255,0.12)' }}>
            {sortedCapabilities.map((cap) => {
              const riskLevel = getRiskLevel(cap.risk_score);
              const badgeVariant =
                riskLevel === 'critical'
                  ? 'danger'
                  : riskLevel === 'high'
                  ? 'warning'
                  : riskLevel === 'medium'
                  ? 'primary'
                  : 'success';

              // Map static mock details for a rich timeline stream layout
              const mockAuthor = 'SHREESHANTH99';
              const mockSha = 'cfe1921';

              return (
                <div key={cap.id} className="relative group select-none">
                  {/* Timeline Indicator Dot */}
                  <span
                    className="absolute -left-[30px] top-1 flex h-4 w-4 items-center justify-center rounded-full"
                    style={{
                      background: 'rgba(0,240,255,0.08)',
                      border: '1px solid rgba(0,240,255,0.25)',
                    }}
                  >
                    <span
                      className="h-1.5 w-1.5 rounded-full animate-pulse"
                      style={{ background: 'var(--neon-blue)', boxShadow: '0 0 6px var(--neon-blue)' }}
                    />
                  </span>

                  {/* Timeline Card Row */}
                  <button
                    type="button"
                    onClick={() => handleRowClick(cap.id)}
                    className="w-full flex items-start justify-between gap-4 p-3 rounded-xl text-left transition-all duration-150"
                    style={{
                      background: 'rgba(0,240,255,0.02)',
                      border: '1px solid rgba(0,240,255,0.08)',
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background = 'rgba(0,240,255,0.05)';
                      (e.currentTarget as HTMLElement).style.borderColor = 'rgba(0,240,255,0.18)';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = 'rgba(0,240,255,0.02)';
                      (e.currentTarget as HTMLElement).style.borderColor = 'rgba(0,240,255,0.08)';
                    }}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-bold text-[var(--color-text-primary)] group-hover:text-[var(--color-primary)] transition-colors truncate">
                          {cap.name}
                        </span>
                        <Badge variant={badgeVariant} className="text-[9px] px-1.5 py-0.2 shrink-0">
                          {riskLevel} risk
                        </Badge>
                      </div>

                      {/* Sub-text activity description */}
                      <p className="text-[11px] text-[var(--color-text-secondary)] mt-1.5 line-clamp-1 leading-snug">
                        {cap.description || 'Live code domain successfully mapped to semantic architecture models.'}
                      </p>

                      {/* Author / SHA / Time footer */}
                      <div className="flex items-center gap-3 text-[9px] font-mono text-[var(--color-text-tertiary)] mt-2">
                        <span className="flex items-center gap-1 shrink-0">
                          <User size={10} />
                          {mockAuthor}
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1 shrink-0">
                          <GitCommit size={10} />
                          {mockSha}
                        </span>
                        <span>•</span>
                        <span className="shrink-0">{formatRelativeDate(cap.created_at)}</span>
                      </div>
                    </div>

                    <ChevronRight className="w-3.5 h-3.5 mt-1.5 text-sip-text-tertiary group-hover:text-[var(--color-primary)] transition-colors shrink-0" />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </SpotlightCard>
  );
}

export default function RecentChangesWidget({ capabilities, isLoading }: RecentChangesWidgetProps) {
  return (
    <ErrorBoundary>
      <RecentChangesInner capabilities={capabilities} isLoading={isLoading} />
    </ErrorBoundary>
  );
}
