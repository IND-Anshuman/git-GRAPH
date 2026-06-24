'use client';

import React from 'react';
import { Terminal, ShieldCheck, Activity } from 'lucide-react';
import { useCapability } from '@/hooks/useCapabilities';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface BehaviorsTabProps {
  capabilityId: string;
}

export default function BehaviorsTab({ capabilityId }: BehaviorsTabProps) {
  const { data: capability, isLoading, isError } = useCapability(capabilityId);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
        <LoadingSpinner size="md" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Querying Behavior Engines...
        </span>
      </div>
    );
  }

  if (isError || !capability) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <span className="text-xl mb-2">⚠️</span>
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          Behavior Offline
        </h4>
        <p className="text-xs text-sip-text-secondary">
          Could not retrieve behavioral telemetry.
        </p>
      </div>
    );
  }

  const behaviors = capability.behaviors || [];

  if (behaviors.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-[var(--color-border)] bg-sip-surface/10 rounded-lg">
        <Terminal className="w-8 h-8 text-sip-text-tertiary mb-2" />
        <h4 className="text-xs font-semibold text-sip-text-primary">No Behaviors Registered</h4>
        <p className="text-[11px] text-sip-text-secondary mt-1 max-w-[240px]">
          No functional code behaviors or state mutations are registered under this capability.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-1 animate-fade-in">
      <div className="flex items-center gap-2 px-3 py-2 bg-[#161A22]/30 border border-[var(--color-border)] rounded-md mb-2">
        <ShieldCheck className="w-4 h-4 text-sip-text-tertiary" />
        <span className="text-[10px] uppercase font-mono text-sip-text-secondary tracking-wider">
          Total Mapped State Mutations: {behaviors.length}
        </span>
      </div>

      <div className="flex flex-col gap-2.5">
        {behaviors.map((behavior, idx) => {
          // Parse namespaces if behavior has syntax like 'auth:session:create'
          const parts = behavior.split(':');
          const isNamespaced = parts.length > 1;
          const displayNamespace = isNamespaced ? parts.slice(0, -1).join(' / ') : 'global';
          const displayName = isNamespaced ? parts[parts.length - 1] : behavior;

          return (
            <div
              key={idx}
              className="bg-sip-surface/30 border border-[var(--color-border)] rounded-lg p-3.5 flex items-start gap-3"
            >
              <div className="p-1.5 bg-[#161A22] text-sip-text-tertiary rounded shrink-0">
                <Activity size={13} className="text-[var(--color-primary)]" />
              </div>
              <div className="flex-1 min-w-0 flex flex-col gap-0.5">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-xs font-bold text-sip-text-primary font-mono truncate">
                    {displayName}
                  </span>
                  <span className="text-[9px] font-mono text-sip-text-muted shrink-0 bg-sip-surface border border-[var(--color-border)]/55 px-1.5 rounded uppercase">
                    {displayNamespace}
                  </span>
                </div>
                <p className="text-[11px] text-sip-text-secondary leading-relaxed mt-1">
                  Executes state changes and functional actions corresponding to behavior: <code className="text-sip-text-muted">{behavior}</code>.
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
