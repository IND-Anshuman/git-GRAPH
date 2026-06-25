'use client';

import React, { useRef } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface SpotlightCardProps extends HTMLMotionProps<'div'> {
  children: React.ReactNode;
  className?: string;
  glowColor?: string;
  /** Show animated corner brackets (cyber HUD style) */
  cornerBrackets?: boolean;
}

export default function SpotlightCard({
  children,
  className,
  glowColor = 'rgba(0, 240, 255, 0.2)',
  cornerBrackets = false,
  ...props
}: SpotlightCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    cardRef.current.style.setProperty('--mouse-x', `${x}px`);
    cardRef.current.style.setProperty('--mouse-y', `${y}px`);
  };

  const bracketColor = glowColor;

  return (
    <motion.div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      className={cn(
        'spotlight-card relative rounded-[var(--radius-2xl)] overflow-hidden transition-all duration-300',
        'bg-[rgba(12,12,30,0.55)] backdrop-blur-xl',
        'border border-[rgba(0,240,255,0.1)]',
        'hover:border-[rgba(0,240,255,0.22)]',
        'hover:shadow-[0_0_32px_rgba(0,240,255,0.08),0_0_64px_rgba(0,240,255,0.04)]',
        className
      )}
      style={{
        ['--_glow-color' as any]: glowColor,
      }}
      {...props}
    >
      {/* Subtle inner cyber grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{
          backgroundImage:
            'linear-gradient(rgba(0,240,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.04) 1px, transparent 1px)',
          backgroundSize: '20px 20px',
        }}
        aria-hidden="true"
      />

      {/* Top-edge neon line */}
      <div
        className="absolute top-0 left-8 right-8 h-px pointer-events-none"
        style={{
          background: `linear-gradient(90deg, transparent, ${glowColor}, transparent)`,
          opacity: 0.5,
        }}
        aria-hidden="true"
      />

      {/* Corner brackets (HUD style) */}
      {cornerBrackets && (
        <>
          {/* Top-left */}
          <span className="absolute top-2 left-2 w-3 h-3 border-t border-l pointer-events-none" style={{ borderColor: bracketColor }} aria-hidden="true" />
          {/* Top-right */}
          <span className="absolute top-2 right-2 w-3 h-3 border-t border-r pointer-events-none" style={{ borderColor: bracketColor }} aria-hidden="true" />
          {/* Bottom-left */}
          <span className="absolute bottom-2 left-2 w-3 h-3 border-b border-l pointer-events-none" style={{ borderColor: bracketColor }} aria-hidden="true" />
          {/* Bottom-right */}
          <span className="absolute bottom-2 right-2 w-3 h-3 border-b border-r pointer-events-none" style={{ borderColor: bracketColor }} aria-hidden="true" />
        </>
      )}

      <div className="relative z-10 h-full flex flex-col justify-between">
        {children}
      </div>
    </motion.div>
  );
}
