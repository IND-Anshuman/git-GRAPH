"use client";

import React, { memo } from "react";
import { cn, formatScore, truncate } from "@/lib/utils";
import type { Capability } from "@/types/platform";

// ─── Capability Type badge color map ────────────────────────────────────────
const TYPE_COLORS: Record<string, { bg: string; text: string }> = {
  AI:             { bg: "rgba(139,92,246,0.15)", text: "#A78BFA" },
  BUSINESS:       { bg: "rgba(79,124,255,0.15)",  text: "#7BA4FF" },
  TECHNICAL:      { bg: "rgba(6,182,212,0.15)",   text: "#22D3EE" },
  INFRASTRUCTURE: { bg: "rgba(249,115,22,0.15)",  text: "#FB923C" },
  SECURITY:       { bg: "rgba(239,68,68,0.15)",   text: "#F87171" },
  INTEGRATION:    { bg: "rgba(16,185,129,0.15)",  text: "#34D399" },
};

const RISK_COLORS: Record<string, { bg: string; text: string }> = {
  low:      { bg: "rgba(34,197,94,0.12)",    text: "#22C55E" },
  medium:   { bg: "rgba(245,158,11,0.12)",   text: "#F59E0B" },
  high:     { bg: "rgba(249,115,22,0.12)",   text: "#F97316" },
  critical: { bg: "rgba(239,68,68,0.12)",    text: "#EF4444" },
};

function getRiskLevel(score: number): string {
  if (score <= 0.25) return "low";
  if (score <= 0.5)  return "medium";
  if (score <= 0.75) return "high";
  return "critical";
}

// ─── Props ───────────────────────────────────────────────────────────────────
export interface CapabilityCardProps {
  capability: Capability;
  isSelected: boolean;
  onClick: () => void;
  /** Optional style injection for react-window absolute positioning */
  style?: React.CSSProperties;
}

// ─── Component ───────────────────────────────────────────────────────────────
export const CapabilityCard = memo(function CapabilityCard({
  capability,
  isSelected,
  onClick,
  style,
}: CapabilityCardProps) {
  const typeColor  = TYPE_COLORS[capability.capability_type] ?? { bg: "rgba(255,255,255,0.05)", text: "#8B95B0" };
  const riskLevel  = getRiskLevel(capability.risk_score);
  const riskColor  = RISK_COLORS[riskLevel] ?? RISK_COLORS.medium;
  const confidence = formatScore(capability.confidence);
  const desc       = capability.description
    ? truncate(capability.description, 120)
    : "No description available.";

  return (
    <div
      role="listitem"
      aria-selected={isSelected}
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      }}
      className={cn(
        "relative flex flex-col justify-center gap-1 px-3 cursor-pointer select-none",
        "border-b transition-colors duration-150",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--color-primary)]",
        isSelected
          ? "bg-[var(--color-bg-surface-elevated)] border-b-[var(--color-border)]"
          : "bg-[var(--color-bg-surface)] hover:bg-[var(--color-bg-surface-elevated)] border-b-[var(--color-border-subtle)]"
      )}
      style={{
        ...style,
        height: 72,
        borderLeftWidth: 3,
        borderLeftStyle: "solid",
        borderLeftColor: isSelected ? "var(--color-primary)" : "transparent",
      }}
    >
      {/* Row 1 — name + badges */}
      <div className="flex items-center gap-2 min-w-0">
        <span
          className="text-sm font-semibold truncate flex-1"
          style={{ color: "var(--color-text-primary)" }}
          title={capability.name}
        >
          {capability.name}
        </span>

        {/* Capability type badge */}
        <span
          className="shrink-0 text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded"
          style={{ background: typeColor.bg, color: typeColor.text }}
        >
          {capability.capability_type}
        </span>

        {/* Risk badge */}
        <span
          className="shrink-0 text-[10px] font-medium uppercase tracking-wide px-1.5 py-0.5 rounded"
          style={{ background: riskColor.bg, color: riskColor.text }}
        >
          {riskLevel}
        </span>
      </div>

      {/* Row 2 — description + confidence */}
      <div className="flex items-center gap-2 min-w-0">
        <p
          className="truncate-2 text-xs flex-1 leading-snug"
          style={{ color: "var(--color-text-secondary)", WebkitLineClamp: 1, display: "-webkit-box", WebkitBoxOrient: "vertical", overflow: "hidden" }}
        >
          {desc}
        </p>
        <span
          className="shrink-0 text-xs font-mono tabular-nums"
          style={{ color: "var(--color-text-tertiary)" }}
          aria-label={`Confidence ${confidence}`}
        >
          {confidence}
        </span>
      </div>
    </div>
  );
});
