"use client";

import React from "react";
import { motion } from "framer-motion";

interface OrbitDot {
  size?: number;
  color?: string;
  opacity?: number;
}

interface OrbitRingProps {
  /** Diameter of the orbit circle in px */
  diameter: number;
  /** How long one full revolution takes in seconds */
  duration?: number;
  /** Number of dots on this ring */
  dots?: number;
  dotProps?: OrbitDot;
  /** Whether to reverse direction */
  reverse?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

export function OrbitRing({
  diameter,
  duration = 6,
  dots = 3,
  dotProps = {},
  reverse = false,
  className = "",
  style,
}: OrbitRingProps) {
  const {
    size: dotSize = 4,
    color: dotColor = "#00F0FF",
    opacity: dotOpacity = 0.9,
  } = dotProps;

  const r = diameter / 2;

  return (
    <div
      className={`absolute pointer-events-none ${className}`}
      style={{ width: diameter, height: diameter, ...style }}
    >
      {/* The ring track (faint) */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          border: `1px solid ${dotColor}22`,
        }}
        aria-hidden="true"
      />

      {/* Rotating layer */}
      <motion.div
        className="absolute inset-0"
        animate={{ rotate: reverse ? -360 : 360 }}
        transition={{ duration, repeat: Infinity, ease: "linear" }}
        aria-hidden="true"
      >
        {Array.from({ length: dots }).map((_, i) => {
          const angle = (i / dots) * 360;
          const rad = (angle * Math.PI) / 180;
          const x = r + r * Math.cos(rad) - dotSize / 2;
          const y = r + r * Math.sin(rad) - dotSize / 2;
          return (
            <span
              key={i}
              className="absolute rounded-full"
              style={{
                width: dotSize,
                height: dotSize,
                left: x,
                top: y,
                backgroundColor: dotColor,
                opacity: dotOpacity,
                boxShadow: `0 0 ${dotSize * 2}px ${dotColor}, 0 0 ${dotSize * 4}px ${dotColor}55`,
              }}
            />
          );
        })}
      </motion.div>
    </div>
  );
}
