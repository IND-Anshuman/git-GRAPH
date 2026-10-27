'use client';

import React from "react";
import { ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import { useCapabilities } from "@/hooks/useCapabilities";
import { Card, Stack, Text, Skeleton, ErrorState, EmptyState, riskScoreToTone } from "@/components/ui";
import Sparkline from "@/components/common/Sparkline";

interface RepositoryHealthWidgetProps {
  repositoryId: string | null;
}

// Sparklines plot real per-capability scores in discovery order (oldest ->
// newest). There is no repository-level health history endpoint, so the
// widget shows no trend arrows rather than inventing a direction.

function RepositoryHealthInner({ repositoryId }: RepositoryHealthWidgetProps) {
  const { data: capabilities = [], isLoading, isError, refetch } = useCapabilities(repositoryId);

  if (isLoading) {
    return (
      <Card padded style={{ minHeight: 420 }}>
        <Stack direction="vertical" gap={3} align="center" className="h-full justify-center">
          <Skeleton shape="circle" width="quarter" height={48} />
          <Skeleton width="third" />
          <Skeleton width="half" />
        </Stack>
      </Card>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load metrics"
        description="We couldn't reach the backend. Check your connection and try again."
        onRetry={() => refetch()}
      />
    );
  }

  if (capabilities.length === 0) {
    return (
      <EmptyState
        icon={<ShieldCheck size={20} />}
        title="No data available"
        description="Ingest a repository to view intelligence metrics."
      />
    );
  }

  // ── Compute averages ──────────────────────────────────────────────
  // Backend returns scores in [0, 1]; widgets display as 0–100 ints.
  const parseScore = (val: number) => (val > 1 ? val / 100 : val);

  const totalCaps = capabilities.length;
  let sumMaturity = 0;
  let sumRisk = 0;
  let sumCoverage = 0;

  for (const c of capabilities) {
    sumMaturity += parseScore(c.maturity_score);
    sumRisk += parseScore(c.risk_score);
    sumCoverage += parseScore(c.coverage_score);
  }

  const avgMaturity = sumMaturity / totalCaps;
  const avgRisk = sumRisk / totalCaps;
  const avgCoverage = sumCoverage / totalCaps;

  // System Intelligence Score: (Maturity + Coverage + (1 - Risk)) / 3
  const healthScore = Math.max(
    0,
    Math.min(100, Math.round(((avgMaturity + avgCoverage + (1 - avgRisk)) / 3) * 100)),
  );

  const byDiscovery = [...capabilities].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  );
  const riskSparkline = byDiscovery.map((c) => parseScore(c.risk_score) * 100);
  const coverageSparkline = byDiscovery.map((c) => parseScore(c.coverage_score) * 100);
  const maturitySparkline = byDiscovery.map((c) => parseScore(c.maturity_score) * 100);
  const highRiskCount = capabilities.filter((c) => parseScore(c.risk_score) >= 0.6).length;

  const riskLevel: "low" | "medium" | "high" | "critical" =
    avgRisk >= 0.7 ? "critical" : avgRisk >= 0.4 ? "medium" : "low";
  const riskTone = riskScoreToTone(avgRisk);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{ minHeight: 420 }}
    >
      <Card padded>
        <Stack direction="vertical" gap={8}>
          {/* Center-aligned score */}
          <Stack direction="vertical" gap={2} align="center">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
            >
              <Text variant="metric" tone="primary" className="text-5xl font-bold">
                {healthScore}
              </Text>
            </motion.div>
            <Text variant="eyebrow">System Intelligence</Text>
          </Stack>

          {/* Three metrics */}
          <div className="grid grid-cols-3 gap-6">
            {/* Risk */}
            <Stack direction="vertical" gap={3}>
              <Text variant="eyebrow">Risk</Text>
              <Stack direction="horizontal" gap={2} align="baseline">
                <Text
                  variant="title"
                  className="text-4xl"
                  tone={
                    riskTone === "danger"
                      ? "danger"
                      : riskTone === "warning"
                        ? "warning"
                        : "success"
                  }
                >
                  {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)}
                </Text>
              </Stack>
              <Text variant="caption" tone="muted">
                {highRiskCount} of {totalCaps} capabilities high risk
              </Text>
              <Sparkline
                data={riskSparkline}
                width={180}
                height={40}
                color={
                  riskTone === "danger"
                    ? "var(--color-danger)"
                    : riskTone === "warning"
                      ? "var(--color-warning)"
                      : "var(--color-success)"
                }
                strokeWidth={2}
                filled
              />
            </Stack>

            {/* Coverage */}
            <Stack direction="vertical" gap={3}>
              <Text variant="eyebrow">Coverage</Text>
              <Stack direction="horizontal" gap={2} align="baseline">
                <Text variant="title" className="text-4xl" tone="primary">
                  {Math.round(avgCoverage * 100)}%
                </Text>
              </Stack>
              <Text variant="caption" tone="muted">
                average across {totalCaps} capabilities
              </Text>
              <Sparkline
                data={coverageSparkline}
                width={180}
                height={40}
                color="var(--color-primary)"
                strokeWidth={2}
                filled
              />
            </Stack>

            {/* Drift */}
            <Stack direction="vertical" gap={3}>
              <Text variant="eyebrow">Maturity</Text>
              <Stack direction="horizontal" gap={2} align="baseline">
                <Text variant="title" className="text-4xl" tone="warning">
                  {Math.round(avgMaturity * 100)}%
                </Text>
              </Stack>
              <Text variant="caption" tone="muted">
                per capability, oldest → newest
              </Text>
              <Sparkline
                data={maturitySparkline}
                width={180}
                height={40}
                color="var(--color-warning)"
                strokeWidth={2}
                filled
              />
            </Stack>
          </div>
        </Stack>
      </Card>
    </motion.div>
  );
}

export default function RepositoryHealthWidget({ repositoryId }: RepositoryHealthWidgetProps) {
  return (
    <ErrorBoundary>
      <RepositoryHealthInner repositoryId={repositoryId} />
    </ErrorBoundary>
  );
}

// Minimal error boundary kept local to avoid pulling common/ into the import graph
import { Component, type ReactNode } from "react";
class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; message?: string }
> {
  state = { hasError: false, message: undefined as string | undefined };
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, message: error.message };
  }
  render() {
    if (this.state.hasError) {
      return (
        <ErrorState
          title="Widget crashed"
          description={this.state.message ?? "An unexpected error occurred."}
        />
      );
    }
    return this.props.children;
  }
}
