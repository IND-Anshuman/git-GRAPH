'use client';

import React from 'react';
import { Activity, ShieldAlert, Layers } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCapabilities } from '@/hooks/useCapabilities';
import ScoreRing from '@/components/common/ScoreRing';
import StatusBadge from '@/components/common/StatusBadge';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorBoundary from '@/components/common/ErrorBoundary';
import { formatScore } from '@/lib/utils';
import type { HealthStatus } from '@/types/platform';

interface RepositoryHealthWidgetProps {
  repositoryId: string | null;
}

function RepositoryHealthInner({ repositoryId }: RepositoryHealthWidgetProps) {
  const { data: capabilities = [], isLoading, isError, refetch } = useCapabilities(repositoryId);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[260px] bg-sip-surface border border-[var(--color-border)] rounded-lg p-6">
        <LoadingSpinner size="md" className="mb-2" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Computing Health Profile...
        </span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-[260px] bg-sip-surface border border-[var(--color-border)] rounded-lg p-6 text-center">
        <ShieldAlert className="w-8 h-8 text-[var(--color-danger)] mb-2" />
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          Health Aggregation Failed
        </h4>
        <p className="text-xs text-sip-text-secondary mb-4 max-w-[200px]">
          Unable to resolve capability health parameters.
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

  if (capabilities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[260px] bg-sip-surface border border-[var(--color-border)] rounded-lg p-6 text-center">
        <Activity className="w-8 h-8 text-sip-text-tertiary mb-2" />
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          No Capabilities Mapped
        </h4>
        <p className="text-xs text-sip-text-secondary max-w-[220px]">
          Add capabilities or start discovery to compute health profiles.
        </p>
      </div>
    );
  }

  // Helper to detect if values are 0-1 scale or 0-100 scale
  const parseScore = (val: number) => {
    // If the value is > 1.0, it is already on a 0-100 scale
    return val > 1 ? val / 100 : val;
  };

  // Compute Averages
  const totalCaps = capabilities.length;
  let sumMaturity = 0;
  let sumRisk = 0;
  let sumCoverage = 0;

  capabilities.forEach((c) => {
    sumMaturity += parseScore(c.maturity_score);
    sumRisk += parseScore(c.risk_score);
    sumCoverage += parseScore(c.coverage_score);
  });

  const avgMaturity = sumMaturity / totalCaps;
  const avgRisk = sumRisk / totalCaps;
  const avgCoverage = sumCoverage / totalCaps;

  // Health Score Formula: (Maturity + Coverage + (1 - Risk)) / 3
  const healthScoreRaw = (avgMaturity + avgCoverage + (1 - avgRisk)) / 3;
  const healthScore = Math.max(0, Math.min(100, Math.round(healthScoreRaw * 100)));

  // Determine Status Badge
  let status: HealthStatus = 'healthy';
  if (healthScore < 50 || avgRisk > 0.6) {
    status = 'critical';
  } else if (healthScore < 75 || avgRisk > 0.3) {
    status = 'warning';
  }

  // Architecture and drift placeholders (Stage 1 / repository level default metadata)
  const archType = totalCaps > 8 ? 'Distributed Hexagonal' : 'Monolithic Clean';
  const driftScoreRaw = Math.max(0.04, Math.min(0.25, avgRisk * 0.4)); // synthetic but proportional to risk
  const driftText = `${Math.round(driftScoreRaw * 100)}% Drift`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-5 flex flex-col justify-between h-[260px]"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[var(--color-border)] pb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-[var(--color-primary)]" />
          <h3 className="text-sm font-bold text-sip-text-primary">Repository Health</h3>
        </div>
        <StatusBadge status={status} size="sm" />
      </div>

      {/* Content */}
      <div className="flex items-center gap-6 flex-1">
        {/* Large Score Ring */}
        <div className="flex shrink-0">
          <ScoreRing score={healthScore} size={84} strokeWidth={6} label="Health" />
        </div>

        {/* Metrics Grid */}
        <div className="flex-1 grid grid-cols-2 gap-x-4 gap-y-3">
          <div className="flex flex-col">
            <span className="text-[10px] text-sip-text-tertiary font-semibold uppercase tracking-wider">
              Avg Risk
            </span>
            <span className="text-sm font-bold text-sip-text-primary">
              {formatScore(avgRisk)}
            </span>
          </div>

          <div className="flex flex-col">
            <span className="text-[10px] text-sip-text-tertiary font-semibold uppercase tracking-wider">
              Avg Coverage
            </span>
            <span className="text-sm font-bold text-sip-text-primary">
              {formatScore(avgCoverage)}
            </span>
          </div>

          <div className="flex flex-col">
            <span className="text-[10px] text-sip-text-tertiary font-semibold uppercase tracking-wider">
              Avg Maturity
            </span>
            <span className="text-sm font-bold text-sip-text-primary">
              {formatScore(avgMaturity)}
            </span>
          </div>

          <div className="flex flex-col">
            <span className="text-[10px] text-sip-text-tertiary font-semibold uppercase tracking-wider">
              Architecture
            </span>
            <span className="text-xs font-semibold text-sip-text-secondary truncate flex items-center gap-1 mt-0.5">
              <Layers className="w-3 h-3 text-sip-text-tertiary" />
              {archType}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-3 pt-3 border-t border-[var(--color-border)] flex items-center justify-between text-[11px] text-sip-text-secondary">
        <span>Aggregate of {totalCaps} capabilities</span>
        <span className="font-mono text-sip-text-muted">{driftText}</span>
      </div>
    </motion.div>
  );
}

export default function RepositoryHealthWidget({ repositoryId }: RepositoryHealthWidgetProps) {
  return (
    <ErrorBoundary>
      <RepositoryHealthInner repositoryId={repositoryId} />
    </ErrorBoundary>
  );
}
