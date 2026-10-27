'use client';

import React from 'react';
import { Cpu, Briefcase, Blocks, Shield, Layers, HelpCircle, ArrowUpRight, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { useCapabilities } from '@/hooks/useCapabilities';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorBoundary from '@/components/common/ErrorBoundary';
import SpotlightCard from '@/components/common/SpotlightCard';
import AnimatedCounter from '@/components/common/AnimatedCounter';

interface CapabilitySummaryWidgetProps {
  repositoryId: string | null;
}

const DOMAIN_METADATA: Record<string, { label: string; icon: React.ComponentType<{ size?: number; className?: string }>; color: string }> = {
  BUSINESS: { label: 'Business Systems', icon: Briefcase, color: '#4F8CFF' },
  AI: { label: 'AI Intelligence', icon: Cpu, color: '#8B5CF6' },
  TECHNICAL: { label: 'Technical Core', icon: Blocks, color: '#10B981' },
  INFRASTRUCTURE: { label: 'Infrastructure', icon: Layers, color: '#F97316' },
  SECURITY: { label: 'Security Domain', icon: Shield, color: '#EF4444' },
  INTEGRATION: { label: 'Integration Layer', icon: Layers, color: '#06B6D4' },
};

interface DomainStat {
  count: number;
  maturitySum: number;
  coverageSum: number;
  riskSum: number;
  maturity: number[];
}

const emptyStat = (): DomainStat => ({ count: 0, maturitySum: 0, coverageSum: 0, riskSum: 0, maturity: [] });

function CapabilitySummaryInner({ repositoryId }: CapabilitySummaryWidgetProps) {
  const { data: capabilities = [], isLoading, isError, refetch } = useCapabilities(repositoryId);

  // ── All hooks MUST be called unconditionally before any early returns ──

  // Group stats by Domain type
  const domainStats = React.useMemo(() => {
    const stats: Record<string, DomainStat> = {};
    Object.keys(DOMAIN_METADATA).forEach((key) => {
      stats[key] = emptyStat();
    });
    // Discovery order, so each domain's sparkline reads oldest -> newest.
    const ordered = [...capabilities].sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    );
    ordered.forEach((c) => {
      const type = (c.capability_type || 'TECHNICAL').toUpperCase();
      if (!stats[type]) {
        stats[type] = emptyStat();
      }
      const maturity = c.maturity_score > 1 ? c.maturity_score / 100 : c.maturity_score;
      stats[type].count++;
      stats[type].maturity.push(maturity * 100);
      stats[type].maturitySum += maturity;
      stats[type].coverageSum += c.coverage_score > 1 ? c.coverage_score / 100 : c.coverage_score;
      stats[type].riskSum += c.risk_score > 1 ? c.risk_score / 100 : c.risk_score;
    });
    return stats;
  }, [capabilities]);

  // ── Early returns AFTER all hooks ──

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[320px] glass-card p-6">
        <LoadingSpinner size="md" className="mb-2" />
        <span className="text-[10px] text-[var(--color-text-tertiary)] font-bold uppercase tracking-widest font-mono">
          Assembling intelligence matrix...
        </span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-[320px] glass-card p-6 text-center">
        <AlertTriangle className="w-8 h-8 text-[var(--color-danger)] mb-2" />
        <h4 className="text-sm font-semibold text-[var(--color-text-primary)] mb-1">
          Matrix aggregation failed
        </h4>
        <button
          onClick={() => void refetch()}
          type="button"
          className="px-3 py-1.5 mt-2 text-xs font-semibold rounded bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  // Generate simple sparkline SVG path
  const drawSparkline = (data: number[]) => {
    const width = 50;
    const height = 14;
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min === 0 ? 1 : max - min;
    const points = data.map((val, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    });
    return `M ${points.join(' L ')}`;
  };

  // Only render domains that have active capabilities (or technical core as fallback)
  const activeDomains = Object.entries(domainStats).filter(([_, stat]) => stat.count > 0);
  if (activeDomains.length === 0) {
    // default to show TECHNICAL core if database returned 0 (so we never render a blank card)
    activeDomains.push(['TECHNICAL', emptyStat()]);
  }

  return (
    <SpotlightCard
      className="p-5 flex flex-col justify-between h-[320px]"
      glowColor="rgba(176, 38, 255, 0.18)"
      cornerBrackets
    >
      {/* Header */}
      <div
        className="flex items-center justify-between pb-3 shrink-0"
        style={{ borderBottom: '1px solid rgba(0,240,255,0.1)' }}
      >
        <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-[var(--color-text-tertiary)] font-mono leading-none">
          Capability Intelligence Matrix
        </span>
        <Link
          href="/capabilities"
          className="text-[10px] uppercase font-bold tracking-wider flex items-center gap-0.5 transition-colors"
          style={{ color: 'var(--neon-blue)' }}
        >
          Analysis
          <ArrowUpRight className="w-3 h-3" />
        </Link>
      </div>

      {/* Domain Rows */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-3 py-3 pr-1 scrollbar-thin">
        {activeDomains.map(([key, stat]) => {
          const meta = DOMAIN_METADATA[key] || {
            label: key,
            icon: HelpCircle,
            color: 'var(--color-text-tertiary)',
          };
          const Icon = meta.icon;
          const count = stat.count;
          const avgMaturity = count > 0 ? (stat.maturitySum / count) * 100 : 0;
          const avgCoverage = count > 0 ? (stat.coverageSum / count) * 100 : 0;


          return (
            <div
              key={key}
              className="flex items-center justify-between gap-4 p-2.5 rounded-xl transition-colors"
              style={{
                background: 'rgba(0,240,255,0.02)',
                border: '1px solid rgba(0,240,255,0.08)',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'rgba(0,240,255,0.05)';
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(0,240,255,0.15)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'rgba(0,240,255,0.02)';
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(0,240,255,0.08)';
              }}
            >
              {/* Domain Tag & Title */}
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <span
                  className="w-8 h-8 rounded-lg flex items-center justify-center border shrink-0"
                  style={{
                    backgroundColor: `${meta.color}0a`,
                    borderColor: `${meta.color}25`,
                    color: meta.color,
                  }}
                >
                  <Icon size={15} />
                </span>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-bold text-[var(--color-text-primary)] truncate">
                    {meta.label}
                  </span>
                  <span className="text-[10px] font-mono text-[var(--color-text-tertiary)] mt-0.5">
                    {count} Discovered Nodes
                  </span>
                </div>
              </div>

              {/* Maturity of each capability in this domain, in discovery order */}
              <div className="flex items-center gap-3 shrink-0">
                {stat.maturity.length > 1 && (
                  <svg className="w-12 h-4 overflow-visible opacity-50 hidden sm:block" aria-hidden="true">
                    <path
                      d={drawSparkline(stat.maturity)}
                      fill="none"
                      stroke={meta.color}
                      strokeWidth={1.5}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
                <span className="shrink-0 font-mono text-[10px] text-[var(--color-text-tertiary)]">
                  {count} cap{count === 1 ? '' : 's'}
                </span>
              </div>

              {/* Coverage & Maturity Metrics */}
              <div className="flex items-center gap-4 shrink-0 font-mono text-[11px] tabular-nums">
                <div className="flex flex-col items-end">
                  <span className="text-[9px] uppercase font-bold tracking-wider text-[var(--color-text-tertiary)] font-mono leading-none">
                    Maturity
                  </span>
                  <span className="text-[var(--color-text-primary)] font-bold mt-1">
                    <AnimatedCounter value={Math.round(avgMaturity)} formatter={(v) => `${Math.round(v)}%`} />
                  </span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-[9px] uppercase font-bold tracking-wider text-[var(--color-text-tertiary)] font-mono leading-none">
                    Coverage
                  </span>
                  <span className="text-[var(--color-text-primary)] font-bold mt-1">
                    <AnimatedCounter value={Math.round(avgCoverage)} formatter={(v) => `${Math.round(v)}%`} />
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </SpotlightCard>
  );
}

export default function CapabilitySummaryWidget({ repositoryId }: CapabilitySummaryWidgetProps) {
  return (
    <ErrorBoundary>
      <CapabilitySummaryInner repositoryId={repositoryId} />
    </ErrorBoundary>
  );
}
