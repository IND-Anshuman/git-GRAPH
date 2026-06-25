"use client";

import React, { useState, useMemo, useCallback, useRef } from "react";
import { List } from "react-window";
import Fuse from "fuse.js";
import { Search, X, SlidersHorizontal, ChevronDown, ChevronUp } from "lucide-react";

import { cn } from "@/lib/utils";
import {
  CAPABILITY_TYPES,
  RISK_LEVELS,
  VIRTUALIZATION_THRESHOLD,
  SEARCH_DEBOUNCE_MS,
} from "@/lib/constants";
import type { Capability } from "@/types/platform";
import { useCapabilities } from "@/hooks/useCapabilities";
import { useDebounce } from "@/hooks/useDebounce";
import { useUIStore } from "@/stores";
import { CapabilityCard } from "./CapabilityCard";

// ─── Skeleton row ─────────────────────────────────────────────────────────────
function SkeletonRow({ index }: { index: number }) {
  return (
    <div
      key={index}
      className="flex flex-col justify-center gap-2 px-3 border-b"
      style={{
        height: 72,
        borderColor: "var(--color-border-subtle)",
      }}
    >
      <div
        className="skeleton rounded"
        style={{ height: 12, width: `${55 + (index % 4) * 10}%` }}
      />
      <div
        className="skeleton rounded"
        style={{ height: 10, width: `${40 + (index % 3) * 8}%` }}
      />
    </div>
  );
}

// ─── Risk level options ───────────────────────────────────────────────────────
const RISK_LEVEL_OPTIONS = RISK_LEVELS as unknown as string[];
const CAPABILITY_TYPE_OPTIONS = CAPABILITY_TYPES as unknown as string[];

// ─── Main component ───────────────────────────────────────────────────────────
export function CapabilityNavigator() {
  const repositoryId        = useUIStore((s) => s.activeRepositoryId);
  const selectedId          = useUIStore((s) => s.selectedCapabilityId);
  const setSelectedId       = useUIStore((s) => s.setSelectedCapabilityId);
  const filterPanelOpen     = useUIStore((s) => s.filterPanelOpen);
  const toggleFilterPanel   = useUIStore((s) => s.toggleFilterPanel);

  // ── Local state ─────────────────────────────────────────────────────────────
  const [searchQuery, setSearchQuery]         = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedRisks, setSelectedRisks]     = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes]     = useState<string[]>([]);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const debouncedQuery = useDebounce(searchQuery, SEARCH_DEBOUNCE_MS);

  // ── Data ─────────────────────────────────────────────────────────────────────
  const { data, isLoading, isError } = useCapabilities(repositoryId);
  const capabilities: Capability[] = data ?? [];

  // ── Fuse.js instance ─────────────────────────────────────────────────────────
  const fuse = useMemo(
    () =>
      new Fuse(capabilities, {
        keys: ["name", "description", "capability_type"],
        threshold: 0.35,
        includeScore: false,
      }),
    [capabilities]
  );

  // ── Active filter count ──────────────────────────────────────────────────────
  const activeFilterCount = [
    selectedCategory ? 1 : 0,
    selectedRisks.length,
    selectedTypes.length,
  ].reduce((a, b) => a + b, 0);

  // ── Filtered list ────────────────────────────────────────────────────────────
  const filteredCapabilities = useMemo<Capability[]>(() => {
    let result: Capability[] =
      debouncedQuery.trim().length >= 2
        ? fuse.search(debouncedQuery).map((r) => r.item)
        : [...capabilities];

    if (selectedCategory) {
      result = result.filter((c) => c.category === selectedCategory);
    }
    if (selectedRisks.length > 0) {
      result = result.filter((c) => {
        const level =
          c.risk_score <= 0.25
            ? "low"
            : c.risk_score <= 0.5
            ? "medium"
            : c.risk_score <= 0.75
            ? "high"
            : "critical";
        return selectedRisks.includes(level);
      });
    }
    if (selectedTypes.length > 0) {
      result = result.filter((c) => selectedTypes.includes(c.capability_type));
    }

    return result;
  }, [capabilities, debouncedQuery, fuse, selectedCategory, selectedRisks, selectedTypes]);

  // ── Handlers ─────────────────────────────────────────────────────────────────
  const handleClearSearch = useCallback(() => {
    setSearchQuery("");
    searchInputRef.current?.focus();
  }, []);

  const toggleRisk = useCallback((level: string) => {
    setSelectedRisks((prev) =>
      prev.includes(level) ? prev.filter((r) => r !== level) : [...prev, level]
    );
  }, []);

  const toggleType = useCallback((type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  }, []);

  const clearAllFilters = useCallback(() => {
    setSelectedCategory("");
    setSelectedRisks([]);
    setSelectedTypes([]);
    setSearchQuery("");
  }, []);

  // ── Virtualized row renderer ─────────────────────────────────────────────────
  const VirtualRow = useCallback(
    ({ index, style }: { index: number; style: React.CSSProperties }) => {
      const cap = filteredCapabilities[index];
      if (!cap) return null;
      return (
        <CapabilityCard
          capability={cap}
          isSelected={selectedId === cap.id}
          onClick={() => setSelectedId(cap.id)}
          style={style}
        />
      );
    },
    [filteredCapabilities, selectedId, setSelectedId]
  );

  // ── Render ───────────────────────────────────────────────────────────────────
  return (
    <aside
      aria-label="Capability navigator"
      className="flex flex-col h-full rounded-[var(--radius-2xl)] overflow-hidden"
      style={{
        background: "rgba(20, 26, 42, 0.45)",
        backdropFilter: "blur(16px)",
        WebkitBackdropFilter: "blur(16px)",
        border: "1px solid var(--color-border)",
        width: "var(--navigator-width)",
        minWidth: "var(--navigator-width)",
      }}
    >
      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div
        className="flex flex-col gap-3 px-4 py-4 shrink-0"
        style={{ borderBottom: "1px solid var(--color-border)" }}
      >
        {/* Search row */}
        <div className="flex items-center gap-2.5">
          <div
            className="flex items-center flex-1 gap-2 px-3 rounded-md"
            style={{
              background: "var(--color-bg-base)",
              border: "1px solid var(--color-border)",
              height: 38,
            }}
          >
            <Search size={14} style={{ color: "var(--color-text-muted)", flexShrink: 0 }} aria-hidden />
            <input
              ref={searchInputRef}
              type="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search capabilities…"
              aria-label="Search capabilities"
              className="flex-1 bg-transparent text-xs outline-none"
              style={{ color: "var(--color-text-primary)" }}
            />
            {searchQuery && (
              <button
                onClick={handleClearSearch}
                aria-label="Clear search"
                className="shrink-0 rounded transition-colors hover:text-white"
                style={{ color: "var(--color-text-muted)" }}
              >
                <X size={12} />
              </button>
            )}
          </div>

          {/* Filter toggle */}
          <button
            onClick={toggleFilterPanel}
            aria-expanded={filterPanelOpen}
            aria-label={`Filters${activeFilterCount > 0 ? `, ${activeFilterCount} active` : ""}`}
            className="relative flex items-center justify-center rounded-md transition-colors"
            style={{
              width: 38,
              height: 38,
              background: filterPanelOpen ? "var(--color-primary-muted)" : "var(--color-bg-base)",
              border: `1px solid ${filterPanelOpen ? "var(--color-primary)" : "var(--color-border)"}`,
              color: filterPanelOpen ? "var(--color-primary)" : "var(--color-text-secondary)",
              flexShrink: 0,
            }}
          >
            <SlidersHorizontal size={14} aria-hidden />
            {activeFilterCount > 0 && (
              <span
                className="absolute -top-1.5 -right-1.5 flex items-center justify-center text-[9px] font-bold rounded-full"
                style={{
                  width: 14,
                  height: 14,
                  background: "var(--color-primary)",
                  color: "#fff",
                }}
              >
                {activeFilterCount}
              </span>
            )}
          </button>
        </div>

        {/* Filter panel */}
        {filterPanelOpen && (
          <div
            className="flex flex-col gap-3 px-1 py-2 rounded"
            style={{ background: "var(--color-bg-base)", border: "1px solid var(--color-border-subtle)" }}
          >
            {/* Risk level */}
            <FilterSection label="Risk Level">
              <div className="flex flex-wrap gap-1">
                {RISK_LEVEL_OPTIONS.map((level) => (
                  <FilterChip
                    key={level}
                    label={level}
                    active={selectedRisks.includes(level)}
                    onClick={() => toggleRisk(level)}
                  />
                ))}
              </div>
            </FilterSection>

            {/* Capability type */}
            <FilterSection label="Type">
              <div className="flex flex-wrap gap-1">
                {CAPABILITY_TYPE_OPTIONS.map((type) => (
                  <FilterChip
                    key={type}
                    label={type}
                    active={selectedTypes.includes(type)}
                    onClick={() => toggleType(type)}
                  />
                ))}
              </div>
            </FilterSection>

            {/* Clear */}
            {activeFilterCount > 0 && (
              <button
                onClick={clearAllFilters}
                className="text-xs underline self-start transition-colors"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                Clear all filters
              </button>
            )}
          </div>
        )}
      </div>

      {/* ── Item count ──────────────────────────────────────────────────────── */}
      <div
        className="px-3 py-1.5 text-[11px] shrink-0"
        style={{ color: "var(--color-text-muted)", borderBottom: "1px solid var(--color-border-subtle)" }}
      >
        {isLoading
          ? "Loading…"
          : isError
          ? "Failed to load"
          : `${filteredCapabilities.length} ${filteredCapabilities.length === 1 ? "capability" : "capabilities"}`}
      </div>

      {/* ── List ────────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-hidden relative" role="list" aria-label="Capabilities list">
        {isLoading ? (
          <div>
            {Array.from({ length: 8 }).map((_, i) => (
              <SkeletonRow key={i} index={i} />
            ))}
          </div>
        ) : isError ? (
          <div className="flex flex-col items-center justify-center h-32 gap-2 px-4 text-center">
            <span className="text-2xl">⚠</span>
            <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
              Could not load capabilities.
            </p>
          </div>
        ) : filteredCapabilities.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 gap-2 px-4 text-center">
            <Search size={28} style={{ color: "var(--color-text-muted)" }} />
            <p className="text-xs font-medium" style={{ color: "var(--color-text-secondary)" }}>
              No capabilities match
            </p>
            <p className="text-[11px]" style={{ color: "var(--color-text-muted)" }}>
              Try adjusting search or filters
            </p>
            {(searchQuery || activeFilterCount > 0) && (
              <button
                onClick={clearAllFilters}
                className="text-xs underline mt-1"
                style={{ color: "var(--color-primary)" }}
              >
                Clear all
              </button>
            )}
          </div>
        ) : filteredCapabilities.length > VIRTUALIZATION_THRESHOLD ? (
          // Virtualized list
          <AutoSizedList
            items={filteredCapabilities}
            selectedId={selectedId}
            setSelectedId={setSelectedId}
            VirtualRow={VirtualRow}
          />
        ) : (
          // Regular list
          <div className="overflow-y-auto h-full">
            {filteredCapabilities.map((cap) => (
              <CapabilityCard
                key={cap.id}
                capability={cap}
                isSelected={selectedId === cap.id}
                onClick={() => setSelectedId(cap.id)}
              />
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

// ─── AutoSizedList — wraps List with container height measurement ────
function AutoSizedList({
  items,
  VirtualRow,
}: {
  items: Capability[];
  selectedId: string | null;
  setSelectedId: (id: string | null) => void;
  VirtualRow: (props: { index: number; style: React.CSSProperties }) => React.ReactElement | null;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(600);

  React.useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      if (entry) setHeight(entry.contentRect.height);
    });
    ro.observe(el);
    setHeight(el.clientHeight);
    return () => ro.disconnect();
  }, []);

  return (
    <div ref={containerRef} style={{ height: "100%", overflow: "hidden" }}>
      <List
        style={{ height }}
        rowCount={items.length}
        rowHeight={72}
        rowComponent={VirtualRow as any}
        rowProps={{}}
        overscanCount={5}
      />
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────────────
function FilterSection({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-[10px] font-semibold uppercase tracking-wider"
        style={{ color: "var(--color-text-muted)" }}>
        {label}
      </span>
      {children}
    </div>
  );
}

function FilterChip({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className="text-[10px] font-medium px-2 py-0.5 rounded-full transition-colors capitalize"
      style={{
        background: active ? "var(--color-primary)" : "var(--color-bg-surface)",
        color: active ? "#fff" : "var(--color-text-secondary)",
        border: `1px solid ${active ? "var(--color-primary)" : "var(--color-border)"}`,
      }}
    >
      {label.toLowerCase()}
    </button>
  );
}
