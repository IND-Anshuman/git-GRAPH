'use client';

import React from 'react';
import AppShell from '@/components/layout/AppShell';
import { CapabilityNavigator } from '@/features/capabilities/CapabilityNavigator';
import { CapabilityDetail } from '@/features/capabilities/CapabilityDetail';
import ErrorBoundary from '@/components/common/ErrorBoundary';

export default function CapabilitiesPage() {
  return (
    <AppShell>
      <div
        className="flex w-full overflow-hidden"
        style={{
          height: 'calc(100vh - var(--topbar-height))',
          ['--navigator-width' as any]: '320px', // set navigator width variable consumed by CapabilityNavigator
        }}
      >
        {/* Left Panel: Capability Navigator */}
        <div className="shrink-0 h-full overflow-hidden">
          <ErrorBoundary>
            <CapabilityNavigator />
          </ErrorBoundary>
        </div>

        {/* Right Panel: Detail Panel */}
        <div className="flex-1 h-full overflow-hidden">
          <ErrorBoundary>
            <CapabilityDetail />
          </ErrorBoundary>
        </div>
      </div>
    </AppShell>
  );
}
