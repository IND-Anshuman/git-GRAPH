"use client";

/**
 * /reasoning — Reasoning Assistant.
 *
 * Wires to `reasoningApi` (formerly an empty stub). Chat-style UI:
 *  - Question input at the top
 *  - Evidence list in the middle
 *  - "Why this answer?" expandable at the bottom
 *
 * Health of the reasoning engine is shown in the sidebar.
 */
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Brain, Send, Sparkles, AlertTriangle, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import { useUIStore } from "@/stores";
import { reasoningApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import {
  Card,
  Stack,
  Text,
  Section,
  Skeleton,
  ErrorState,
  StatusBadge,
  Field,
  Button,
  EmptyState,
} from "@/components/ui";
import type { ReasoningResult, ReasoningHealth, CacheStatus } from "@/types/platform";

function useReasoningHealth() {
  return useQuery({
    queryKey: queryKeys.reasoning.health(),
    queryFn: () => reasoningApi.getHealth(),
    refetchInterval: 30_000,
  });
}

function useCacheStatus() {
  return useQuery({
    queryKey: queryKeys.reasoning.cacheStatus(),
    queryFn: () => reasoningApi.getCacheStatus(),
    refetchInterval: 60_000,
  });
}

export default function ReasoningPage() {
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ReasoningResult | null>(null);

  const healthQuery = useReasoningHealth();
  const cacheQuery = useCacheStatus();

  const queryMutation = useMutation({
    mutationFn: (q: string) =>
      reasoningApi.query({
        repository_id: activeRepositoryId!,
        commit_hash: "HEAD",
        query: q,
      }),
    onSuccess: (data) => setResult(data),
  });

  if (!activeRepositoryId) {
    return (
      <AppShell>
        <EmptyState
          icon={<Brain size={20} />}
          title="Select a repository"
          description="Reasoning is computed per-repository. Pick one from the top bar."
        />
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="px-12 py-8 max-w-[1400px] mx-auto flex flex-col gap-6 w-full">
        <Section
          eyebrow="Ask the codebase"
          title="Reasoning Assistant"
          description="Natural-language queries answered from capability, concept, and decision evidence."
        />

        <div className="grid grid-cols-1 lg:grid-cols-[1fr,300px] gap-6">
          {/* Main column: input + answer */}
          <Stack direction="vertical" gap={4}>
            <Card padded>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (question.trim() && !queryMutation.isPending) {
                    queryMutation.mutate(question.trim());
                  }
                }}
              >
                <Stack direction="vertical" gap={3}>
                  <Field
                    label="Question"
                    placeholder="e.g. Which capabilities are most likely to break if we refactor the ingestion pipeline?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    disabled={queryMutation.isPending}
                    helperText="The reasoning engine searches evidence across the active repository."
                  />
                  <Stack direction="horizontal" gap={2} justify="end">
                    <Button
                      type="submit"
                      variant="primary"
                      disabled={!question.trim()}
                      loading={queryMutation.isPending}
                      icon={<Send size={14} aria-hidden />}
                    >
                      Ask
                    </Button>
                  </Stack>
                </Stack>
              </form>
            </Card>

            <AnimatePresence mode="wait">
              {queryMutation.isError && (
                <motion.div
                  key="error"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <ErrorState
                    title="Reasoning failed"
                    description="The reasoning engine could not answer this question. Check the backend logs and retry."
                    onRetry={() => queryMutation.mutate(question)}
                  />
                </motion.div>
              )}

              {!queryMutation.isPending && !result && !queryMutation.isError && (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <EmptyState
                    icon={<Sparkles size={20} />}
                    title="Ask anything"
                    description="Try a question about a capability, an architectural decision, or a recent change."
                  />
                </motion.div>
              )}

              {result && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <ResultView result={result} />
                </motion.div>
              )}
            </AnimatePresence>
          </Stack>

          {/* Sidebar: health + cache */}
          <Stack direction="vertical" gap={4}>
            <HealthCard
              health={healthQuery.data}
              isLoading={healthQuery.isLoading}
              isError={healthQuery.isError}
            />
            <CacheCard
              cache={cacheQuery.data}
              isLoading={cacheQuery.isLoading}
              isError={cacheQuery.isError}
            />
            <Card padded>
              <Stack direction="vertical" gap={2}>
                <Text variant="eyebrow">Active repository</Text>
                <Text variant="body" className="font-mono break-all text-xs">
                  {activeRepositoryId}
                </Text>
                <Text variant="caption" tone="muted">
                  Reasoning uses the HEAD commit. Switch repositories from the top bar.
                </Text>
              </Stack>
            </Card>
          </Stack>
        </div>
      </div>
    </AppShell>
  );
}

function ResultView({ result }: { result: ReasoningResult }) {
  const [showWhy, setShowWhy] = useState(false);
  return (
    <Card padded>
      <Stack direction="vertical" gap={4}>
        <Stack direction="vertical" gap={2}>
          <Text variant="eyebrow">Answer</Text>
          <Text variant="body" className="leading-relaxed">
            {result.answer}
          </Text>
          {result.confidence && (
            <Stack direction="horizontal" gap={2} align="center">
              <StatusBadge
                tone={
                  result.confidence.level === "high"
                    ? "success"
                    : result.confidence.level === "medium"
                      ? "warning"
                      : "danger"
                }
                dot
              >
                {result.confidence.level} confidence ·{" "}
                {Math.round(result.confidence.score * 100)}%
              </StatusBadge>
            </Stack>
          )}
        </Stack>

        {result.evidence && result.evidence.length > 0 && (
          <Stack direction="vertical" gap={2}>
            <Text variant="eyebrow">Evidence</Text>
            <Stack direction="vertical" gap={2}>
              {result.evidence.slice(0, 5).map((e) => (
                <div
                  key={e.source_id}
                  className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-bg-surface-elevated)]/30 p-3"
                >
                  <Stack direction="horizontal" gap={2} align="center">
                    <CheckCircle2
                      size={14}
                      className="text-[var(--color-success)]"
                      aria-hidden
                    />
                    <Text variant="caption" tone="muted">
                      {e.source_type}
                    </Text>
                    <Text variant="caption" tone="muted">
                      weight {Math.round(e.weight * 100)}%
                    </Text>
                  </Stack>
                  <Text variant="body" className="mt-1">
                    {e.description}
                  </Text>
                </div>
              ))}
            </Stack>
          </Stack>
        )}

        {result.chain && result.chain.steps.length > 0 && (
          <Stack direction="vertical" gap={2}>
            <button
              type="button"
              onClick={() => setShowWhy((v) => !v)}
              className="self-start text-xs font-semibold uppercase tracking-wider text-[var(--color-primary)] hover:underline outline-none"
              aria-expanded={showWhy}
            >
              {showWhy ? "Hide" : "Why this answer?"} ({result.chain.total_steps} step
              {result.chain.total_steps === 1 ? "" : "s"})
            </button>
            <AnimatePresence>
              {showWhy && (
                <motion.ol
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="flex flex-col gap-2 pl-4 list-decimal"
                >
                  {result.chain.steps.map((s) => (
                    <li key={s.step_index} className="text-sm text-[var(--color-text-secondary)]">
                      <Text variant="caption" tone="muted" className="block">
                        {s.step_type}
                      </Text>
                      {s.description}
                    </li>
                  ))}
                </motion.ol>
              )}
            </AnimatePresence>
          </Stack>
        )}

        {result.limitations && result.limitations.length > 0 && (
          <Stack direction="vertical" gap={2}>
            <Text variant="eyebrow">Limitations</Text>
            {result.limitations.map((l, i) => (
              <Stack key={i} direction="horizontal" gap={2} align="start">
                <AlertTriangle
                  size={14}
                  className="text-[var(--color-warning)] shrink-0 mt-0.5"
                  aria-hidden
                />
                <Text variant="caption" tone="muted">
                  {l.reason}
                </Text>
              </Stack>
            ))}
          </Stack>
        )}
      </Stack>
    </Card>
  );
}

function HealthCard({
  health,
  isLoading,
  isError,
}: {
  health: ReasoningHealth | undefined;
  isLoading: boolean;
  isError: boolean;
}) {
  if (isLoading) return <Skeleton shape="block" height={120} />;
  if (isError) {
    return (
      <ErrorState
        title="Engine unavailable"
        description="The reasoning engine health check failed."
      />
    );
  }
  if (!health) return null;
  return (
    <Card padded>
      <Stack direction="vertical" gap={2}>
        <Stack direction="horizontal" gap={2} align="center">
          <Brain size={14} className="text-[var(--color-primary)]" aria-hidden />
          <Text variant="eyebrow">Reasoning engine</Text>
        </Stack>
        <StatusBadge tone={health.status === "healthy" ? "success" : "danger"} dot>
          {health.status}
        </StatusBadge>
        <Text variant="caption" tone="muted">
          v{health.reasoning_version} · {health.cache_size} cached ·{" "}
          {health.registered_strategies.length} strategies
        </Text>
      </Stack>
    </Card>
  );
}

function CacheCard({
  cache,
  isLoading,
  isError,
}: {
  cache: CacheStatus | undefined;
  isLoading: boolean;
  isError: boolean;
}) {
  if (isLoading) return <Skeleton shape="block" height={100} />;
  if (isError) return null;
  if (!cache) return null;
  return (
    <Card padded>
      <Stack direction="vertical" gap={2}>
        <Text variant="eyebrow">Cache</Text>
        <Text variant="title">{cache.cache_size}</Text>
        <Text variant="caption" tone="muted">
          {cache.message}
        </Text>
      </Stack>
    </Card>
  );
}
