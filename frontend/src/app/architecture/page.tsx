"use client";

/**
 * /architecture — Architecture Studio.
 * Four tabs: Fitness, Drift, Bounded Contexts, Refactoring.
 * Drift tab offers commit-pair selection from the repo's commit list.
 */
import { useState } from "react";
import * as Tabs from "@radix-ui/react-tabs";
import { useQuery } from "@tanstack/react-query";
import AppShell from "@/components/layout/AppShell";
import { useUIStore } from "@/stores/uiStore";
import { temporalApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { CACHE } from "@/lib/constants";
import EmptyState from "@/components/common/EmptyState";
import { FitnessPanel } from "@/features/architecture/FitnessPanel";
import { DriftChart } from "@/features/architecture/DriftChart";
import { ContextMap } from "@/features/architecture/ContextMap";
import { RefactoringList } from "@/features/architecture/RefactoringList";

const TABS = [
  { value: "fitness", label: "Fitness" },
  { value: "drift", label: "Drift" },
  { value: "contexts", label: "Bounded Contexts" },
  { value: "refactoring", label: "Refactoring" },
] as const;

export default function ArchitecturePage() {
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);
  const [fromCommit, setFromCommit] = useState<string>("");
  const [toCommit, setToCommit] = useState<string>("");

  const commitsQ = useQuery({
    queryKey: queryKeys.temporal.commits(activeRepositoryId ?? ""),
    queryFn: () => temporalApi.listCommits(activeRepositoryId!),
    enabled: Boolean(activeRepositoryId),
    staleTime: CACHE.COMMITS,
  });

  const commits = commitsQ.data ?? [];

  if (!activeRepositoryId) {
    return (
      <AppShell>
        <div className="flex h-full items-center justify-center p-6">
          <EmptyState
            title="No repository selected"
            description="Select a repository from the top bar to explore its architecture."
          />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="mx-auto max-w-6xl p-6">
        <div className="mb-6 flex items-center gap-3 border-b border-[var(--color-border)] pb-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-[var(--color-text-primary)]">
              Architecture Studio
            </h1>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Fitness, drift, bounded contexts, and refactoring intelligence
            </p>
          </div>
        </div>

        <Tabs.Root defaultValue="fitness">
          <Tabs.List className="mb-6 flex gap-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-base-2)] p-1">
            {TABS.map((tab) => (
              <Tabs.Trigger
                key={tab.value}
                value={tab.value}
                className="flex-1 rounded-md px-3 py-2 text-sm font-medium text-[var(--color-text-secondary)] transition-colors data-[state=active]:bg-[var(--color-bg-surface-elevated)] data-[state=active]:text-[var(--color-text-primary)] data-[state=active]:shadow-sm"
              >
                {tab.label}
              </Tabs.Trigger>
            ))}
          </Tabs.List>

          <Tabs.Content value="fitness">
            <FitnessPanel repositoryId={activeRepositoryId} />
          </Tabs.Content>

          <Tabs.Content value="drift">
            <div className="mb-4 flex flex-wrap items-end gap-3">
              <label className="flex flex-col gap-1 text-xs text-[var(--color-text-secondary)]">
                From commit
                <select
                  value={fromCommit}
                  onChange={(e) => setFromCommit(e.target.value)}
                  className="rounded-md border border-[var(--color-border)] bg-[var(--color-bg-base-2)] px-2 py-1.5 text-sm text-[var(--color-text-primary)]"
                >
                  <option value="">Select…</option>
                  {commits.map((c) => (
                    <option key={c.hash} value={c.hash}>
                      {c.hash.slice(0, 7)} — {c.message.slice(0, 40)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-1 text-xs text-[var(--color-text-secondary)]">
                To commit
                <select
                  value={toCommit}
                  onChange={(e) => setToCommit(e.target.value)}
                  className="rounded-md border border-[var(--color-border)] bg-[var(--color-bg-base-2)] px-2 py-1.5 text-sm text-[var(--color-text-primary)]"
                >
                  <option value="">Select…</option>
                  {commits.map((c) => (
                    <option key={c.hash} value={c.hash}>
                      {c.hash.slice(0, 7)} — {c.message.slice(0, 40)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <DriftChart
              repositoryId={activeRepositoryId}
              fromCommit={fromCommit || undefined}
              toCommit={toCommit || undefined}
            />
          </Tabs.Content>

          <Tabs.Content value="contexts">
            <ContextMap repositoryId={activeRepositoryId} />
          </Tabs.Content>

          <Tabs.Content value="refactoring">
            <RefactoringList repositoryId={activeRepositoryId} />
          </Tabs.Content>
        </Tabs.Root>
      </div>
    </AppShell>
  );
}
