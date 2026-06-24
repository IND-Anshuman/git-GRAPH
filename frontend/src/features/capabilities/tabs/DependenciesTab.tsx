'use client';

import React from 'react';
import { GitBranch, ShieldAlert, Cpu, Share2, HelpCircle } from 'lucide-react';
import { useCapability, useCapabilityBlastRadius, useCapabilities } from '@/hooks/useCapabilities';
import { useUIStore } from '@/stores';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ScoreRing from '@/components/common/ScoreRing';
import { scoreToInt } from '@/lib/utils';

interface DependenciesTabProps {
  capabilityId: string;
}

// Stage 2 Flow Types Ready
export interface FlowGraphNode {
  id: string;
  type: 'capability' | 'entity' | 'external';
  data: { label: string; score?: number };
  position: { x: number; y: number };
}

export interface FlowGraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated?: boolean;
}

export default function DependenciesTab({ capabilityId }: DependenciesTabProps) {
  const repositoryId = useUIStore((s) => s.activeRepositoryId);

  const { data: capability, isLoading: isCapLoading } = useCapability(capabilityId);
  const { data: blastRadius, isLoading: isBlastLoading, isError: isBlastError } = useCapabilityBlastRadius(capabilityId);
  const { data: allCapsData } = useCapabilities(repositoryId);

  const allCapabilities = React.useMemo(() => {
    return allCapsData ?? [];
  }, [allCapsData]);

  const isLoading = isCapLoading || isBlastLoading;

  // Map impacted IDs to capability names
  const impactedCaps = React.useMemo(() => {
    if (!blastRadius || !allCapabilities) return [];
    return blastRadius.impacted_capability_ids.map((id) => {
      const found = allCapabilities.find((c) => c.id === id);
      return {
        id,
        name: found ? found.name : `capability-${id.slice(0, 6)}`,
        type: found ? found.capability_type : 'UNKNOWN',
      };
    });
  }, [blastRadius, allCapabilities]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
        <LoadingSpinner size="md" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Mapping Blast Radius...
        </span>
      </div>
    );
  }

  if (!capability) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <span className="text-xl mb-2">⚠️</span>
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          Capability Offline
        </h4>
        <p className="text-xs text-sip-text-secondary">
          Could not retrieve dependency profile.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-1 animate-fade-in">
      {/* Stage 2 Info Notice */}
      <div className="bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/20 rounded-lg p-3 text-[11px] text-sip-text-secondary flex items-center justify-between">
        <span>🕸️ Interactive React Flow visualizer coming in Stage 2.</span>
        <span className="font-mono text-sip-text-muted">STAGE 1 COMPLIANT</span>
      </div>

      {/* Blast Radius Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Score Card */}
        <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5 flex flex-col items-center justify-center text-center gap-3">
          <ScoreRing
            score={blastRadius ? scoreToInt(blastRadius.blast_radius_score) : 0}
            size={72}
            strokeWidth={5}
            label="Blast Radius"
          />
          <div className="flex flex-col">
            <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider">
              Blast Radius Score
            </span>
            <span className="text-xs text-sip-text-secondary mt-0.5">
              Impact of failure or refactoring
            </span>
          </div>
        </div>

        {/* Depth & Count Card */}
        <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5 flex flex-col justify-center gap-4 col-span-2">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col">
              <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider">
                Max Impact Depth
              </span>
              <span className="text-2xl font-extrabold text-sip-text-primary font-mono mt-1">
                {blastRadius ? blastRadius.impact_depth : 0}
              </span>
              <span className="text-[10px] text-sip-text-muted">
                levels of downstream dependencies
              </span>
            </div>

            <div className="flex flex-col">
              <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider">
                Impacted Nodes
              </span>
              <span className="text-2xl font-extrabold text-sip-text-primary font-mono mt-1">
                {blastRadius ? blastRadius.impacted_capability_ids.length : 0}
              </span>
              <span className="text-[10px] text-sip-text-muted">
                downstream capabilities
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Downstream Impact List */}
      <div className="bg-sip-surface/40 border border-[var(--color-border)] rounded-lg p-5">
        <h4 className="text-xs font-bold text-sip-text-primary uppercase tracking-wider mb-3">
          Impacted Downstream Capabilities
        </h4>
        {impactedCaps.length > 0 ? (
          <div className="flex flex-wrap gap-2 max-h-[120px] overflow-y-auto">
            {impactedCaps.map((cap) => (
              <div
                key={cap.id}
                className="flex items-center gap-1.5 px-2.5 py-1 text-xs bg-sip-surface border border-[var(--color-border)]/60 rounded text-sip-text-secondary"
              >
                <GitBranch className="w-3.5 h-3.5 text-sip-text-tertiary" />
                <span className="font-semibold text-sip-text-primary">{cap.name}</span>
                <span className="text-[9px] uppercase font-mono text-sip-text-muted">
                  ({cap.type})
                </span>
              </div>
            ))}
          </div>
        ) : (
          <span className="text-xs text-sip-text-muted italic">No downstream capabilities impacted. Isolation is clean.</span>
        )}
      </div>

      {/* Contracts / Code Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Internal Entities */}
        <div className="bg-sip-surface/20 border border-[var(--color-border)] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 border-b border-[var(--color-border)]/40 pb-2">
            <Cpu className="w-4 h-4 text-sip-text-tertiary" />
            <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider">
              Internal Entity Dependencies ({capability.entities?.length || 0})
            </span>
          </div>
          <div className="flex flex-col gap-1.5 max-h-[160px] overflow-y-auto pr-1">
            {capability.entities?.length > 0 ? (
              capability.entities.map((ent) => (
                <span
                  key={ent}
                  className="px-2 py-1.5 text-xs font-mono bg-sip-surface/60 border border-[var(--color-border)]/40 rounded text-sip-text-secondary truncate"
                >
                  {ent}
                </span>
              ))
            ) : (
              <span className="text-xs text-sip-text-muted italic">No code entities mapped.</span>
            )}
          </div>
        </div>

        {/* External Relationships */}
        <div className="bg-sip-surface/20 border border-[var(--color-border)] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 border-b border-[var(--color-border)]/40 pb-2">
            <Share2 className="w-4 h-4 text-sip-text-tertiary" />
            <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider">
              External Relationships ({capability.relationships?.length || 0})
            </span>
          </div>
          <div className="flex flex-col gap-1.5 max-h-[160px] overflow-y-auto pr-1">
            {capability.relationships?.length > 0 ? (
              capability.relationships.map((rel) => (
                <span
                  key={rel}
                  className="px-2 py-1.5 text-xs font-mono bg-sip-surface/60 border border-[var(--color-border)]/40 rounded text-sip-text-secondary truncate"
                >
                  {rel}
                </span>
              ))
            ) : (
              <span className="text-xs text-sip-text-muted italic">No external relationships mapped.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
