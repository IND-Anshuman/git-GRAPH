'use client';

import React from 'react';
import { Award, ShieldCheck, CheckCircle2, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { useCapability } from '@/hooks/useCapabilities';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ScoreRing from '@/components/common/ScoreRing';
import MetricCard from '@/components/common/MetricCard';
import { scoreToInt, formatScore } from '@/lib/utils';

interface CoverageTabProps {
  capabilityId: string;
}

export default function CoverageTab({ capabilityId }: CoverageTabProps) {
  const { data: capability, isLoading, isError } = useCapability(capabilityId);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
        <LoadingSpinner size="md" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Querying Coverage Matrices...
        </span>
      </div>
    );
  }

  if (isError || !capability) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <span className="text-xl mb-2">⚠️</span>
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          Coverage Offline
        </h4>
        <p className="text-xs text-sip-text-secondary">
          Failed to fetch coverage parameters.
        </p>
      </div>
    );
  }

  const cov = scoreToInt(capability.coverage_score);
  const mat = scoreToInt(capability.maturity_score);
  const conf = scoreToInt(capability.confidence);
  const rsk = scoreToInt(capability.risk_score);

  const chartData = [
    { name: 'Coverage', value: cov, color: 'var(--color-primary)' },
    { name: 'Maturity', value: mat, color: 'var(--color-success)' },
    { name: 'Confidence', value: conf, color: '#8B5CF6' },
    { name: 'Risk Limit', value: 100 - rsk, color: '#F97316' },
  ];

  return (
    <div className="flex flex-col gap-6 p-1 animate-fade-in">
      {/* Top Banner Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Coverage ScoreRing */}
        <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5 flex flex-col items-center justify-center text-center gap-3">
          <ScoreRing score={cov} size={84} strokeWidth={6} label="Code Coverage" />
          <div className="flex flex-col">
            <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider">
              Test Coverage
            </span>
            <span className="text-xs text-sip-text-secondary mt-0.5">
              Code execution verification
            </span>
          </div>
        </div>

        {/* Aggregate details */}
        <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5 col-span-2 flex flex-col justify-center gap-4">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-sip-text-tertiary shrink-0 mt-0.5 text-[var(--color-success)]" />
            <div className="flex flex-col">
              <h4 className="text-xs font-bold text-sip-text-primary uppercase tracking-wider">
                Coverage Sufficiency Verified
              </h4>
              <p className="text-xs text-sip-text-secondary mt-0.5 leading-relaxed">
                Coverage matches strict validation boundaries. Ingested behavioral flows are mapped against unit tests.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards & Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score metrics */}
        <div className="grid grid-cols-2 gap-3">
          <MetricCard
            title="Maturity Index"
            value={formatScore(capability.maturity_score)}
            subtitle="Architectural compliance"
            icon={<Award size={14} />}
          />
          <MetricCard
            title="Confidence Index"
            value={formatScore(capability.confidence)}
            subtitle="Verification level"
            icon={<ShieldCheck size={14} />}
          />
          <MetricCard
            title="Structural Risk"
            value={formatScore(capability.risk_score)}
            subtitle="Encapsulation boundary risk"
            icon={<TrendingUp size={14} />}
          />
          <div className="bg-sip-surface/20 border border-dashed border-[var(--color-border)] rounded-lg p-4 flex flex-col items-center justify-center text-center text-[10px] text-sip-text-muted font-mono leading-normal uppercase">
            <span>COV SCORE: {cov}</span>
            <span>MAT SCORE: {mat}</span>
            <span>CONF SCORE: {conf}</span>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5 flex flex-col h-[240px]">
          <h4 className="text-xs font-semibold text-sip-text-tertiary uppercase tracking-wider mb-4">
            Quality Attributes Comparison
          </h4>
          <div className="flex-1 min-h-0 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="name"
                  tick={{ fill: 'var(--color-text-secondary)', fontSize: 10 }}
                  axisLine={{ stroke: 'var(--color-border)' }}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: 'var(--color-text-secondary)', fontSize: 10 }}
                  axisLine={{ stroke: 'var(--color-border)' }}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  contentStyle={{
                    backgroundColor: '#161A22',
                    borderColor: 'var(--color-border)',
                    borderRadius: 'var(--radius-lg)',
                  }}
                  itemStyle={{
                    color: 'var(--color-text-primary)',
                    fontSize: '11px',
                  }}
                />
                <Bar dataKey="value" fill="var(--color-primary)" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
