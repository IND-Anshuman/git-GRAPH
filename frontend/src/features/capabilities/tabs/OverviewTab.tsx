'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Layers, Box, Terminal, Route, Calendar } from 'lucide-react';
import { useCapability } from '@/hooks/useCapabilities';
import ScoreRing from '@/components/common/ScoreRing';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { scoreToInt, formatDate } from '@/lib/utils';

interface OverviewTabProps {
  capabilityId: string;
}

export default function OverviewTab({ capabilityId }: OverviewTabProps) {
  const { data: capability, isLoading, isError } = useCapability(capabilityId);
  const [conceptsExpanded, setConceptsExpanded] = useState(true);
  const [behaviorsExpanded, setBehaviorsExpanded] = useState(true);
  const [entitiesExpanded, setEntitiesExpanded] = useState(false);
  const [flowsExpanded, setFlowsExpanded] = useState(false);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
        <LoadingSpinner size="md" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Querying Capability Layer...
        </span>
      </div>
    );
  }

  if (isError || !capability) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <span className="text-xl mb-2">⚠️</span>
        <h4 className="text-sm font-semibold text-sip-text-primary mb-1">
          Resolution Error
        </h4>
        <p className="text-xs text-sip-text-secondary max-w-sm">
          Failed to fetch detailed profile for this capability.
        </p>
      </div>
    );
  }

  const calculatedHealth = capability.health_score ?? 
    Math.round(((capability.maturity_score + capability.coverage_score + (1 - capability.risk_score)) / 3) * 100);

  return (
    <div className="flex flex-col gap-6 p-1 animate-fade-in">
      {/* Description Card */}
      <div className="glass-card glow-hover p-5">
        <h4 className="text-xs font-semibold text-sip-text-tertiary uppercase tracking-wider mb-2">
          Description
        </h4>
        <p className="text-sm text-sip-text-primary leading-relaxed">
          {capability.description || 'No conceptual description provided for this capability.'}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card glow-hover p-4 flex flex-col items-center justify-center text-center gap-2">
          <ScoreRing score={scoreToInt(capability.maturity_score)} size={60} strokeWidth={4} label="Maturity" />
          <span className="text-xs font-semibold text-sip-text-secondary">Maturity Score</span>
        </div>
        <div className="glass-card glow-hover p-4 flex flex-col items-center justify-center text-center gap-2">
          <ScoreRing score={scoreToInt(capability.risk_score)} size={60} strokeWidth={4} label="Risk" />
          <span className="text-xs font-semibold text-sip-text-secondary">Risk Score</span>
        </div>
        <div className="glass-card glow-hover p-4 flex flex-col items-center justify-center text-center gap-2">
          <ScoreRing score={scoreToInt(capability.coverage_score)} size={60} strokeWidth={4} label="Coverage" />
          <span className="text-xs font-semibold text-sip-text-secondary">Code Coverage</span>
        </div>
        <div className="glass-card glow-hover p-4 flex flex-col items-center justify-center text-center gap-2">
          <ScoreRing score={scoreToInt(capability.confidence)} size={60} strokeWidth={4} label="Confidence" />
          <span className="text-xs font-semibold text-sip-text-secondary">Model Confidence</span>
        </div>
      </div>

      {/* Expandable Sections */}
      <div className="flex flex-col gap-4">
        {/* Concepts */}
        <div className="border border-[var(--color-border)]/60 rounded-lg glass-card bg-opacity-10 backdrop-blur-sm">
          <button
            onClick={() => setConceptsExpanded(!conceptsExpanded)}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-sip-surface/40 transition-colors rounded-t-lg"
          >
            <div className="flex items-center gap-2">
              <Box className="w-4 h-4 text-[var(--color-primary)]" />
              <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider">
                Related Concepts ({capability.concepts?.length || 0})
              </span>
            </div>
            {conceptsExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {conceptsExpanded && (
            <div className="p-4 border-t border-[var(--color-border)] flex flex-wrap gap-2">
              {capability.concepts?.length > 0 ? (
                capability.concepts.map((concept) => (
                  <span
                    key={concept}
                    className="px-2.5 py-1 text-xs bg-sip-surface border border-[var(--color-border)] rounded text-sip-text-secondary"
                  >
                    {concept}
                  </span>
                ))
              ) : (
                <span className="text-xs text-sip-text-muted italic">No associated domain concepts.</span>
              )}
            </div>
          )}
        </div>

        {/* Behaviors */}
        <div className="border border-[var(--color-border)]/60 rounded-lg glass-card bg-opacity-10 backdrop-blur-sm">
          <button
            onClick={() => setBehaviorsExpanded(!behaviorsExpanded)}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-sip-surface/40 transition-colors rounded-t-lg"
          >
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[var(--color-primary)]" />
              <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider">
                Related Behaviors ({capability.behaviors?.length || 0})
              </span>
            </div>
            {behaviorsExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {behaviorsExpanded && (
            <div className="p-4 border-t border-[var(--color-border)] flex flex-wrap gap-2">
              {capability.behaviors?.length > 0 ? (
                capability.behaviors.map((behavior) => (
                  <span
                    key={behavior}
                    className="px-2.5 py-1 text-xs bg-sip-surface border border-[var(--color-border)] rounded text-sip-text-secondary font-mono"
                  >
                    {behavior}
                  </span>
                ))
              ) : (
                <span className="text-xs text-sip-text-muted italic">No associated functional behaviors.</span>
              )}
            </div>
          )}
        </div>

        {/* Entities */}
        <div className="border border-[var(--color-border)]/60 rounded-lg glass-card bg-opacity-10 backdrop-blur-sm">
          <button
            onClick={() => setEntitiesExpanded(!entitiesExpanded)}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-sip-surface/40 transition-colors rounded-t-lg"
          >
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-[var(--color-primary)]" />
              <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider">
                Code Entities ({capability.entities?.length || 0})
              </span>
            </div>
            {entitiesExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {entitiesExpanded && (
            <div className="p-4 border-t border-[var(--color-border)] flex flex-col gap-1">
              {capability.entities?.length > 0 ? (
                capability.entities.map((entity) => (
                  <div
                    key={entity}
                    className="px-3 py-2 text-xs font-mono bg-sip-surface/40 border border-[var(--color-border)]/40 rounded flex items-center justify-between"
                  >
                    <span className="text-sip-text-secondary truncate pr-3">{entity}</span>
                    <span className="text-[10px] text-sip-text-muted">Entity</span>
                  </div>
                ))
              ) : (
                <span className="text-xs text-sip-text-muted italic">No mapped code classes or files.</span>
              )}
            </div>
          )}
        </div>

        {/* Flows */}
        <div className="border border-[var(--color-border)]/60 rounded-lg glass-card bg-opacity-10 backdrop-blur-sm">
          <button
            onClick={() => setFlowsExpanded(!flowsExpanded)}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-sip-surface/40 transition-colors rounded-t-lg"
          >
            <div className="flex items-center gap-2">
              <Route className="w-4 h-4 text-[var(--color-primary)]" />
              <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider">
                Logical Flows ({capability.flows?.length || 0})
              </span>
            </div>
            {flowsExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {flowsExpanded && (
            <div className="p-4 border-t border-[var(--color-border)] flex flex-col gap-1">
              {capability.flows?.length > 0 ? (
                capability.flows.map((flow) => (
                  <div
                    key={flow}
                    className="px-3 py-2 text-xs font-mono bg-sip-surface/40 border border-[var(--color-border)]/40 rounded text-sip-text-secondary"
                  >
                    {flow}
                  </div>
                ))
              ) : (
                <span className="text-xs text-sip-text-muted italic">No mapped execution flows.</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Metadata Panel */}
      <div className="glass-card p-4 flex flex-wrap gap-x-8 gap-y-3 text-xs text-sip-text-secondary">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-sip-text-tertiary" />
          <span>Discovered on: {formatDate(capability.created_at)}</span>
        </div>
        <div className="flex items-center gap-2">
          <Box className="w-4 h-4 text-sip-text-tertiary" />
          <span>Type: <strong className="text-sip-text-primary">{capability.capability_type}</strong></span>
        </div>
      </div>
    </div>
  );
}
