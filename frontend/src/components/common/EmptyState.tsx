'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export default function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className={cn(
        'flex flex-col items-center justify-center text-center p-8 border border-dashed rounded-[var(--radius-2xl)]',
        'bg-[var(--color-bg-surface)]/45 border-[var(--color-border)] min-h-[280px] w-full shadow-[var(--shadow-lg)] backdrop-blur-sm',
        className
      )}
    >
      {icon && (
        <div className="mb-4 text-sip-text-tertiary/75 flex items-center justify-center">
          {icon}
        </div>
      )}
      <h3 className="text-base font-semibold text-sip-text-primary tracking-tight mb-1">
        {title}
      </h3>
      {description && (
        <p className="text-sm text-sip-text-secondary max-w-sm leading-relaxed mb-4">
          {description}
        </p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          type="button"
          className={cn(
          'px-3.5 py-1.5 text-sm font-medium rounded-xl text-[var(--color-text-inverse)] bg-[var(--color-primary)]',
          'hover:bg-[var(--color-primary-hover)] transition-all duration-150 shadow-[var(--shadow-glow)]',
          'focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50 focus:ring-offset-2 focus:ring-offset-[#070A12]'
        )}
        >
          {action.label}
        </button>
      )}
    </motion.div>
  );
}
