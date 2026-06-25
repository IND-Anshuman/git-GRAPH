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
        className="max-w-[1600px] mx-auto w-full h-[calc(100vh-var(--topbar-height))] px-6 sm:px-8 py-6 flex gap-6 overflow-hidden"
        style={{
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
