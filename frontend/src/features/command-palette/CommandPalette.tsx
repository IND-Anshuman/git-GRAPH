'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { Command } from 'cmdk';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Boxes,
  Search,
  RefreshCw,
  Sliders,
  CornerDownLeft,
} from 'lucide-react';
import { useCommandPaletteStore, useUIStore } from '@/stores';
import { useKeyboardShortcut } from '@/hooks/useKeyboardShortcut';
import { cn } from '@/lib/utils';

export default function CommandPalette() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const isOpen = useCommandPaletteStore((s) => s.isOpen);
  const closePalette = useCommandPaletteStore((s) => s.close);
  const openSearch = useCommandPaletteStore((s) => s.openSearch);
  const recentCommands = useCommandPaletteStore((s) => s.recentCommands);
  const recordExecution = useCommandPaletteStore((s) => s.recordCommandExecution);

  const toggleSidebar = useUIStore((s) => s.toggleSidebar);

  const [search, setSearch] = useState('');

  // Setup Ctrl+K toggle shortcut
  useKeyboardShortcut({ key: 'k', ctrlKey: true }, (e) => {
    e.preventDefault();
    if (isOpen) closePalette();
    else useCommandPaletteStore.getState().open();
  });

  // Base list of commands
  const allCommands = useMemo(() => {
    return [
      {
        id: 'goto-dashboard',
        label: 'Go to Dashboard',
        category: 'Navigation',
        icon: LayoutDashboard,
        action: () => router.push('/dashboard'),
      },
      {
        id: 'goto-capabilities',
        label: 'Go to Capabilities',
        category: 'Navigation',
        icon: Boxes,
        action: () => router.push('/capabilities'),
      },
      {
        id: 'open-search',
        label: 'Open Global Search',
        category: 'Actions',
        icon: Search,
        action: () => openSearch(),
      },
      {
        id: 'refresh-data',
        label: 'Refresh Platform Data',
        category: 'Actions',
        icon: RefreshCw,
        action: () => {
          void queryClient.invalidateQueries();
        },
      },
      {
        id: 'toggle-sidebar',
        label: 'Toggle Navigation Sidebar',
        category: 'UI',
        icon: Sliders,
        action: () => toggleSidebar(),
      },
    ];
  }, [router, openSearch, queryClient, toggleSidebar]);

  // Sort and prioritize commands based on execution history
  const prioritizedCommands = useMemo(() => {
    return [...allCommands].sort((a, b) => {
      const recA = recentCommands.find((r) => r.id === a.id);
      const recB = recentCommands.find((r) => r.id === b.id);

      // Check recency (within 7 days)
      const sevenDays = 7 * 24 * 60 * 60 * 1000;
      const now = Date.now();
      const isRecentA = recA && now - recA.lastExecuted < sevenDays;
      const isRecentB = recB && now - recB.lastExecuted < sevenDays;

      if (isRecentA && !isRecentB) return -1;
      if (!isRecentA && isRecentB) return 1;

      // Check frequency (executed >= 5 times)
      const isFreqA = recA && recA.executionCount >= 5;
      const isFreqB = recB && recB.executionCount >= 5;

      if (isFreqA && !isFreqB) return -1;
      if (!isFreqA && isFreqB) return 1;

      // Fallback: sort by category then alphabetically
      if (a.category !== b.category) {
        return a.category.localeCompare(b.category);
      }
      return a.label.localeCompare(b.label);
    });
  }, [allCommands, recentCommands]);

  const handleSelectCommand = (id: string, label: string, action: () => void) => {
    recordExecution(id, label);
    action();
    // Close after delay for execution visual feedback
    setTimeout(() => {
      closePalette();
    }, 150);
  };

  // Grouped commands
  const groupedCommands = useMemo(() => {
    const groups: Record<string, typeof prioritizedCommands> = {};
    prioritizedCommands.forEach((cmd) => {
      if (!groups[cmd.category]) {
        groups[cmd.category] = [];
      }
      groups[cmd.category].push(cmd);
    });
    return groups;
  }, [prioritizedCommands]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[var(--z-modal)] flex items-start justify-center pt-[15vh] px-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closePalette}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* cmdk Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="relative w-full max-w-lg bg-[#111318] border border-[var(--color-border)] rounded-xl shadow-[var(--shadow-2xl)] overflow-hidden"
          >
            <Command
              label="Command Palette"
              value={search}
              onValueChange={setSearch}
              className="flex flex-col w-full"
            >
              {/* Input */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--color-border)]">
                <Search className="w-4 h-4 text-sip-text-tertiary shrink-0" />
                <Command.Input
                  placeholder="Type a command or search actions..."
                  className="w-full bg-transparent text-sm outline-none text-sip-text-primary placeholder:text-sip-text-tertiary border-none"
                />
              </div>

              {/* List */}
              <Command.List className="max-h-[280px] overflow-y-auto p-2 flex flex-col gap-0.5">
                <Command.Empty className="py-6 text-center text-xs text-sip-text-tertiary">
                  No commands found.
                </Command.Empty>

                {Object.entries(groupedCommands).map(([category, cmds]) => (
                  <Command.Group
                    key={category}
                    heading={category}
                    className="flex flex-col"
                  >
                    {/* Header */}
                    <div className="px-3 py-1.5 text-[9px] font-bold text-sip-text-tertiary uppercase tracking-wider">
                      {category}
                    </div>

                    {cmds.map((cmd) => {
                      const Icon = cmd.icon;
                      return (
                        <Command.Item
                          key={cmd.id}
                          value={`${cmd.category} ${cmd.label}`}
                          onSelect={() => handleSelectCommand(cmd.id, cmd.label, cmd.action)}
                          className={cn(
                            'flex items-center justify-between px-3 py-2 text-xs font-semibold rounded-md cursor-pointer select-none outline-none transition-colors duration-100',
                            'aria-selected:bg-[#161A22] aria-selected:text-[var(--color-primary)] text-sip-text-secondary'
                          )}
                        >
                          <div className="flex items-center gap-3 truncate">
                            <Icon size={14} className="text-sip-text-tertiary shrink-0" />
                            <span className="truncate">{cmd.label}</span>
                          </div>
                          {/* Show execution badge if frequented */}
                          {recentCommands.some((r) => r.id === cmd.id && r.executionCount >= 3) && (
                            <span className="text-[8px] bg-sip-surface border border-[var(--color-border)] px-1.5 py-0.2 rounded font-mono text-sip-text-muted shrink-0">
                              frequent
                            </span>
                          )}
                        </Command.Item>
                      );
                    })}
                  </Command.Group>
                ))}
              </Command.List>

              {/* Footer */}
              <div className="px-4 py-2 border-t border-[var(--color-border)] bg-[#0d0f14] flex items-center justify-between text-[10px] text-sip-text-muted">
                <span>Press <kbd className="font-mono text-sip-text-secondary bg-[#161A22] px-1 rounded">ESC</kbd> to close</span>
                <div className="flex items-center gap-1 font-mono">
                  <span>navigate with arrows</span>
                  <CornerDownLeft size={10} className="ml-1" />
                  <span>enter to run</span>
                </div>
              </div>
            </Command>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
