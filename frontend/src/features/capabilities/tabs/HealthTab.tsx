'use client';

import React from 'react';
import { ShieldAlert, Activity, CheckCircle2 } from 'lucide-react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
} from 'recharts';
import { useCapabilityHealth } from '@/hooks/useCapabilities';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ScoreRing from '@/components/common/ScoreRing';
import { scoreToInt } from '@/lib/utils';

interface HealthTabProps {
  capabilityId: string;
}

export default function HealthTab({ capabilityId }: HealthTabProps) {
  const { data: healthData, isLoading, isError } = useCapabilityHealth(capabilityId);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
        <LoadingSpinner size="md" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Querying Health Telemetry...
        </span>
      </div>
    );
  }

  if (isError || !healthData) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <span className="text-xl mb-2">⚠️</span>
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          Telemetry Offline
        </h4>
        <p className="text-xs text-sip-text-secondary max-w-sm">
          Failed to fetch health and risk metrics for this capability.
        </p>
      </div>
    );
  }

  // Handle value parsing: convert 0-1 metrics to 0-100 scale
  const parseScore = (val: number) => {
    return val <= 1 ? Math.round(val * 100) : Math.round(val);
  };

  const health = parseScore(healthData.health_score);
  const risk = parseScore(healthData.risk_score);
  const stability = parseScore(healthData.stability_score);
  const cohesion = parseScore(healthData.cohesion_score);
  const coupling = parseScore(healthData.coupling_score);
  const boundary = parseScore(healthData.boundary_strength);

  // Invert risk and coupling so that "higher is better" on the radar shape
  const invRisk = 100 - risk;
  const invCoupling = 100 - coupling;

  const radarData = [
    { subject: 'Health', value: health, fullMark: 100 },
    { subject: 'Low Risk', value: invRisk, fullMark: 100 },
    { subject: 'Stability', value: stability, fullMark: 100 },
    { subject: 'Cohesion', value: cohesion, fullMark: 100 },
    { subject: 'Low Coupling', value: invCoupling, fullMark: 100 },
    { subject: 'Boundary', value: boundary, fullMark: 100 },
  ];

  const barData = [
    { name: 'Health', value: health, color: 'var(--color-success)' },
    { name: 'Risk', value: risk, color: 'var(--color-danger)' },
    { name: 'Stability', value: stability, color: 'var(--color-primary)' },
    { name: 'Cohesion', value: cohesion, color: '#8B5CF6' },
    { name: 'Coupling', value: coupling, color: '#F97316' },
    { name: 'Boundary', value: boundary, color: '#06B6D4' },
  ];

  return (
    <div className="flex flex-col gap-6 p-1 animate-fade-in">
      {/* Leakage warning */}
      {healthData.boundary_leakage_detected ? (
        <div className="bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/30 rounded-lg p-4 flex gap-3 items-start">
          <ShieldAlert className="w-5 h-5 text-[var(--color-danger)] shrink-0 mt-0.5" />
          <div className="flex flex-col">
            <h4 className="text-xs font-bold text-[var(--color-danger)] uppercase tracking-wider">
              Boundary Leakage Detected
            </h4>
            <p className="text-xs text-sip-text-secondary mt-1 leading-relaxed">
              This capability references or modifies entities outside its defined semantic boundary without formal contracts. Inward/outward coupling ratios violate safety limits.
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-[var(--color-success)]/10 border border-[var(--color-success)]/30 rounded-lg p-4 flex gap-3 items-start">
          <CheckCircle2 className="w-5 h-5 text-[var(--color-success)] shrink-0 mt-0.5" />
          <div className="flex flex-col">
            <h4 className="text-xs font-bold text-[var(--color-success)] uppercase tracking-wider">
              Boundary Integrity Secure
            </h4>
            <p className="text-xs text-sip-text-secondary mt-1 leading-relaxed">
              No boundary leakage detected. The capability conforms fully to encapsulated hexagonal/monolithic design boundaries.
            </p>
          </div>
        </div>
      )}

      {/* Main Charts Side-by-Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5 flex flex-col items-center min-h-[320px]">
          <h4 className="text-xs font-semibold text-sip-text-tertiary uppercase tracking-wider mb-4 self-start">
            Structural Cohesion (Higher is Better)
          </h4>
          <div className="w-full h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="var(--color-border)" />
                <PolarAngleAxis
                  dataKey="subject"
                  tick={{ fill: 'var(--color-text-secondary)', fontSize: 10, fontWeight: 500 }}
                />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'var(--color-text-muted)', fontSize: 8 }} />
                <Radar
                  name="Capability Health"
                  dataKey="value"
                  stroke="var(--color-primary)"
                  fill="var(--color-primary)"
                  fillOpacity={0.25}
                />
                <Tooltip
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
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart metrics */}
        <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5 flex flex-col justify-between min-h-[320px]">
          <h4 className="text-xs font-semibold text-sip-text-tertiary uppercase tracking-wider mb-4">
            Individual Metric Breakdown
          </h4>
          <div className="w-full h-[200px] flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                  cursor={{ fill: 'rgba(255,255,255,0.03)' }}
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
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {barData.map((entry, index) => (
                    <span key={index} style={{ display: 'none' }} />
                  ))}
                  {barData.map((entry, index) => (
                    <Bar key={entry.name} dataKey="value" fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-between items-center text-[10px] text-sip-text-muted mt-2 pt-2 border-t border-[var(--color-border)]/40 font-mono">
            <span>Aggregated Structural Layer</span>
            <span>COHESION VS COUPLING</span>
          </div>
        </div>
      </div>
    </div>
  );
}
