'use client';

import React from 'react';
import { GitBranch, ShieldAlert, Cpu, Share2, HelpCircle, Network } from 'lucide-react';
import { useCapability, useCapabilityBlastRadius, useCapabilities } from '@/hooks/useCapabilities';
import { useUIStore } from '@/stores';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ScoreRing from '@/components/common/ScoreRing';
import { scoreToInt } from '@/lib/utils';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

interface DependenciesTabProps {
  capabilityId: string;
}

// Stage 2 Flow Types Ready
export interface FlowGraphNode {
  id: string;
  type: string;
  data: { label: React.ReactNode };
  position: { x: number; y: number };
  style?: React.CSSProperties;
}

export interface FlowGraphEdge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
  style?: React.CSSProperties;
  markerEnd?: any;
}

export default function DependenciesTab({ capabilityId }: DependenciesTabProps) {
  const repositoryId = useUIStore((s) => s.activeRepositoryId);
  const setSelectedCapabilityId = useUIStore((s) => s.setSelectedCapabilityId);

  const { data: capability, isLoading: isCapLoading } = useCapability(capabilityId);
  const { data: blastRadius, isLoading: isBlastLoading } = useCapabilityBlastRadius(capabilityId);
  const { data: allCapsData } = useCapabilities(repositoryId);

  const [isMounted, setIsMounted] = React.useState(false);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

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

  // Build nodes and edges when capability details change
  React.useEffect(() => {
    if (!capability || !isMounted) return;

    const centerVal = 200;
    const spacingY = 90;
    const newNodes: FlowGraphNode[] = [];
    const newEdges: FlowGraphEdge[] = [];

    // Central Node: Selected Capability
    newNodes.push({
      id: 'current-cap',
      type: 'default',
      data: {
        label: (
          <div className="px-4 py-2.5 rounded-lg bg-[#161a22]/95 border-2 border-[var(--color-primary)] shadow-[0_0_15px_rgba(79,124,255,0.25)] text-center relative overflow-hidden group">
            <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-info)]"></div>
            <div className="text-[8px] font-bold uppercase tracking-wider text-[var(--color-primary)] font-mono">Selected Node</div>
            <div className="font-bold text-sip-text-primary text-xs mt-1 truncate" title={capability.name}>{capability.name}</div>
            <div className="text-[8px] uppercase font-mono text-sip-text-tertiary mt-1.5 px-1.5 py-0.5 bg-[#090b10]/60 rounded border border-[var(--color-border)]/60 inline-block">
              {capability.capability_type}
            </div>
          </div>
        )
      },
      position: { x: 260, y: centerVal - 45 },
      style: { background: 'transparent', border: 'none', width: 200 }
    });

    // Left Nodes: Entities (Internal code dependencies)
    const entityList = capability.entities?.slice(0, 5) || [];
    const entityCount = entityList.length;
    entityList.forEach((entity, idx) => {
      const yPos = entityCount > 1 
        ? centerVal - ((entityCount - 1) * spacingY) / 2 + idx * spacingY
        : centerVal;
      
      newNodes.push({
        id: `entity-${idx}`,
        type: 'input',
        data: {
          label: (
            <div className="px-3 py-2 rounded border border-[var(--color-border)] bg-[#111318]/90 text-left w-full hover:border-[var(--color-primary)]/50 transition-colors shadow-sm">
              <div className="text-[8px] font-semibold uppercase tracking-wider text-sip-text-tertiary font-mono">Code Entity</div>
              <div className="font-mono text-[10px] text-sip-text-secondary truncate mt-0.5" title={entity}>
                {entity.split('.').pop() || entity}
              </div>
            </div>
          )
        },
        position: { x: 20, y: yPos - 25 },
        style: { background: 'transparent', border: 'none', width: 170 }
      });

      newEdges.push({
        id: `edge-entity-${idx}`,
        source: `entity-${idx}`,
        target: 'current-cap',
        animated: true,
        style: { stroke: 'rgba(79, 124, 255, 0.45)', strokeWidth: 1.5 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: 'rgba(79, 124, 255, 0.45)',
          size: 14
        }
      });
    });

    // Right Nodes: Impacted Capabilities
    const rightList = impactedCaps.slice(0, 5);
    const rightCount = rightList.length;
    rightList.forEach((cap, idx) => {
      const yPos = rightCount > 1
        ? centerVal - ((rightCount - 1) * spacingY) / 2 + idx * spacingY
        : centerVal;

      newNodes.push({
        id: `impacted-${cap.id}`,
        type: 'output',
        data: {
          label: (
            <div className="px-3 py-2 rounded border border-[#ef4444]/25 bg-[#ef4444]/5 text-left w-full hover:border-[#ef4444]/60 cursor-pointer transition-colors shadow-sm group">
              <div className="flex items-center justify-between">
                <span className="text-[8px] font-semibold uppercase tracking-wider text-[#ef4444]/80 font-mono">Impact Path</span>
                <span className="text-[7px] text-sip-text-muted opacity-0 group-hover:opacity-100 transition-opacity font-mono">Click to view</span>
              </div>
              <div className="font-semibold text-sip-text-primary text-[10px] truncate mt-0.5" title={cap.name}>{cap.name}</div>
              <div className="text-[7px] uppercase font-mono text-sip-text-secondary mt-0.5">{cap.type}</div>
            </div>
          )
        },
        position: { x: 510, y: yPos - 25 },
        style: { background: 'transparent', border: 'none', width: 170 }
      });

      newEdges.push({
        id: `edge-impacted-${cap.id}`,
        source: 'current-cap',
        target: `impacted-${cap.id}`,
        animated: true,
        style: { stroke: 'rgba(239, 68, 68, 0.45)', strokeWidth: 1.5 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: 'rgba(239, 68, 68, 0.45)',
          size: 14
        }
      });
    });

    // Bottom Nodes: External relationships / integrations
    const relList = capability.relationships?.slice(0, 3) || [];
    const relCount = relList.length;
    relList.forEach((rel, idx) => {
      const xPos = relCount > 1
        ? 360 - ((relCount - 1) * 190) / 2 + idx * 190
        : 260;
      
      newNodes.push({
        id: `rel-${idx}`,
        type: 'default',
        data: {
          label: (
            <div className="px-3 py-2 rounded border border-[#06b6d4]/20 bg-[#06b6d4]/5 text-left w-full hover:border-[#06b6d4]/50 transition-colors shadow-sm">
              <div className="text-[8px] font-semibold uppercase tracking-wider text-[#06b6d4] font-mono font-bold">API / Dep</div>
              <div className="font-mono text-[10px] text-sip-text-secondary truncate mt-0.5" title={rel}>
                {rel}
              </div>
            </div>
          )
        },
        position: { x: xPos, y: centerVal + 115 },
        style: { background: 'transparent', border: 'none', width: 160 }
      });

      newEdges.push({
        id: `edge-rel-${idx}`,
        source: 'current-cap',
        target: `rel-${idx}`,
        style: { stroke: 'rgba(6, 182, 212, 0.4)', strokeWidth: 1.2, strokeDasharray: '4 4' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: 'rgba(6, 182, 212, 0.4)',
          size: 12
        }
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [capability, impactedCaps, isMounted, setNodes, setEdges]);

  // Navigate to selecting the clicked node if it's an impacted capability
  const onNodeClick = React.useCallback((event: React.MouseEvent, node: any) => {
    if (node.id.startsWith('impacted-')) {
      const targetId = node.id.replace('impacted-', '');
      setSelectedCapabilityId(targetId);
    }
  }, [setSelectedCapabilityId]);

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
      {/* Visualizer header status */}
      <div className="bg-[#4f7cff]/5 border border-[#4f7cff]/15 rounded-lg p-3 text-[11px] text-sip-text-secondary flex items-center justify-between">
        <span className="flex items-center gap-1.5"><Network className="w-3.5 h-3.5 text-[var(--color-primary)]" /> Interactive blast-radius node graph. Click downstream red nodes to traverse the graph.</span>
        <span className="font-mono text-[9px] uppercase tracking-wider text-[var(--color-primary)] font-bold px-1.5 py-0.5 bg-[#4f7cff]/10 rounded">Graph Interactive</span>
      </div>

      {/* Blast Radius Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Score Card */}
        <div className="glass-card glow-hover p-5 flex flex-col items-center justify-center text-center gap-3">
          <ScoreRing
            score={blastRadius ? scoreToInt(blastRadius.blast_radius_score) : 0}
            size={72}
            strokeWidth={5}
            label="Blast Radius"
          />
          <div className="flex flex-col">
            <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider font-mono">
              Blast Radius Score
            </span>
            <span className="text-xs text-sip-text-secondary mt-0.5">
              Impact of failure or refactoring
            </span>
          </div>
        </div>

        {/* Depth & Count Card */}
        <div className="glass-card glow-hover p-5 flex flex-col justify-center gap-4 col-span-2">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col">
              <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider font-mono">
                Max Impact Depth
              </span>
              <span className="text-2xl font-extrabold text-gradient-brand font-mono mt-1">
                {blastRadius ? blastRadius.impact_depth : 0}
              </span>
              <span className="text-[10px] text-sip-text-muted mt-0.5">
                levels of downstream dependencies
              </span>
            </div>

            <div className="flex flex-col">
              <span className="text-[10px] text-sip-text-tertiary font-bold uppercase tracking-wider font-mono">
                Impacted Nodes
              </span>
              <span className="text-2xl font-extrabold text-gradient-success font-mono mt-1">
                {blastRadius ? blastRadius.impacted_capability_ids.length : 0}
              </span>
              <span className="text-[10px] text-sip-text-muted mt-0.5">
                downstream capabilities
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* REACT FLOW GRAPH INTERACTIVE */}
      <div className="h-[400px] w-full rounded-xl border border-[var(--color-border)]/60 bg-[#090b10]/45 overflow-hidden relative group/graph">
        {isMounted ? (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            fitViewOptions={{ padding: 0.15 }}
            attributionPosition="bottom-right"
            minZoom={0.3}
            maxZoom={1.5}
            zoomOnScroll={false}
            panOnDrag={true}
            preventScrolling={true}
          >
            <Background color="var(--color-border)" gap={16} size={1} variant={BackgroundVariant.Dots} />
            <Controls showInteractive={false} />
          </ReactFlow>
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-2 bg-[#090b10]/20">
            <LoadingSpinner size="md" />
            <span className="text-xs text-sip-text-secondary font-mono uppercase tracking-wider">Initializing Graph Canvas...</span>
          </div>
        )}
        <div className="absolute top-3 right-3 bg-[#111318]/90 border border-[var(--color-border)]/80 px-2 py-1 rounded text-[9px] font-mono text-sip-text-secondary flex gap-2 pointer-events-none select-none">
          <span>↕ Drag to pan</span>
          <span>🖱 Scroll to zoom</span>
        </div>
      </div>

      {/* Downstream Impact List */}
      <div className="glass-card p-5">
        <h4 className="text-xs font-bold text-sip-text-primary uppercase tracking-wider mb-3 font-mono">
          Impacted Downstream Capabilities Detailed
        </h4>
        {impactedCaps.length > 0 ? (
          <div className="flex flex-wrap gap-2 max-h-[120px] overflow-y-auto">
            {impactedCaps.map((cap) => (
              <button
                key={cap.id}
                onClick={() => setSelectedCapabilityId(cap.id)}
                className="flex items-center gap-1.5 px-2.5 py-1 text-xs bg-sip-surface hover:bg-[#161a22] border border-[var(--color-border)]/60 hover:border-[var(--color-primary)]/50 rounded text-sip-text-secondary transition-all cursor-pointer text-left"
              >
                <GitBranch className="w-3.5 h-3.5 text-sip-text-tertiary" />
                <span className="font-semibold text-sip-text-primary">{cap.name}</span>
                <span className="text-[9px] uppercase font-mono text-sip-text-muted">
                  ({cap.type})
                </span>
              </button>
            ))}
          </div>
        ) : (
          <span className="text-xs text-sip-text-muted italic">No downstream capabilities impacted. Isolation is clean.</span>
        )}
      </div>

      {/* Contracts / Code Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Internal Entities */}
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 mb-3 border-b border-[var(--color-border)]/40 pb-2">
            <Cpu className="w-4 h-4 text-sip-text-tertiary" />
            <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider font-mono">
              Internal Entity Dependencies ({capability.entities?.length || 0})
            </span>
          </div>
          <div className="flex flex-col gap-1.5 max-h-[160px] overflow-y-auto pr-1">
            {capability.entities?.length > 0 ? (
              capability.entities.map((ent) => (
                <span
                  key={ent}
                  className="px-2.5 py-1.5 text-xs font-mono bg-sip-surface/60 border border-[var(--color-border)]/40 rounded text-sip-text-secondary truncate"
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
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 mb-3 border-b border-[var(--color-border)]/40 pb-2">
            <Share2 className="w-4 h-4 text-sip-text-tertiary" />
            <span className="text-xs font-bold text-sip-text-primary uppercase tracking-wider font-mono">
              External Relationships ({capability.relationships?.length || 0})
            </span>
          </div>
          <div className="flex flex-col gap-1.5 max-h-[160px] overflow-y-auto pr-1">
            {capability.relationships?.length > 0 ? (
              capability.relationships.map((rel) => (
                <span
                  key={rel}
                  className="px-2.5 py-1.5 text-xs font-mono bg-sip-surface/60 border border-[var(--color-border)]/40 rounded text-sip-text-secondary truncate"
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

