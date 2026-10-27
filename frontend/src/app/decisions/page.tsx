"use client";

/**
 * /decisions — Decision Registry.
 *
 * Wires to `decisionsApi` (formerly an empty stub). Shows:
 *  - Portfolio summary (total / by-type / by-status)
 *  - Active decisions list
 *  - Detected intents
 *  - Cross-repo decision graph
 *
 * The decisions/intents are the "why it evolved" story of the codebase.
 */
import * as Tabs from "@radix-ui/react-tabs";
import { GitFork, Network, Sparkles } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import AppShell from "@/components/layout/AppShell";
import { useUIStore } from "@/stores";
import { decisionsApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { CACHE } from "@/lib/constants";
import {
  Card,
  Stack,
  Text,
  Section,
  Skeleton,
  ErrorState,
  EmptyState,
  StatusBadge,
  MetricTile,
} from "@/components/ui";
import type {
  DecisionSummary,
  Intent,
  Decision,
  DecisionGraph,
} from "@/types/platform";

function useDecisionsData(repositoryId: string | null) {
  const summary = useQuery({
    queryKey: queryKeys.decisions.summary(repositoryId!),
    queryFn: () => decisionsApi.getSummary(repositoryId!),
    enabled: !!repositoryId,
    staleTime: CACHE.ARCHITECTURE,
  });
  const active = useQuery({
    queryKey: queryKeys.decisions.active(repositoryId!),
    queryFn: () => decisionsApi.getActive(repositoryId!),
    enabled: !!repositoryId,
    staleTime: CACHE.ARCHITECTURE,
  });
  const intents = useQuery({
    queryKey: queryKeys.decisions.intents(repositoryId!),
    queryFn: () => decisionsApi.listIntents(repositoryId!),
    enabled: !!repositoryId,
    staleTime: CACHE.ARCHITECTURE,
  });
  const graph = useQuery({
    queryKey: queryKeys.decisions.graph(repositoryId!),
    queryFn: () => decisionsApi.getGraph(repositoryId!),
    enabled: !!repositoryId,
    staleTime: CACHE.ARCHITECTURE,
  });
  return { summary, active, intents, graph };
}

export default function DecisionsPage() {
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);
  const { summary, active, intents, graph } = useDecisionsData(activeRepositoryId);

  if (!activeRepositoryId) {
    return (
      <AppShell>
        <EmptyState
          icon={<GitFork size={20} />}
          title="Select a repository"
          description="The Decision Registry is computed per-repository. Pick one from the top bar."
        />
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="px-12 py-8 max-w-[1600px] mx-auto flex flex-col gap-8 w-full">
        <Section
          eyebrow="Why it evolved"
          title="Decision Registry"
          description="Architectural decisions, inferred intents, and the causal chains between them."
        />

        {summary.isLoading || active.isLoading ? (
          <Stack direction="vertical" gap={4}>
            <Skeleton shape="block" height={120} />
            <Skeleton shape="block" height={320} />
          </Stack>
        ) : summary.isError ? (
          <ErrorState
            title="Failed to load decisions"
            description="The backend did not return a decision summary."
            onRetry={() => summary.refetch()}
          />
        ) : (
          <Stack direction="vertical" gap={6}>
            <SummaryRow summary={summary.data} />
            <Tabs.Root defaultValue="active">
              <Tabs.List className="flex gap-1 border-b border-[var(--color-border)] mb-4">
                <TabsTrigger value="active">
                  Active ({active.data?.length ?? 0})
                </TabsTrigger>
                <TabsTrigger value="intents">
                  Intents ({intents.data?.length ?? 0})
                </TabsTrigger>
                <TabsTrigger value="graph">Graph</TabsTrigger>
              </Tabs.List>
              <Tabs.Content value="active">
                <ActiveList
                  decisions={active.data ?? []}
                  isLoading={active.isLoading}
                  isError={active.isError}
                />
              </Tabs.Content>
              <Tabs.Content value="intents">
                <IntentsList
                  intents={intents.data ?? []}
                  isLoading={intents.isLoading}
                  isError={intents.isError}
                />
              </Tabs.Content>
              <Tabs.Content value="graph">
                <GraphView
                  graph={graph.data ?? null}
                  isLoading={graph.isLoading}
                  isError={graph.isError}
                />
              </Tabs.Content>
            </Tabs.Root>
          </Stack>
        )}
      </div>
    </AppShell>
  );
}

function TabsTrigger({ value, children }: { value: string; children: React.ReactNode }) {
  return (
    <Tabs.Trigger
      value={value}
      className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] data-[state=active]:text-[var(--color-primary)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--color-primary)] outline-none transition-colors hover:text-[var(--color-text-primary)]"
    >
      {children}
    </Tabs.Trigger>
  );
}

function SummaryRow({ summary }: { summary: DecisionSummary | undefined }) {
  if (!summary) return null;
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricTile
        label="Total decisions"
        value={summary.total_decisions}
        icon={GitFork}
      />
      <MetricTile
        label="Inferred intents"
        value={summary.total_intents}
        icon={Sparkles}
      />
      <MetricTile
        label="Active"
        value={summary.by_status?.ACTIVE ?? summary.by_status?.active ?? 0}
      />
      <MetricTile
        label="Decision types"
        value={Object.keys(summary.by_type ?? {}).length}
        icon={Network}
      />
    </div>
  );
}

function ActiveList({
  decisions,
  isLoading,
  isError,
}: {
  decisions: Decision[];
  isLoading: boolean;
  isError: boolean;
}) {
  if (isLoading) return <Skeleton shape="block" height={240} />;
  if (isError) {
    return (
      <ErrorState
        title="Failed to load active decisions"
        description="The backend did not return the decision list."
      />
    );
  }
  if (decisions.length === 0) {
    return (
      <EmptyState
        icon={<GitFork size={20} />}
        title="No active decisions"
        description="No active architectural decisions detected for this repository yet."
      />
    );
  }
  return (
    <Stack direction="vertical" gap={3}>
      {decisions.map((d) => (
        <Card key={d.id} padded>
          <Stack direction="vertical" gap={2}>
            <Stack direction="horizontal" gap={2} align="center">
              <Text variant="title" className="flex-1">
                {d.name}
              </Text>
              <StatusBadge tone={d.status === "ACTIVE" ? "success" : "neutral"}>
                {d.status}
              </StatusBadge>
              <StatusBadge tone="info">{d.decision_type}</StatusBadge>
            </Stack>
            <Text variant="body">{d.description}</Text>
            {d.confidence != null && (
              <Text variant="caption" tone="muted">
                Confidence: {Math.round(d.confidence * 100)}%
              </Text>
            )}
          </Stack>
        </Card>
      ))}
    </Stack>
  );
}

function IntentsList({
  intents,
  isLoading,
  isError,
}: {
  intents: Intent[];
  isLoading: boolean;
  isError: boolean;
}) {
  if (isLoading) return <Skeleton shape="block" height={240} />;
  if (isError) {
    return (
      <ErrorState
        title="Failed to load intents"
        description="The backend did not return inferred intents."
      />
    );
  }
  if (intents.length === 0) {
    return (
      <EmptyState
        icon={<Sparkles size={20} />}
        title="No intents detected"
        description="Run discovery to surface strategic intents from commit history."
      />
    );
  }
  return (
    <Stack direction="vertical" gap={3}>
      {intents.map((i) => (
        <Card key={i.id} padded>
          <Stack direction="vertical" gap={2}>
            <Stack direction="horizontal" gap={2} align="center">
              <Sparkles
                size={14}
                className="text-[var(--color-primary)]"
                aria-hidden
              />
              <Text variant="title" className="flex-1">
                {i.name}
              </Text>
              <StatusBadge tone="primary">
                {Math.round(i.confidence * 100)}% confidence
              </StatusBadge>
            </Stack>
            <Text variant="body">{i.description}</Text>
            {i.supporting_decision_ids.length > 0 && (
              <Text variant="caption" tone="muted">
                {i.supporting_decision_ids.length} supporting decision
                {i.supporting_decision_ids.length === 1 ? "" : "s"}
              </Text>
            )}
          </Stack>
        </Card>
      ))}
    </Stack>
  );
}

function GraphView({
  graph,
  isLoading,
  isError,
}: {
  graph: DecisionGraph | null;
  isLoading: boolean;
  isError: boolean;
}) {
  if (isLoading) return <Skeleton shape="block" height={320} />;
  if (isError) {
    return (
      <ErrorState
        title="Failed to load decision graph"
        description="The backend did not return the graph."
      />
    );
  }
  if (!graph || graph.nodes.length === 0) {
    return (
      <EmptyState
        icon={<Network size={20} />}
        title="No decision graph"
        description="Causal links between decisions haven't been detected yet."
      />
    );
  }
  return (
    <Card padded>
      <Stack direction="vertical" gap={3}>
        <Text variant="eyebrow">Causal graph</Text>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
          {graph.nodes.slice(0, 24).map((n) => (
            <div
              key={n.id}
              className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-bg-surface-elevated)]/40 p-2"
            >
              <Text variant="caption" className="block truncate">
                {n.name}
              </Text>
              <Text variant="caption" tone="muted">
                {n.decision_type}
              </Text>
            </div>
          ))}
        </div>
        <Text variant="caption" tone="muted">
          {graph.edges.length} causal relationship
          {graph.edges.length === 1 ? "" : "s"} between {graph.nodes.length}{" "}
          decision
          {graph.nodes.length === 1 ? "" : "s"}.
        </Text>
      </Stack>
    </Card>
  );
}
