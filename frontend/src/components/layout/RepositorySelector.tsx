'use client';

import React from 'react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { ChevronDown, GitBranch, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Repository } from '@/types/platform';

interface RepositorySelectorProps {
  repositories: Repository[];
  activeRepo: Repository | null;
  onSelect: (id: string) => void;
}

export const RepositorySelector = React.memo<RepositorySelectorProps>(
  function RepositorySelector({ repositories, activeRepo, onSelect }) {
    return (
      <DropdownMenu.Root>
        <DropdownMenu.Trigger asChild>
          <button
            type="button"
            className={cn(
              'flex items-center gap-2 h-10 px-3.5 rounded-[var(--radius-xl)]',
              'bg-[var(--color-bg-surface)]/90 border border-[var(--color-border)] shadow-[var(--shadow-sm)]',
              'text-sip-text-primary text-xs font-semibold select-none',
              'hover:bg-[var(--color-bg-surface-elevated)] hover:border-[var(--color-border-strong)]',
              'transition-all duration-150 ease-out',
              'focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-1 focus:ring-offset-[var(--color-bg-surface)]'
            )}
            aria-label="Select repository"
          >
            <GitBranch size={14} className="text-[var(--color-primary)] shrink-0" />
            <span className="truncate max-w-[120px] sm:max-w-[180px]">
              {activeRepo ? activeRepo.name : 'Select Repository...'}
            </span>
            <ChevronDown size={12} className="text-sip-text-tertiary shrink-0 ml-1" />
          </button>
        </DropdownMenu.Trigger>

        <DropdownMenu.Portal>
          <DropdownMenu.Content
            align="start"
            sideOffset={4}
            className={cn(
              'z-[var(--z-dropdown)] min-w-[220px] max-w-[320px] p-1.5 rounded-[var(--radius-2xl)]',
              'bg-[rgba(13,18,31,0.98)] border border-[var(--color-border)] shadow-[var(--shadow-xl)] backdrop-blur-xl',
              'animate-fade-in'
            )}
          >
            <DropdownMenu.Label className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-sip-text-tertiary">
              Repositories
            </DropdownMenu.Label>

            {repositories.length === 0 ? (
              <div className="px-2 py-3 text-xs text-sip-text-muted text-center">
                No repositories found
              </div>
            ) : (
              repositories.map((repo) => {
                const isSelected = activeRepo?.id === repo.id;
                return (
                  <DropdownMenu.Item
                    key={repo.id}
                    onClick={() => onSelect(repo.id)}
                    className={cn(
                      'flex items-center justify-between px-2.5 py-2.5 text-xs font-medium rounded-xl cursor-pointer outline-none select-none',
                      'text-sip-text-secondary hover:text-sip-text-primary hover:bg-[#222938]',
                      isSelected && 'text-[var(--color-primary)] bg-[var(--color-primary-muted)] hover:bg-[var(--color-primary-muted)]'
                    )}
                  >
                    <div className="flex flex-col min-w-0 mr-2">
                      <span className="truncate text-sip-text-primary font-semibold">
                        {repo.name}
                      </span>
                      <span className="truncate text-[10px] text-sip-text-muted">
                        {repo.default_branch}
                      </span>
                    </div>
                    {isSelected && <Check size={14} className="text-[var(--color-primary)] shrink-0" />}
                  </DropdownMenu.Item>
                );
              })
            )}
          </DropdownMenu.Content>
        </DropdownMenu.Portal>
      </DropdownMenu.Root>
    );
  }
);

RepositorySelector.displayName = 'RepositorySelector';
