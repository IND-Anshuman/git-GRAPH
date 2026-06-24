'use client';

import React from 'react';
import AppShell from '@/components/layout/AppShell';
import { useUIStore } from '@/stores';
import { useCapabilities } from '@/hooks/useCapabilities';
import { useRepositories } from '@/hooks/useRepositories';
import RepositoryHealthWidget from '@/features/dashboard/RepositoryHealthWidget';
import CapabilitySummaryWidget from '@/features/dashboard/CapabilitySummaryWidget';
import DependencyOverviewWidget from '@/features/dashboard/DependencyOverviewWidget';
import RecentChangesWidget from '@/features/dashboard/RecentChangesWidget';
import HealthDistributionChart from '@/features/dashboard/HealthDistributionChart';
import ErrorBoundary from '@/components/common/ErrorBoundary';
import LoadingSpinner from '@/components/common/LoadingSpinner';

import type { Capability } from '@/types/platform';

export default function DashboardPage() {
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);
  const { data: repositories = [], isLoading: isReposLoading } = useRepositories();

  // Load capabilities at page level to feed into sharing widgets
  const { data: capabilitiesData, isLoading: isCapsLoading } = useCapabilities(activeRepositoryId);
  const capabilities = capabilitiesData as Capability[] | undefined;

  const activeRepo = repositories.find((r) => r.id === activeRepositoryId);

  return (
    <AppShell>
      <div className="p-6 max-w-[1600px] mx-auto flex flex-col gap-6">
        {/* Page Header */}
        <div className="flex flex-col gap-1 border-b border-[var(--color-border)] pb-4 shrink-0">
          <h1 className="text-xl font-bold tracking-tight text-sip-text-primary">
            Command Center
          </h1>
          <p className="text-xs text-sip-text-secondary">
            {activeRepo ? `Executive overview for repository: ${activeRepo.name}` : 'Repository executive overview'}
          </p>
        </div>

        {/* Dashboard Content */}
        {isReposLoading ? (
          <div className="flex flex-col items-center justify-center min-h-[300px] gap-3">
            <LoadingSpinner size="md" />
            <span className="text-xs text-sip-text-secondary font-mono">
              QUERYING WORKSPACE STATE...
            </span>
          </div>
        ) : !activeRepositoryId ? (
          <div className="border border-dashed border-[var(--color-border)] rounded-lg p-12 text-center max-w-md mx-auto my-12 bg-sip-surface/30">
            <span className="text-2xl mb-2 inline-block">📁</span>
            <h3 className="text-sm font-semibold text-sip-text-primary mb-1">
              Select a Repository
            </h3>
            <p className="text-xs text-sip-text-secondary leading-relaxed mb-4">
              Switch or select a repository from the selector at the top bar to inspect its code intelligence layers.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            {/* 4-Widget Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Row 1 */}
              <ErrorBoundary>
                <RepositoryHealthWidget repositoryId={activeRepositoryId} />
              </ErrorBoundary>

              <ErrorBoundary>
                <CapabilitySummaryWidget repositoryId={activeRepositoryId} />
              </ErrorBoundary>

              {/* Row 2 */}
              <ErrorBoundary>
                <DependencyOverviewWidget capabilities={capabilities} isLoading={isCapsLoading} />
              </ErrorBoundary>

              <ErrorBoundary>
                <RecentChangesWidget capabilities={capabilities} isLoading={isCapsLoading} />
              </ErrorBoundary>
            </div>

            {/* Row 3 - Full Width chart */}
            <div className="w-full">
              <ErrorBoundary>
                <HealthDistributionChart capabilities={capabilities} isLoading={isCapsLoading} />
              </ErrorBoundary>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
