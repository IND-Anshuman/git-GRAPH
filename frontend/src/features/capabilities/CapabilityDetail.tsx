'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Boxes, Sparkles, HelpCircle } from 'lucide-react';
import { useUIStore } from '@/stores';
import { useCapability } from '@/hooks/useCapabilities';
import { DETAIL_TABS, type DetailTabId } from '@/lib/constants';
import { cn } from '@/lib/utils';
import StatusBadge from '@/components/common/StatusBadge';
import RiskBadge from '@/components/common/RiskBadge';
import EmptyState from '@/components/common/EmptyState';
import LoadingSpinner from '@/components/common/LoadingSpinner';

// Lazy-loaded Tab content
const OverviewTab = dynamic(() => import('./tabs/OverviewTab'), {
  loading: () => <TabLoader label="Overview" />,
});
const ConceptsTab = dynamic(() => import('./tabs/ConceptsTab'), {
  loading: () => <TabLoader label="Concepts" />,
});
const BehaviorsTab = dynamic(() => import('./tabs/BehaviorsTab'), {
  loading: () => <TabLoader label="Behaviors" />,
});
const DependenciesTab = dynamic(() => import('./tabs/DependenciesTab'), {
  loading: () => <TabLoader label="Dependencies" />,
});
const CoverageTab = dynamic(() => import('./tabs/CoverageTab'), {
  loading: () => <TabLoader label="Coverage" />,
});
const HealthTab = dynamic(() => import('./tabs/HealthTab'), {
  loading: () => <TabLoader label="Health" />,
});
const TimelineTab = dynamic(() => import('./tabs/TimelineTab'), {
  loading: () => <TabLoader label="Timeline" />,
});

function TabLoader({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
      <LoadingSpinner size="md" />
      <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
        Loading {label} Layer...
      </span>
    </div>
  );
}

export function CapabilityDetail() {
  const selectedCapabilityId = useUIStore((s) => s.selectedCapabilityId);
  const activeTab = useUIStore((s) => s.activeDetailTab);
  const setActiveTab = useUIStore((s) => s.setActiveDetailTab);

  const { data: capability, isLoading, isError } = useCapability(selectedCapabilityId);

  // If no capability is selected
  if (!selectedCapabilityId) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <EmptyState
          icon={<Boxes className="w-10 h-10" />}
          title="No Capability Selected"
          description="Select a capability from the navigator to explore its semantic structures, behavior mapping, dependencies, and health metrics."
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 p-8">
        <LoadingSpinner size="lg" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Resolving Capability Node...
        </span>
      </div>
    );
  }

  if (isError || !capability) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <span className="text-2xl mb-2">⚠️</span>
        <h3 className="text-sm font-bold text-sip-text-primary mb-1">
          Capability Resolve Error
        </h3>
        <p className="text-xs text-sip-text-secondary max-w-sm">
          Failed to fetch capability profile. Verify repository sync status and API connection.
        </p>
      </div>
    );
  }

  const getRiskLevel = (score: number) => {
    if (score >= 0.8) return 'critical';
    if (score >= 0.6) return 'high';
    if (score >= 0.3) return 'medium';
    return 'low';
  };

  const getHealthStatus = (cov: number, risk: number) => {
    if (cov < 0.5 || risk > 0.6) return 'critical';
    if (cov < 0.75 || risk > 0.3) return 'warning';
    return 'healthy';
  };

  const riskLevel = getRiskLevel(capability.risk_score);
  const healthStatus = getHealthStatus(capability.coverage_score, capability.risk_score);

  // Render tab content based on activeTab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab capabilityId={capability.id} />;
      case 'concepts':
        return <ConceptsTab capabilityId={capability.id} />;
      case 'behaviors':
        return <BehaviorsTab capabilityId={capability.id} />;
      case 'dependencies':
        return <DependenciesTab capabilityId={capability.id} />;
      case 'coverage':
        return <CoverageTab capabilityId={capability.id} />;
      case 'health':
        return <HealthTab capabilityId={capability.id} />;
      case 'timeline':
        return <TimelineTab capabilityId={capability.id} />;
      default:
        return <OverviewTab capabilityId={capability.id} />;
    }
  };

  return (
    <section
      aria-label="Capability details"
      className="flex flex-col h-full bg-sip-bg-base overflow-hidden"
    >
      {/* Detail Header */}
      <div className="border-b border-[var(--color-border)] p-6 bg-sip-surface shrink-0">
        <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-base font-bold text-sip-text-primary tracking-tight truncate max-w-[300px] sm:max-w-[400px]">
                {capability.name}
              </h2>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider bg-sip-surface border border-[var(--color-border)]/80 px-2 py-0.5 rounded-sm">
                {capability.capability_type}
              </span>
            </div>
            <p className="text-xs text-sip-text-secondary mt-1 max-w-xl truncate">
              {capability.description || 'No conceptual description resolved.'}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <StatusBadge status={healthStatus} size="sm" />
            <RiskBadge level={riskLevel} />
          </div>
        </div>

        {/* Tab Triggers */}
        <div className="flex items-center gap-1 overflow-x-auto border-b border-[var(--color-border)]/50 pb-1 scrollbar-none">
          {DETAIL_TABS.map((tab) => {
            const isSelected = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as DetailTabId)}
                aria-selected={isSelected}
                role="tab"
                className={cn(
                  'px-3.5 py-2 text-xs font-semibold rounded-md border border-transparent transition-all select-none',
                  isSelected
                    ? 'bg-[#161A22] border-[var(--color-border)] text-sip-text-primary shadow-sm font-bold'
                    : 'text-sip-text-secondary hover:text-sip-text-primary hover:bg-[#161A22]/50'
                )}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Detail Tab Content Area */}
      <div className="flex-1 overflow-y-auto p-6 bg-sip-bg-base">
        {renderTabContent()}
      </div>
    </section>
  );
}

export default CapabilityDetail;
