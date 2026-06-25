"use client";

import React, { memo } from "react";
import { Bell, Search } from "lucide-react";

import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores";
import { useCommandPaletteStore } from "@/stores";
import type { Repository } from "@/types/platform";
import { RepositorySelector } from "./RepositorySelector";

// ─── Types ────────────────────────────────────────────────────────────────────

interface TopBarProps {
  repositories: Repository[];
}

// ─── SearchTrigger ────────────────────────────────────────────────────────────

const SearchTrigger = memo(function SearchTrigger() {
  const openSearch = useCommandPaletteStore((s) => s.openSearch);

  return (
    <button
      type="button"
      onClick={openSearch}
      aria-label="Open command palette (Ctrl+K)"
      aria-keyshortcuts="Control+K"
      className={cn(
        "flex items-center gap-2",
        "h-9 px-3 rounded-[var(--radius-xl)]",
        "bg-[rgba(0,240,255,0.04)]",
        "border border-[rgba(0,240,255,0.12)]",
        "text-[var(--color-text-tertiary)] text-sm",
        "hover:border-[rgba(0,240,255,0.3)]",
        "hover:text-[var(--neon-blue)]",
        "hover:bg-[rgba(0,240,255,0.07)]",
        "hover:shadow-[0_0_12px_rgba(0,240,255,0.12)]",
        "transition-all duration-150 ease-out",
        "focus-visible:outline-none focus-visible:ring-2",
        "focus-visible:ring-[var(--neon-blue)]",
        "focus-visible:ring-offset-1",
        "focus-visible:ring-offset-[rgba(5,5,16,0.9)]",
        "min-w-[220px]",
      )}
    >
      <Search size={14} className="shrink-0" aria-hidden="true" />
      <span className="flex-1 text-left whitespace-nowrap text-xs">
        Search...
      </span>
      <kbd
        className={cn(
          "flex items-center gap-0.5",
          "text-[10px] font-mono text-[var(--color-text-muted)]",
          "bg-[var(--color-bg-surface)] border border-[var(--color-border)]",
          "px-1.5 py-0.5 rounded",
        )}
        aria-hidden="true"
      >
        Ctrl+K
      </kbd>
    </button>
  );
});

// ─── NotificationBell ─────────────────────────────────────────────────────────

const NotificationBell = memo(function NotificationBell() {
  return (
    <button
      type="button"
      aria-label="Notifications (0 unread)"
      className={cn(
        "relative flex items-center justify-center",
        "w-9 h-9 rounded-[var(--radius-xl)]",
        "text-[var(--color-text-tertiary)]",
        "hover:bg-[var(--color-bg-surface-elevated)]",
        "hover:text-[var(--color-text-secondary)]",
        "transition-colors duration-150",
        "focus-visible:outline-none focus-visible:ring-2",
        "focus-visible:ring-[var(--color-primary)]",
        "focus-visible:ring-offset-1",
        "focus-visible:ring-offset-[var(--color-bg-surface)]",
      )}
    >
      <Bell size={16} aria-hidden="true" />
      {/* Unread dot — placeholder, hidden until wired up */}
      <span className="sr-only">No notifications</span>
    </button>
  );
});

// ─── UserAvatar ───────────────────────────────────────────────────────────────

const UserAvatar = memo(function UserAvatar() {
  return (
    <button
      type="button"
      aria-label="User menu"
      aria-haspopup="menu"
      className={cn(
        "flex items-center justify-center shrink-0",
        "w-9 h-9 rounded-full",
        "bg-[var(--color-primary-muted)]",
        "border border-[var(--color-border)]",
        "text-[var(--color-primary)] text-xs font-bold",
        "hover:border-[var(--color-primary)]",
        "transition-colors duration-150",
        "focus-visible:outline-none focus-visible:ring-2",
        "focus-visible:ring-[var(--color-primary)]",
        "focus-visible:ring-offset-1",
        "focus-visible:ring-offset-[var(--color-bg-surface)]",
      )}
    >
      {/* Placeholder initials — replace with actual user data */}
      <span aria-hidden="true">U</span>
    </button>
  );
});

// ─── TopBar ───────────────────────────────────────────────────────────────────

export const TopBar = memo(function TopBar({ repositories }: TopBarProps) {
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);
  const setActiveRepositoryId = useUIStore((s) => s.setActiveRepositoryId);

  const activeRepo = repositories.find((r) => r.id === activeRepositoryId);

  return (
    <header
      role="banner"
      aria-label="Application top bar"
      className={cn(
        "fixed top-0 right-0 z-[var(--z-sticky)]",
        "h-[var(--topbar-height)]",
        "bg-[rgba(5,5,16,0.72)] backdrop-blur-xl",
        "border-b border-[rgba(0,240,255,0.1)]",
        "transition-[left] duration-300 ease-in-out",
      )}
      style={{
        left: "var(--_sidebar-current-width, var(--sidebar-width))",
        boxShadow: '0 1px 0 rgba(0,240,255,0.06), 0 4px 24px rgba(0,0,0,0.4)',
      }}
    >
      <div className="w-full h-full max-w-[1600px] mx-auto px-6 flex items-center justify-between gap-3">
        {/* ── Left: Repository selector ─────────────────────────────── */}
        <div className="flex items-center shrink-0">
          <RepositorySelector
            repositories={repositories}
            activeRepo={activeRepo ?? null}
            onSelect={setActiveRepositoryId}
          />
        </div>

        {/* ── Center: Breadcrumbs / spacer ─────────────────────────── */}
        <div
          className="flex-1 flex items-center min-w-0 justify-center"
          aria-label="Breadcrumbs"
          role="navigation"
        >
          <div className="hidden md:flex items-center gap-2 text-[11px] uppercase tracking-[0.24em] text-[var(--color-text-tertiary)] font-mono">
            <span>Command Center</span>
            <span
              className="h-1 w-1 rounded-full"
              style={{ background: 'var(--neon-blue)', boxShadow: '0 0 6px var(--neon-blue)' }}
              aria-hidden="true"
            />
            <span style={{ color: 'var(--neon-blue)', textShadow: '0 0 8px rgba(0,240,255,0.4)' }}>
              {activeRepo?.name ?? 'No repository selected'}
            </span>
          </div>
          <span className="sr-only">Current location</span>
        </div>

        {/* ── Right: Actions ───────────────────────────────────────── */}
        <div className="flex items-center gap-2 shrink-0" role="toolbar" aria-label="Header actions">
          <SearchTrigger />

          <span
            className="w-px h-5 bg-[var(--color-border)] mx-1"
            aria-hidden="true"
          />

          <NotificationBell />
          <UserAvatar />
        </div>
      </div>
    </header>
  );
});

export default TopBar;
