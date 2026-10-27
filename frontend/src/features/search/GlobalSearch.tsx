'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDebounce } from '@/hooks/useDebounce';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Clock, CornerDownLeft, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useUIStore, useCommandPaletteStore, useSearchStore } from '@/stores';
import { capabilitiesApi } from '@/lib/api';
import type { CapabilityQueryResult } from '@/types/platform';
import { useKeyboardShortcut } from '@/hooks/useKeyboardShortcut';
import { cn } from '@/lib/utils';

export default function GlobalSearch() {
  const router = useRouter();
  const repositoryId = useUIStore((s) => s.activeRepositoryId);
  const setSelectedCapabilityId = useUIStore((s) => s.setSelectedCapabilityId);

  const isSearchOpen = useCommandPaletteStore((s) => s.isSearchOpen);
  const closeSearch = useCommandPaletteStore((s) => s.closeSearch);

  const recentSearches = useSearchStore((s) => s.recentSearches);
  const addRecentSearch = useSearchStore((s) => s.addRecentSearch);
  const clearRecentSearches = useSearchStore((s) => s.clearRecentSearches);

  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Start fresh each time the panel opens. Adjusting state during render
  // (instead of in an effect) avoids rendering the stale query first.
  const [wasOpen, setWasOpen] = useState(isSearchOpen);
  if (isSearchOpen !== wasOpen) {
    setWasOpen(isSearchOpen);
    if (isSearchOpen) {
      setQuery('');
      setActiveIndex(0);
    }
  }

  const trimmed = query.trim();
  const debounced = useDebounce(trimmed, 300);
  const searchQuery = useQuery({
    queryKey: ['capability-search', repositoryId, debounced],
    queryFn: () => capabilitiesApi.query(repositoryId!, { query_text: debounced, limit: 10 }),
    enabled: isSearchOpen && !!repositoryId && debounced.length >= 2,
    staleTime: 30_000,
  });
  const results: CapabilityQueryResult[] =
    trimmed.length >= 2 && debounced === trimmed ? (searchQuery.data?.results ?? []) : [];
  const isSearching = trimmed.length >= 2 && (debounced !== trimmed || searchQuery.isFetching);

  // Keyboard Navigation inside search
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeSearch();
      return;
    }

    const totalResults = query.trim().length < 2 ? recentSearches.length : results.length;
    if (totalResults === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => (prev + 1) % totalResults);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => (prev - 1 + totalResults) % totalResults);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (query.trim().length < 2) {
        // Run recent search query
        const recent = recentSearches[activeIndex];
        if (recent) setQuery(recent.query);
      } else {
        // Select capability result
        const selected = results[activeIndex];
        if (selected) {
          addRecentSearch(query, results.length);
          handleSelectCapability(selected.capability.id);
        }
      }
    }
  };

  const handleSelectCapability = (id: string) => {
    setSelectedCapabilityId(id);
    closeSearch();
    router.push('/capabilities');
  };

  // Keyboard shortcut listener to toggle search with Ctrl+Space or / (excluding focus inputs)
  useKeyboardShortcut({ key: '/' }, () => {
    // Only open if focus is not in an input
    const active = document.activeElement;
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) {
      return;
    }
    useCommandPaletteStore.getState().openSearch();
  });

  // Listen for Escape key globally if open
  useEffect(() => {
    const handleGlobalEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isSearchOpen) {
        closeSearch();
      }
    };
    window.addEventListener('keydown', handleGlobalEsc);
    return () => window.removeEventListener('keydown', handleGlobalEsc);
  }, [isSearchOpen, closeSearch]);

  return (
    <AnimatePresence>
      {isSearchOpen && (
        <div className="fixed inset-0 z-[var(--z-modal)] flex items-start justify-center pt-[10vh] px-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeSearch}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="relative w-full max-w-2xl bg-[#111318] border border-[var(--color-border)] rounded-xl shadow-[var(--shadow-2xl)] overflow-hidden flex flex-col"
            onKeyDown={handleKeyDown}
          >
            {/* Search Input Area */}
            <div className="flex items-center gap-3 px-4 py-3.5 border-b border-[var(--color-border)]">
              <Search className="w-4 h-4 text-sip-text-tertiary shrink-0" />
              <input
                ref={inputRef}
                type="text"
                autoFocus
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setActiveIndex(0);
                }}
                placeholder="Search capabilities, concepts, or behavioral signatures..."
                className="flex-1 bg-transparent border-none text-sm outline-none text-sip-text-primary placeholder:text-sip-text-tertiary"
              />
              {isSearching ? (
                <Loader2 className="w-4 h-4 text-sip-text-tertiary animate-spin shrink-0" />
              ) : query ? (
                <button
                  type="button"
                  onClick={() => setQuery('')}
                  className="p-1 hover:bg-[#161A22] rounded text-sip-text-tertiary hover:text-sip-text-primary"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              ) : null}
            </div>

            {/* Results Area */}
            <div className="flex-1 max-h-[360px] overflow-y-auto p-2">
              {/* Empty state & Query instructions */}
              {query.trim().length === 0 ? (
                /* Recent searches */
                recentSearches.length > 0 ? (
                  <div className="flex flex-col">
                    <div className="flex items-center justify-between px-3 py-1.5 text-[10px] font-bold text-sip-text-tertiary uppercase tracking-wider">
                      <span>Recent Searches</span>
                      <button
                        type="button"
                        onClick={clearRecentSearches}
                        className="hover:underline text-[9px]"
                      >
                        Clear
                      </button>
                    </div>
                    <ul className="flex flex-col gap-0.5">
                      {recentSearches.map((recent, idx) => {
                        const isFocused = activeIndex === idx;
                        return (
                          <li key={recent.query}>
                            <button
                              type="button"
                              onClick={() => setQuery(recent.query)}
                              className={cn(
                                'w-full flex items-center justify-between px-3 py-2 text-xs text-left rounded-md transition-colors',
                                isFocused ? 'bg-[#161A22] text-sip-text-primary' : 'text-sip-text-secondary hover:bg-[#161A22]/40'
                              )}
                            >
                              <div className="flex items-center gap-2 truncate">
                                <Clock className="w-3.5 h-3.5 text-sip-text-tertiary shrink-0" />
                                <span className="truncate">{recent.query}</span>
                              </div>
                              <span className="text-[10px] text-sip-text-muted shrink-0">
                                {recent.resultCount} results
                              </span>
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ) : (
                  <div className="py-8 text-center text-xs text-sip-text-tertiary">
                    Type 2 or more characters to query capabilities...
                  </div>
                )
              ) : results.length > 0 ? (
                /* Query results list */
                <div className="flex flex-col">
                  <div className="px-3 py-1.5 text-[10px] font-bold text-sip-text-tertiary uppercase tracking-wider">
                    Capabilities Resolved ({results.length})
                  </div>
                  <ul className="flex flex-col gap-0.5">
                    {results.map((result, idx) => {
                      const isFocused = activeIndex === idx;
                      const score = Math.round(result.relevance_score * 100);

                      return (
                        <li key={result.capability.id}>
                          <button
                            type="button"
                            onClick={() => handleSelectCapability(result.capability.id)}
                            className={cn(
                              'w-full flex items-start justify-between px-3 py-2 rounded-md text-left transition-colors',
                              isFocused ? 'bg-[#161A22]' : 'hover:bg-[#161A22]/40'
                            )}
                          >
                            <div className="flex flex-col min-w-0 pr-4">
                              <span className={cn(
                                'text-xs font-bold transition-colors',
                                isFocused ? 'text-[var(--color-primary)]' : 'text-sip-text-primary'
                              )}>
                                {result.capability.name}
                              </span>
                              <span className="text-[10px] text-sip-text-secondary truncate mt-0.5">
                                {result.capability.description || 'No description resolved.'}
                              </span>
                            </div>

                            <div className="flex items-center gap-3 shrink-0 mt-0.5">
                              <span className="text-[10px] font-mono bg-sip-surface border border-[var(--color-border)] px-1 rounded text-sip-text-secondary font-bold">
                                {score}% match
                              </span>
                            </div>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : !isSearching ? (
                <div className="py-8 text-center text-xs text-sip-text-tertiary">
                  No matching capabilities found for &ldquo;{query}&rdquo;
                </div>
              ) : null}
            </div>

            {/* Footer tips */}
            <div className="px-4 py-2 border-t border-[var(--color-border)] bg-[#0d0f14] flex items-center justify-between text-[10px] text-sip-text-muted">
              <span>Press <kbd className="font-mono text-sip-text-secondary bg-[#161A22] px-1 rounded">ESC</kbd> to close</span>
              <div className="flex items-center gap-3 font-mono">
                <span>↑↓ to navigate</span>
                <span className="flex items-center gap-0.5">
                  <CornerDownLeft size={10} /> enter to select
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
