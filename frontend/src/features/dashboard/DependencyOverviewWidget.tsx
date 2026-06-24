'use client';

import React from 'react';
import { Network, Blocks, ShieldAlert, Cpu, Share2 } from 'lucide-react';
import { motion } from 'framer-motion';
import type { Capability } from '@/types/platform';
import MetricCard from '@/components/common/MetricCard';
import ErrorBoundary from '@/components/common/ErrorBoundary';

interface DependencyOverviewWidgetProps {
  capabilities: Capability[] | undefined;
  isLoading: boolean;
}

function DependencyOverviewInner({ capabilities = [], isLoading }: DependencyOverviewWidgetProps) {
  // Aggregate data if capabilities are available
  let internalDepsCount = 0;
  let externalDepsCount = 0;
  let conceptsCount = 0;
  let behaviorsCount = 0;

  if (capabilities && capabilities.length > 0) {
    capabilities.forEach((c) => {
      // Internal code entities (e.g., classes/files)
      internalDepsCount += c.entities?.length || 0;
      // External relationships / flows
      externalDepsCount += c.relationships?.length || 0;
      // Concepts
      conceptsCount += c.concepts?.length || 0;
      // Behaviors
      behaviorsCount += c.behaviors?.length || 0;
    });
  }

  // If there are no capabilities and we are not loading, show empty state or stub
  const showEmpty = !isLoading && capabilities.length === 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
      className="bg-sip-surface border border-[var(--color-border)] rounded-lg p-5 flex flex-col justify-between h-auto min-h-[260px]"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[var(--color-border)] pb-3">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-[var(--color-primary)]" />
          <h3 className="text-sm font-bold text-sip-text-primary">Intelligence Overview</h3>
        </div>
        <span className="text-[10px] font-mono text-sip-text-tertiary uppercase tracking-wider">
          Semantic Metrics
        </span>
      </div>

      {showEmpty ? (
        <div className="flex flex-col items-center justify-center flex-1 text-center py-6">
          <Network className="w-8 h-8 text-sip-text-tertiary mb-2" />
          <h4 className="text-xs font-semibold text-sip-text-primary">No Graph Connections</h4>
          <p className="text-[11px] text-sip-text-secondary max-w-[200px]">
            Intelligence overview will populate when capabilities are resolved.
          </p>
        </div>
      ) : (
        /* 2x2 Metric Grid */
        <div className="grid grid-cols-2 gap-3 flex-1">
          <MetricCard
            title="Internal Code Entities"
            value={internalDepsCount}
            subtitle="Classes & Modules"
            isLoading={isLoading}
            icon={<Blocks size={14} />}
            trend={{ direction: 'neutral', label: 'Stable' }}
          />
          <MetricCard
            title="External Contracts"
            value={externalDepsCount}
            subtitle="API & Database Links"
            isLoading={isLoading}
            icon={<Share2 size={14} />}
            trend={{ direction: 'neutral', label: 'Resolved' }}
          />
          <MetricCard
            title="Extracted Concepts"
            value={conceptsCount}
            subtitle="Domain Abstractions"
            isLoading={isLoading}
            icon={<Cpu size={14} />}
            trend={{ direction: 'neutral', label: 'Extracted' }}
          />
          <MetricCard
            title="Identified Behaviors"
            value={behaviorsCount}
            subtitle="Side Effects & Actions"
            isLoading={isLoading}
            icon={<Network size={14} />}
            trend={{ direction: 'neutral', label: 'Monitored' }}
          />
        </div>
      )}
    </motion.div>
  );
}

export default function DependencyOverviewWidget({
  capabilities,
  isLoading,
}: DependencyOverviewWidgetProps) {
  return (
    <ErrorBoundary>
      <DependencyOverviewInner capabilities={capabilities} isLoading={isLoading} />
    </ErrorBoundary>
  );
}
