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
import ErrorBoundary from '@/components/common/ErrorBoundary';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { GlitchText } from '@/components/common/GlitchText';

import type { Capability } from '@/types/platform';

export default function DashboardPage() {
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);
  const { data: repositories = [], isLoading: isReposLoading } = useRepositories();

  const { data: capabilitiesData, isLoading: isCapsLoading } = useCapabilities(activeRepositoryId);
  const capabilities = capabilitiesData as Capability[] | undefined;

  const activeRepo = repositories.find((r) => r.id === activeRepositoryId);

  return (
    <AppShell>
      <div className="px-12 py-8 max-w-[1600px] mx-auto flex flex-col gap-8 w-full relative z-10">
        {/* Page Title Header */}
        <div className="flex flex-col gap-2 shrink-0">
          <h1 className="text-page-title">
            Command Center
          </h1>
          <p className="text-metadata text-gray-400">
            {activeRepo ? (
              <span>
                Real-time architecture intelligence for {activeRepo.name}
              </span>
            ) : (
              'Select a repository to analyze architecture health'
            )}
          </p>
        </div>

        {isReposLoading ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
            <LoadingSpinner size="md" />
            <span className="text-[10px] text-[var(--color-text-tertiary)] font-bold uppercase tracking-widest font-mono">
              QUERYING WORKSPACE STATE...
            </span>
          </div>
        ) : !activeRepositoryId ? (
          <div className="border border-dashed border-[var(--color-border)] rounded-[var(--radius-2xl)] p-12 text-center max-w-md mx-auto my-12 bg-[var(--color-bg-surface)]/45 backdrop-blur-sm shadow-[var(--shadow-lg)]">
            <span className="text-3xl mb-3 inline-block">📁</span>
            <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-1">
              Select a Repository
            </h3>
            <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed mb-4">
              Switch or select a repository from the selector at the top bar to inspect its code intelligence layers.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-8 w-full">
            {/* ROW 1: Intelligence Score (7 cols) + Capability Radar (5 cols) */}
            <div className="grid grid-cols-12 gap-8">
              <div className="col-span-7">
                <ErrorBoundary>
                  <RepositoryHealthWidget repositoryId={activeRepositoryId} />
                </ErrorBoundary>
              </div>
              <div className="col-span-5">
                <ErrorBoundary>
                  <CapabilitySummaryWidget repositoryId={activeRepositoryId} />
                </ErrorBoundary>
              </div>
            </div>

            {/* ROW 2: Semantic Architecture Map (12 cols) */}
            <div className="grid grid-cols-12 gap-8">
              <div className="col-span-12">
                <ErrorBoundary>
                  <DependencyOverviewWidget capabilities={capabilities} isLoading={isCapsLoading} />
                </ErrorBoundary>
              </div>
            </div>

            {/* ROW 3: Risk Intelligence (6 cols) + Timeline (6 cols) */}
            <div className="grid grid-cols-12 gap-8">
              <div className="col-span-6">
                {/* Risk Intelligence - placeholder for now */}
                <div className="professional-card" style={{ height: '400px' }}>
                  <h3 className="text-section-header mb-4">Risk Intelligence</h3>
                  <p className="text-metadata text-gray-400">Coming soon...</p>
                </div>
              </div>
              <div className="col-span-6">
                <ErrorBoundary>
                  <RecentChangesWidget capabilities={capabilities} isLoading={isCapsLoading} />
                </ErrorBoundary>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
