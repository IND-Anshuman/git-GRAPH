'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/stores';
import { useRepositories } from '@/hooks/useRepositories';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import LoadingSpinner from '../common/LoadingSpinner';
import GlobalSearch from '@/features/search/GlobalSearch';
import CommandPalette from '@/features/command-palette/CommandPalette';

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);
  const activeRepositoryId = useUIStore((s) => s.activeRepositoryId);
  const setActiveRepositoryId = useUIStore((s) => s.setActiveRepositoryId);
  const reducedMotion = useUIStore((s) => s.reducedMotion);

  const { data: repositories = [], isLoading, isError } = useRepositories();

  // Auto-select first repository if none selected (prioritize one with files/entities)
  useEffect(() => {
    if (repositories.length > 0) {
      const exists = repositories.some((r) => r.id === activeRepositoryId);
      if (!activeRepositoryId || !exists) {
        // Sort repositories to prioritize those with higher entity_count or file_count
        const bestRepo = [...repositories].sort((a, b) => {
          const aCount = a.entity_count ?? 0;
          const bCount = b.entity_count ?? 0;
          if (bCount !== aCount) return bCount - aCount;
          
          const aFiles = a.file_count ?? 0;
          const bFiles = b.file_count ?? 0;
          return bFiles - aFiles;
        })[0];
        
        setActiveRepositoryId(bestRepo.id);
      }
    }
  }, [repositories, activeRepositoryId, setActiveRepositoryId]);

  const currentSidebarWidth = sidebarOpen ? 220 : 60;

  return (
    <div className="min-h-screen bg-sip-bg-base text-sip-text-primary flex relative overflow-hidden">
      {/* Ambient background effects — cyber neon aurora */}
      <div className="ambient-grid" />
      <div className="ambient-aurora-blue" />
      <div className="ambient-aurora-cyan" />
      <div className="ambient-aurora-purple" />
      {/* Subtle neon top vignette */}
      <div className="pointer-events-none fixed inset-x-0 top-0 h-24 bg-gradient-to-b from-[rgba(0,240,255,0.04)] to-transparent" />

      {/* Skip to Main Content Link (Accessibility WCAG) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 z-[999] px-4 py-2 bg-[var(--color-primary)] text-white font-semibold rounded-md shadow-lg outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--color-primary)]"
      >
        Skip to main content
      </a>

      {/* Sidebar Component */}
      <Sidebar />

      {/* Main Layout Area */}
      <div
        className="flex flex-col flex-1 min-w-0 transition-[padding-left] duration-300 ease-in-out"
        style={{
          paddingLeft: `${currentSidebarWidth}px`,
          // Set dynamic custom variable for topbar left offset
          ['--_sidebar-current-width' as any]: `${currentSidebarWidth}px`,
        }}
      >
        {/* TopBar Component */}
        <TopBar repositories={repositories} />

        {/* Content Container */}
        <main
          id="main-content"
          className="flex-1 mt-[var(--topbar-height)] overflow-y-auto outline-none"
          tabIndex={-1}
        >
          {isLoading ? (
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-var(--topbar-height))] gap-4">
              <div
                className="rounded-full p-4"
                style={{
                  background: 'rgba(0,240,255,0.06)',
                  border: '1px solid rgba(0,240,255,0.25)',
                  boxShadow: '0 0 20px rgba(0,240,255,0.15)',
                }}
              >
                <LoadingSpinner size="lg" />
              </div>
              <p
                className="text-[11px] tracking-[0.28em] uppercase font-mono"
                style={{ color: 'var(--neon-blue)', textShadow: '0 0 10px rgba(0,240,255,0.5)' }}
              >
                RESOLVING SEMANTIC LAYERS...
              </p>
            </div>
          ) : isError ? (
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-var(--topbar-height))] p-6 text-center">
              <div className="mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-[var(--color-danger)]/20 bg-[var(--color-danger)]/10 text-[var(--color-danger)] shadow-[var(--shadow-lg)]">
                !
              </div>
              <h2 className="text-lg font-bold text-sip-text-primary mb-2">
                Failed to Connect to Backend
              </h2>
              <p className="text-sm text-sip-text-secondary max-w-md mb-5 leading-relaxed">
                Ensure the FastAPI application is running at <code className="font-mono text-sip-text-primary">http://localhost:8000/api/v1</code> and try again.
              </p>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-4 py-2 text-sm font-semibold rounded-xl text-[var(--color-text-inverse)] bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] shadow-[var(--shadow-glow)] transition-colors"
              >
                Retry Connection
              </button>
            </div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div
                key="page-content"
                initial={reducedMotion ? { opacity: 1 } : { opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={reducedMotion ? { opacity: 1 } : { opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="h-full w-full"
              >
                {children}
              </motion.div>
            </AnimatePresence>
          )}
        </main>
      </div>

      {/* Global Modals */}
      <GlobalSearch />
      <CommandPalette />
    </div>
  );
}
