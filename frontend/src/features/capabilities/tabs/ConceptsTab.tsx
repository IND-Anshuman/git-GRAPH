'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Box, ChevronDown, ChevronUp, Cpu, Award } from 'lucide-react';
import { useCapability } from '@/hooks/useCapabilities';
import { conceptsApi } from '@/services/api/endpoints';
import { queryKeys } from '@/lib/query-keys';
import { useUIStore } from '@/stores';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ScoreRing from '@/components/common/ScoreRing';
import { scoreToInt } from '@/lib/utils';

interface ConceptsTabProps {
  capabilityId: string;
}

export default function ConceptsTab({ capabilityId }: ConceptsTabProps) {
  const repositoryId = useUIStore((s) => s.activeRepositoryId);
  const { data: capability, isLoading: isCapLoading } = useCapability(capabilityId);

  // Fetch all repository concepts to cross-reference full metadata
  const { data: allConcepts = [], isLoading: isConceptsLoading } = useQuery({
    queryKey: queryKeys.concepts.byRepo(repositoryId ?? ''),
    queryFn: () => conceptsApi.listByRepository(repositoryId!),
    enabled: !!repositoryId,
  });

  const [expandedConceptIds, setExpandedConceptIds] = useState<Record<string, boolean>>({});

  const isLoading = isCapLoading || isConceptsLoading;

  const toggleExpand = (id: string) => {
    setExpandedConceptIds((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const capabilityConcepts = React.useMemo(() => {
    if (!capability || !capability.concepts) return [];

    return capability.concepts.map((name) => {
      // Find full concept metadata if available
      const fullConcept = allConcepts.find(
        (c) => c.name.toLowerCase() === name.toLowerCase() || c.id === name
      );

      return {
        id: fullConcept?.id || name,
        name: fullConcept?.name || name,
        description: fullConcept?.description || 'No detailed domain definition resolved for this concept.',
        concept_type: fullConcept?.concept_type || 'Domain Domain Domain',
        version: fullConcept?.version || '1.0.0',
        health_score: fullConcept?.health_score ?? null,
      };
    });
  }, [capability, allConcepts]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 gap-3 min-h-[300px]">
        <LoadingSpinner size="md" />
        <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">
          Compiling Concept Layer...
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
          Could not retrieve capability concepts.
        </p>
      </div>
    );
  }

  if (capabilityConcepts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-[var(--color-border)] bg-sip-surface/10 rounded-lg">
        <Box className="w-8 h-8 text-sip-text-tertiary mb-2" />
        <h4 className="text-xs font-semibold text-sip-text-primary">No Concepts Ingested</h4>
        <p className="text-[11px] text-sip-text-secondary mt-1 max-w-[240px]">
          There are no domain abstraction definitions mapped to this capability.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-1 animate-fade-in">
      {capabilityConcepts.map((concept) => {
        const isExpanded = !!expandedConceptIds[concept.id];
        return (
          <div
            key={concept.id}
            className="border border-[var(--color-border)] rounded-lg bg-sip-surface/30 overflow-hidden"
          >
            {/* Concept Header */}
            <button
              type="button"
              onClick={() => toggleExpand(concept.id)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-sip-surface/60 transition-colors text-left"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="p-1.5 bg-[var(--color-primary-muted)] text-[var(--color-primary)] rounded">
                  <Cpu size={14} />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-bold text-sip-text-primary truncate">
                    {concept.name}
                  </span>
                  <span className="text-[9px] uppercase tracking-wider text-sip-text-muted mt-0.5">
                    {concept.concept_type}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                {concept.health_score !== null && (
                  <div className="flex items-center gap-1.5 bg-[#161A22] px-2 py-0.5 rounded border border-[var(--color-border)]/40 text-[10px] text-sip-text-secondary font-mono">
                    <Award size={10} className="text-sip-text-tertiary" />
                    <span>Health: {scoreToInt(concept.health_score)}</span>
                  </div>
                )}
                {isExpanded ? <ChevronUp size={14} className="text-sip-text-tertiary" /> : <ChevronDown size={14} className="text-sip-text-tertiary" />}
              </div>
            </button>

            {/* Concept Details */}
            {isExpanded && (
              <div className="px-4 pb-4 pt-3 border-t border-[var(--color-border)]/40 bg-[#161A22]/20 flex flex-col gap-3 text-xs">
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-sip-text-tertiary">
                    Semantic Abstraction
                  </span>
                  <p className="text-sip-text-secondary leading-relaxed">
                    {concept.description}
                  </p>
                </div>
                <div className="flex justify-between items-center text-[10px] text-sip-text-muted font-mono pt-2 border-t border-[var(--color-border)]/20">
                  <span>Version: {concept.version}</span>
                  <span>ID: {concept.id}</span>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
