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
        'flex flex-col items-center justify-center text-center p-8 border border-dashed rounded-lg bg-sip-surface/40',
        'border-[var(--color-border)] min-h-[280px] w-full',
        className
      )}
    >
      {icon && (
        <div className="mb-4 text-sip-text-tertiary/75 flex items-center justify-center">
          {icon}
        </div>
      )}
      <h3 className="text-sm font-semibold text-sip-text-primary tracking-tight mb-1">
        {title}
      </h3>
      {description && (
        <p className="text-xs text-sip-text-secondary max-w-sm leading-relaxed mb-4">
          {description}
        </p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          type="button"
          className={cn(
            'px-3.5 py-1.5 text-xs font-medium rounded-md text-white bg-[var(--color-primary)]',
            'hover:bg-[var(--color-primary)]/90 transition-all duration-150',
            'focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50 focus:ring-offset-2 focus:ring-offset-[#090B10]'
          )}
        >
          {action.label}
        </button>
      )}
    </motion.div>
  );
}
