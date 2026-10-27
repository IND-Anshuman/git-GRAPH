"use client";

/**
 * /timeline — Evolution Time Machine.
 * Scrub or play through commits; the graph diffs frame-to-frame with
 * added (green) / removed (red) coloring.
 */
import dynamic from "next/dynamic";
import { Clock } from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import EmptyState from "@/components/common/EmptyState";
import { useUIStore } from "@/stores";
import { useQuery } from "@tanstack/react-query";
import { temporalApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { CACHE } from "@/lib/constants";

// ReactFlow inside TimeMachine — no SSR
const TimeMachine = dynamic(
  () =>
    import("@/features/time-machine/TimeMachine").then((m) => m.TimeMachine),
  { ssr: false }
);

export default function TimelinePage() {
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);

  // Commit count gate: need >= 2 commits for a meaningful evolution
  const commitsQuery = useQuery({
    queryKey: queryKeys.temporal.commits(activeRepositoryId ?? ""),
    queryFn: () => temporalApi.listCommits(activeRepositoryId!),
    enabled: !!activeRepositoryId,
    staleTime: CACHE.COMMITS,
  });

  const commitCount = commitsQuery.data?.length ?? 0;

  return (
    <AppShell>
      <div className="flex h-full flex-col">
        {/* Page header */}
        <div className="flex items-center gap-3 border-b border-[var(--color-border)] px-6 py-4 shrink-0">
          <div className="p-2 bg-[var(--color-primary-muted)] text-[var(--color-primary)] rounded">
            <Clock className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-xl font-bold tracking-tight text-sip-text-primary">
              Evolution Time Machine
            </h1>
            <span className="text-[10px] uppercase tracking-wider font-bold text-[var(--color-primary)]">
              Temporal Reconstruction
            </span>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 min-h-0">
          {!activeRepositoryId ? (
            <div className="flex h-full items-center justify-center">
              <EmptyState
                title="No repository selected"
                description="Select a repository from the top bar to replay its evolution."
              />
            </div>
          ) : commitsQuery.isLoading ? (
            <div className="flex h-full items-center justify-center">
              <span className="font-mono text-[10px] uppercase tracking-widest text-[var(--color-text-muted)]">
                indexing commits…
              </span>
            </div>
          ) : commitCount < 2 ? (
            <div className="flex h-full items-center justify-center">
              <EmptyState
                title="Not enough history"
                description={`This repository has ${commitCount} commit${commitCount === 1 ? "" : "s"}. At least 2 are needed to replay evolution.`}
              />
            </div>
          ) : (
            <TimeMachine repositoryId={activeRepositoryId} />
          )}
        </div>
      </div>
    </AppShell>
  );
}
