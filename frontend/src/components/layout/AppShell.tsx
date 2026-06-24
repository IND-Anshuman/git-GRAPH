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

  // Auto-select first repository if none selected
  useEffect(() => {
    if (repositories.length > 0 && !activeRepositoryId) {
      setActiveRepositoryId(repositories[0].id);
    }
  }, [repositories, activeRepositoryId, setActiveRepositoryId]);

  const currentSidebarWidth = sidebarOpen ? 220 : 60;

  return (
    <div className="min-h-screen bg-sip-bg-base text-sip-text-primary flex">
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
        className="flex flex-col flex-1 min-w-0 transition-[padding-left] duration-300 ease-out"
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
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-var(--topbar-height))] gap-3">
              <LoadingSpinner size="lg" />
              <p className="text-xs text-sip-text-secondary tracking-wider font-mono">
                RESOLVING SEMANTIC LAYERS...
              </p>
            </div>
          ) : isError ? (
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-var(--topbar-height))] p-6 text-center">
              <div className="p-3 bg-[var(--color-danger)]/10 text-[var(--color-danger)] rounded-full mb-4 border border-[var(--color-danger)]/20 animate-pulse">
                ⚠️
              </div>
              <h2 className="text-base font-bold text-sip-text-primary mb-1">
                Failed to Connect to Backend
              </h2>
              <p className="text-xs text-sip-text-secondary max-w-sm mb-4">
                Ensure the FastAPI application is running at <code className="font-mono text-sip-text-primary">http://localhost:8000/api/v1</code>.
              </p>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-4 py-2 text-xs font-semibold rounded-md text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90"
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
