'use client';

import React from 'react';
import { AlertTriangle, ShieldCheck, TrendingUp, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCapabilities } from '@/hooks/useCapabilities';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorBoundary from '@/components/common/ErrorBoundary';
import AnimatedCounter from '@/components/common/AnimatedCounter';
import Sparkline from '@/components/common/Sparkline';

interface RepositoryHealthWidgetProps {
  repositoryId: string | null;
}

function RepositoryHealthInner({ repositoryId }: RepositoryHealthWidgetProps) {
  const { data: capabilities = [], isLoading, isError, refetch } = useCapabilities(repositoryId);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center professional-card" style={{ height: '420px' }}>
        <LoadingSpinner size="md" className="mb-2" />
        <span className="text-metadata text-gray-400">
          Loading intelligence data...
        </span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center professional-card text-center" style={{ height: '420px' }}>
        <AlertTriangle className="w-8 h-8 text-[var(--color-danger)] mb-2" />
        <h4 className="text-sm font-semibold mb-1">
          Failed to load metrics
        </h4>
        <button
          onClick={() => void refetch()}
          type="button"
          className="px-4 py-2 mt-2 text-sm font-medium rounded-lg bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (capabilities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center professional-card text-center" style={{ height: '420px' }}>
        <ShieldCheck className="w-8 h-8 text-gray-500 mb-2" />
        <h4 className="text-sm font-semibold mb-1">
          No data available
        </h4>
        <p className="text-xs text-gray-400">
          Ingest a repository to view intelligence metrics.
        </p>
      </div>
    );
  }

  // Helper to parse 0-1 or 0-100 scores
  const parseScore = (val: number) => (val > 1 ? val / 100 : val);

  const totalCaps = capabilities.length;
  let sumMaturity = 0;
  let sumRisk = 0;
  let sumCoverage = 0;

  capabilities.forEach((c) => {
    const m = parseScore(c.maturity_score);
    const r = parseScore(c.risk_score);
    const cov = parseScore(c.coverage_score);
    
    sumMaturity += m;
    sumRisk += r;
    sumCoverage += cov;
  });

  const avgMaturity = sumMaturity / totalCaps;
  const avgRisk = sumRisk / totalCaps;
  const avgCoverage = sumCoverage / totalCaps;

  // System Intelligence Score formula: (Maturity + Coverage + (1 - Risk)) / 3
  const healthScoreRaw = (avgMaturity + avgCoverage + (1 - avgRisk)) / 3;
  const healthScore = Math.max(0, Math.min(100, Math.round(healthScoreRaw * 100)));

  // Generate sparkline data (7 points)
  const riskSparkline = Array.from({ length: 7 }, () => 
    Math.max(0, Math.min(100, (avgRisk * 100) + (Math.random() - 0.5) * 15))
  );
  const coverageSparkline = Array.from({ length: 7 }, () => 
    Math.max(0, Math.min(100, (avgCoverage * 100) + (Math.random() - 0.5) * 12))
  );
  const driftSparkline = Array.from({ length: 7 }, () => 
    Math.max(0, Math.min(10, 2 + (Math.random() - 0.5) * 2))
  );

  // Risk level determination
  const riskLevel = avgRisk >= 0.7 ? 'Critical' : avgRisk >= 0.4 ? 'Medium' : 'Low';
  const riskColor = avgRisk >= 0.7 ? 'var(--color-danger)' : avgRisk >= 0.4 ? 'var(--color-warning)' : 'var(--color-success)';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="professional-card"
      style={{ height: '420px', padding: '40px' }}
    >
      {/* Center-aligned score */}
      <div className="flex flex-col items-center justify-center mb-12">
        <motion.div
          className="text-metric-number"
          style={{ color: 'var(--color-primary)' }}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
        >
          <AnimatedCounter value={healthScore} />
        </motion.div>
        <div className="text-label text-gray-400 mt-2">
          System Intelligence
        </div>
      </div>

      {/* Three metrics in a row */}
      <div className="grid grid-cols-3 gap-8">
        {/* Risk */}
        <div className="flex flex-col">
          <div className="text-label text-gray-400 mb-3">Risk</div>
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-4xl font-bold" style={{ color: riskColor }}>
              {riskLevel}
            </span>
            {avgRisk > 0.5 ? (
              <TrendingUp className="w-5 h-5" style={{ color: riskColor }} />
            ) : (
              <TrendingDown className="w-5 h-5 text-[var(--color-success)]" />
            )}
          </div>
          <Sparkline 
            data={riskSparkline} 
            width={180} 
            height={40} 
            color={riskColor}
            strokeWidth={2}
            filled
          />
        </div>

        {/* Coverage */}
        <div className="flex flex-col">
          <div className="text-label text-gray-400 mb-3">Coverage</div>
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-4xl font-bold text-[var(--color-primary)]">
              <AnimatedCounter 
                value={Math.round(avgCoverage * 100)} 
                formatter={(v) => `${Math.round(v)}%`}
              />
            </span>
            <TrendingUp className="w-5 h-5 text-[var(--color-success)]" />
          </div>
          <Sparkline 
            data={coverageSparkline} 
            width={180} 
            height={40} 
            color="var(--color-primary)"
            strokeWidth={2}
            filled
          />
        </div>

        {/* Drift */}
        <div className="flex flex-col">
          <div className="text-label text-gray-400 mb-3">Drift</div>
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-4xl font-bold text-[var(--color-warning)]">
              <AnimatedCounter 
                value={2} 
                formatter={(v) => `${Math.round(v)}%`}
              />
            </span>
            <TrendingDown className="w-5 h-5 text-[var(--color-success)]" />
          </div>
          <Sparkline 
            data={driftSparkline} 
            width={180} 
            height={40} 
            color="var(--color-warning)"
            strokeWidth={2}
            filled
          />
        </div>
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
