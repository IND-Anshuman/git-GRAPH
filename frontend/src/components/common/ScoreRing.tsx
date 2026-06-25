'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import AnimatedCounter from './AnimatedCounter';
import { OrbitRing } from './OrbitRing';

// ─── Types ──────────────────────────────────────────────────────────────────

interface ScoreRingProps {
  /** Score value between 0 and 100 (inclusive). */
  score: number;
  /** Diameter of the SVG in pixels. @default 64 */
  size?: number;
  /** Width of the progress stroke. @default 5 */
  strokeWidth?: number;
  /** Optional accessible label for the ring. Falls back to "Score: {score}" */
  label?: string;
  /** Override the ring color with any valid CSS color string. */
  colorOverride?: string;
  /** Show orbiting particle rings around the score. */
  orbiting?: boolean;
  className?: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Returns the CSS variable token matching the score bracket:
 *   ≥ 80 → success  |  ≥ 60 → warning  |  ≥ 40 → orange  |  < 40 → danger
 */
function resolveScoreColor(score: number): string {
  if (score >= 80) return 'var(--color-success)';
  if (score >= 60) return 'var(--color-warning)';
  if (score >= 40) return '#F97316'; // orange-500 — no design-system variable for orange
  return 'var(--color-danger)';
}

// ─── Component ───────────────────────────────────────────────────────────────

const ScoreRing = React.memo<ScoreRingProps>(function ScoreRing({
  score,
  size = 64,
  strokeWidth = 5,
  label,
  colorOverride,
  orbiting = false,
  className,
}) {
  const clampedScore = Math.max(0, Math.min(100, Math.round(score)));
  const color = colorOverride ?? resolveScoreColor(clampedScore);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;

  // dashoffset: full circumference = empty ring, 0 = full ring
  const targetOffset = useMemo(
    () => circumference - (clampedScore / 100) * circumference,
    [circumference, clampedScore],
  );

  const ariaLabel = label ?? `Score: ${clampedScore} out of 100`;

  // Font size scales proportionally with the ring diameter
  const fontSize = Math.max(10, Math.round(size * 0.265));

  return (
    <motion.div
      className={cn('relative inline-flex items-center justify-center flex-shrink-0', className)}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.35, ease: [0, 0, 0.58, 1] }}
      role="img"
      aria-label={ariaLabel}
    >
      {/* Outer orbiting rings (optional) */}
      {orbiting && (
        <>
          <OrbitRing
            diameter={size + 28}
            duration={8}
            dots={2}
            dotProps={{ size: 3, color: color, opacity: 0.9 }}
            className="absolute"
            style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}
          />
          <OrbitRing
            diameter={size + 50}
            duration={14}
            dots={1}
            reverse
            dotProps={{ size: 2, color: '#B026FF', opacity: 0.7 }}
            className="absolute"
            style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}
          />
        </>
      )}

      {/* SVG rotated so arc starts at 12 o'clock */}
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        fill="none"
        aria-hidden="true"
        style={{ transform: 'rotate(-90deg)' }}
      >
        {/* Track ring */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke="var(--color-border)"
          strokeWidth={strokeWidth}
          fill="none"
        />

        {/* Progress arc */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: targetOffset }}
          transition={{ duration: 0.65, ease: [0, 0, 0.58, 1], delay: 0.15 }}
          style={{ filter: `drop-shadow(0 0 4px ${color}66)` }}
        />
      </svg>

      {/* Numeric score centered inside the ring */}
      <span
        aria-hidden="true"
        style={{
          position: 'absolute',
          fontFamily: 'var(--font-mono)',
          fontSize: `${fontSize}px`,
          fontWeight: 600,
          color: 'var(--color-text-primary)',
          lineHeight: 1,
          letterSpacing: '-0.03em',
          userSelect: 'none',
        }}
      >
        <AnimatedCounter value={clampedScore} />
      </span>
    </motion.div>
  );
});

ScoreRing.displayName = 'ScoreRing';

export default ScoreRing;
export type { ScoreRingProps };
