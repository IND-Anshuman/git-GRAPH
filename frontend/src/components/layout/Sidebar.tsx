"use client";

import React, { memo, useCallback, useMemo } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import * as Tooltip from "@radix-ui/react-tooltip";
import {
  Code2,
  LayoutDashboard,
  Boxes,
  Network,
  GitFork,
  Brain,
  Clock,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { NAV_ITEMS, APP_NAME } from "@/lib/constants";
import { useUIStore } from "@/stores";

// ─── Icon map ────────────────────────────────────────────────────────────────

const ICON_MAP = {
  LayoutDashboard,
  Boxes,
  Network,
  GitFork,
  Brain,
  Clock,
} as const;

type IconName = keyof typeof ICON_MAP;

// ─── Types ────────────────────────────────────────────────────────────────────

type NavItem = (typeof NAV_ITEMS)[number];

// ─── Constants ────────────────────────────────────────────────────────────────

const SIDEBAR_EXPANDED_WIDTH = 220;
const SIDEBAR_COLLAPSED_WIDTH = 60;

const SPRING = {
  type: "spring" as const,
  stiffness: 400,
  damping: 35,
  mass: 0.8,
};

// ─── NavItemIcon ──────────────────────────────────────────────────────────────

interface NavItemIconProps {
  iconName: string;
  className?: string;
}

const NavItemIcon = memo(function NavItemIcon({
  iconName,
  className,
}: NavItemIconProps) {
  const Icon = ICON_MAP[iconName as IconName] ?? LayoutDashboard;
  return <Icon size={18} className={className} aria-hidden="true" />;
});

// ─── ComingSoonBadge ──────────────────────────────────────────────────────────

const ComingSoonBadge = memo(function ComingSoonBadge() {
  return (
    <span
      className={cn(
        "inline-flex items-center shrink-0",
        "px-1.5 py-0.5 rounded",
        "text-[9px] font-semibold leading-none tracking-wide uppercase",
        "bg-[var(--color-bg-surface-elevated)] text-[var(--color-text-muted)]",
        "border border-[var(--color-border)]",
      )}
      aria-label="Coming soon"
    >
      Soon
    </span>
  );
});

// ─── NavItemButton ────────────────────────────────────────────────────────────

interface NavItemButtonProps {
  item: NavItem;
  isActive: boolean;
  isExpanded: boolean;
}

const NavItemButton = memo(function NavItemButton({
  item,
  isActive,
  isExpanded,
}: NavItemButtonProps) {
  const isDisabled = !item.enabled;

  const inner = (
    <span
      className={cn(
        "group relative flex items-center gap-3 w-full",
        "px-3 py-2.5 rounded-[var(--radius-lg)]",
        "text-sm font-medium",
        "transition-all duration-150 ease-out",
        "outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--color-bg-surface)]",
        isActive && !isDisabled && [
          "bg-[var(--color-primary-muted)]",
          "text-[var(--color-primary)]",
          "shadow-[inset_0_0_0_1px_var(--color-primary-muted)]",
        ],
        !isActive && !isDisabled && [
          "text-[var(--color-text-secondary)]",
          "hover:bg-[var(--color-bg-surface-elevated)]",
          "hover:text-[var(--color-text-primary)]",
        ],
        isDisabled && [
          "opacity-40 cursor-not-allowed",
          "text-[var(--color-text-tertiary)]",
        ],
        !isExpanded && "justify-center px-0",
      )}
      aria-current={isActive && !isDisabled ? "page" : undefined}
    >
      {/* Active indicator bar */}
      {isActive && !isDisabled && isExpanded && (
        <span
          className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-[var(--color-primary)]"
          aria-hidden="true"
        />
      )}

      <NavItemIcon
        iconName={item.icon}
        className={cn(
          "shrink-0 transition-colors duration-150",
          isActive && !isDisabled
            ? "text-[var(--color-primary)]"
            : "text-[var(--color-text-tertiary)] group-hover:text-[var(--color-text-secondary)]",
          isDisabled && "text-[var(--color-text-muted)]",
        )}
      />

      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.span
            key="label"
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: "auto" }}
            exit={{ opacity: 0, width: 0 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="flex items-center gap-2 overflow-hidden whitespace-nowrap flex-1 min-w-0"
          >
            <span className="truncate">{item.label}</span>
            {isDisabled && <ComingSoonBadge />}
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  );

  if (isDisabled) {
    return (
      <span
        role="menuitem"
        aria-disabled="true"
        tabIndex={-1}
        className="block w-full select-none"
        title={isExpanded ? undefined : `${item.label} — Coming Soon`}
      >
        {inner}
      </span>
    );
  }

  return (
    <Link
      href={item.href}
      role="menuitem"
      tabIndex={0}
      className="block w-full"
      aria-label={item.label}
    >
      {inner}
    </Link>
  );
});

// ─── TooltipNavItem ───────────────────────────────────────────────────────────

interface TooltipNavItemProps {
  item: NavItem;
  isActive: boolean;
  isExpanded: boolean;
}

const TooltipNavItem = memo(function TooltipNavItem({
  item,
  isActive,
  isExpanded,
}: TooltipNavItemProps) {
  if (isExpanded) {
    return (
      <NavItemButton item={item} isActive={isActive} isExpanded={isExpanded} />
    );
  }

  return (
    <Tooltip.Provider delayDuration={300} disableHoverableContent>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <span className="block w-full">
            <NavItemButton
              item={item}
              isActive={isActive}
              isExpanded={isExpanded}
            />
          </span>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            side="right"
            sideOffset={10}
            className={cn(
              "z-[var(--z-tooltip)]",
              "flex items-center gap-2",
              "px-3 py-1.5 rounded-[var(--radius-lg)]",
              "bg-[var(--color-bg-surface-elevated)] border border-[var(--color-border)]",
              "text-xs font-medium text-[var(--color-text-primary)]",
              "shadow-[var(--shadow-lg)]",
              "select-none",
              "animate-fade-in",
            )}
          >
            {item.label}
            {!item.enabled && (
              <span className="text-[var(--color-text-muted)] text-[10px]">
                Coming Soon
              </span>
            )}
            <Tooltip.Arrow className="fill-[var(--color-border)]" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
});

// ─── Sidebar ──────────────────────────────────────────────────────────────────

export const Sidebar = memo(function Sidebar() {
  const pathname = usePathname();
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);

  const activeItems = useMemo(
    () => NAV_ITEMS.filter((item) => item.enabled),
    [],
  );
  const disabledItems = useMemo(
    () => NAV_ITEMS.filter((item) => !item.enabled),
    [],
  );

  const isActive = useCallback(
    (href: string) => pathname === href || pathname.startsWith(href + "/"),
    [pathname],
  );

  const sidebarWidth = sidebarOpen
    ? SIDEBAR_EXPANDED_WIDTH
    : SIDEBAR_COLLAPSED_WIDTH;

  return (
    <motion.aside
      animate={{ width: sidebarWidth }}
      transition={SPRING}
      className={cn(
        "fixed left-0 top-0 bottom-0 z-[var(--z-sticky)]",
        "flex flex-col",
        "bg-[var(--color-bg-surface)]",
        "border-r border-[var(--color-border)]",
        "overflow-hidden",
      )}
      style={{ width: sidebarWidth }}
      aria-label="Main navigation"
    >
      {/* ── Logo ─────────────────────────────────────────────────────── */}
      <div
        className={cn(
          "flex items-center shrink-0 h-[var(--topbar-height)]",
          "border-b border-[var(--color-border)]",
          "px-3",
          sidebarOpen ? "gap-2.5" : "justify-center",
        )}
      >
        <span
          className={cn(
            "flex items-center justify-center shrink-0",
            "w-7 h-7 rounded-[var(--radius-lg)]",
            "bg-[var(--color-primary-muted)]",
          )}
          aria-hidden="true"
        >
          <Code2
            size={16}
            className="text-[var(--color-primary)]"
            aria-hidden="true"
          />
        </span>

        <AnimatePresence initial={false}>
          {sidebarOpen && (
            <motion.span
              key="app-name"
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "auto" }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.15, ease: "easeOut" }}
              className="overflow-hidden whitespace-nowrap"
            >
              <span className="text-sm font-bold tracking-tight text-[var(--color-text-primary)]">
                {APP_NAME}
              </span>
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* ── Navigation ───────────────────────────────────────────────── */}
      <nav
        role="navigation"
        aria-label="Primary navigation"
        className="flex-1 overflow-y-auto overflow-x-hidden py-3 px-2"
      >
        {/* Active items */}
        <ul role="menu" className="flex flex-col gap-0.5" aria-label="Main pages">
          {activeItems.map((item) => (
            <li key={item.href} role="none">
              <TooltipNavItem
                item={item}
                isActive={isActive(item.href)}
                isExpanded={sidebarOpen}
              />
            </li>
          ))}
        </ul>

        {/* Divider (only when there are disabled/future items) */}
        {disabledItems.length > 0 && (
          <>
            <div
              className="my-3 mx-1 h-px bg-[var(--color-border)]"
              role="separator"
              aria-orientation="horizontal"
            />

            {sidebarOpen && (
              <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-muted)]">
                Coming Soon
              </p>
            )}

            {/* Disabled/future items */}
            <ul
              role="menu"
              className="flex flex-col gap-0.5"
              aria-label="Future pages"
            >
              {disabledItems.map((item) => (
                <li key={item.href} role="none">
                  <TooltipNavItem
                    item={item}
                    isActive={false}
                    isExpanded={sidebarOpen}
                  />
                </li>
              ))}
            </ul>
          </>
        )}
      </nav>

      {/* ── Collapse toggle ───────────────────────────────────────────── */}
      <div
        className={cn(
          "shrink-0 border-t border-[var(--color-border)] p-2",
          sidebarOpen ? "flex justify-end" : "flex justify-center",
        )}
      >
        <button
          type="button"
          onClick={toggleSidebar}
          aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          aria-expanded={sidebarOpen}
          className={cn(
            "flex items-center justify-center",
            "w-8 h-8 rounded-[var(--radius-lg)]",
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
          {sidebarOpen ? (
            <ChevronLeft size={16} aria-hidden="true" />
          ) : (
            <ChevronRight size={16} aria-hidden="true" />
          )}
        </button>
      </div>
    </motion.aside>
  );
});

export default Sidebar;
