'use client';

import React from 'react';

interface MiniRadarChartProps {
  data: { label: string; value: number }[];
  size?: number;
  className?: string;
  color?: string;
}

export default function MiniRadarChart({
  data,
  size = 80,
  className = '',
  color = 'var(--neon-blue)',
}: MiniRadarChartProps) {
  if (!data || data.length === 0) {
    return null;
  }

  const center = size / 2;
  const radius = size / 2.5;
  const angleStep = (2 * Math.PI) / data.length;

  // Generate polygon points for the data
  const points = data
    .map((item, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const r = radius * item.value;
      const x = center + r * Math.cos(angle);
      const y = center + r * Math.sin(angle);
      return `${x},${y}`;
    })
    .join(' ');

  // Generate axis lines
  const axisLines = data.map((_, index) => {
    const angle = index * angleStep - Math.PI / 2;
    const x = center + radius * Math.cos(angle);
    const y = center + radius * Math.sin(angle);
    return (
      <line
        key={index}
        x1={center}
        y1={center}
        x2={x}
        y2={y}
        stroke="rgba(176,38,255,0.2)"
        strokeWidth="1"
      />
    );
  });

  // Generate concentric circles (3 levels)
  const circles = [0.33, 0.66, 1].map((level, idx) => (
    <circle
      key={idx}
      cx={center}
      cy={center}
      r={radius * level}
      fill="none"
      stroke="rgba(176,38,255,0.15)"
      strokeWidth="1"
    />
  ));

  return (
    <svg
      width={size}
      height={size}
      className={className}
      viewBox={`0 0 ${size} ${size}`}
    >
      <defs>
        <radialGradient id={`radarGradient-${color}`}>
          <stop offset="0%" stopColor={color} stopOpacity={0.3} />
          <stop offset="100%" stopColor={color} stopOpacity={0.05} />
        </radialGradient>
      </defs>

      {/* Background circles */}
      {circles}

      {/* Axis lines */}
      {axisLines}

      {/* Data polygon */}
      <polygon
        points={points}
        fill={`url(#radarGradient-${color})`}
        stroke={color}
        strokeWidth="2"
        strokeLinejoin="round"
        style={{
          filter: `drop-shadow(0 0 6px ${color})`,
        }}
      />

      {/* Data points */}
      {data.map((item, index) => {
        const angle = index * angleStep - Math.PI / 2;
        const r = radius * item.value;
        const x = center + r * Math.cos(angle);
        const y = center + r * Math.sin(angle);
        return (
          <circle
            key={index}
            cx={x}
            cy={y}
            r="2.5"
            fill={color}
            style={{
              filter: `drop-shadow(0 0 4px ${color})`,
            }}
          />
        );
      })}
    </svg>
  );
}
