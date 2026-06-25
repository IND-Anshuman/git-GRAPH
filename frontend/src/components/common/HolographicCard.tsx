"use client";

import { useRef, ReactNode, useCallback } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";

interface HolographicCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: string;
  tiltStrength?: number;
  disabled?: boolean;
}

export function HolographicCard({
  children,
  className = "",
  glowColor = "rgba(0, 240, 255, 0.25)",
  tiltStrength = 10,
  disabled = false,
}: HolographicCardProps) {
  const ref = useRef<HTMLDivElement>(null);

  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);

  const springConfig = { damping: 20, stiffness: 200 };
  const rotateX = useSpring(
    useTransform(rawY, [-0.5, 0.5], [tiltStrength, -tiltStrength]),
    springConfig,
  );
  const rotateY = useSpring(
    useTransform(rawX, [-0.5, 0.5], [-tiltStrength, tiltStrength]),
    springConfig,
  );
  const glowX = useSpring(
    useTransform(rawX, [-0.5, 0.5], [0, 100]),
    { damping: 25, stiffness: 150 },
  );
  const glowY = useSpring(
    useTransform(rawY, [-0.5, 0.5], [0, 100]),
    { damping: 25, stiffness: 150 },
  );

  // Derive spotlight gradient string from glowX / glowY motion values
  const spotlightBg = useTransform(
    [glowX, glowY],
    ([x, y]: number[]) =>
      `radial-gradient(circle at ${x}% ${y}%, ${glowColor}, transparent 60%)`,
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (disabled || !ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      rawX.set((e.clientX - rect.left) / rect.width - 0.5);
      rawY.set((e.clientY - rect.top) / rect.height - 0.5);
    },
    [disabled, rawX, rawY],
  );

  const handleMouseLeave = useCallback(() => {
    rawX.set(0);
    rawY.set(0);
  }, [rawX, rawY]);

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={disabled ? {} : { rotateX, rotateY, transformStyle: "preserve-3d" }}
      className={cn(
        "relative rounded-xl overflow-hidden",
        "bg-[rgba(18,18,46,0.6)] backdrop-blur-xl",
        "border border-[rgba(0,240,255,0.12)]",
        "transition-shadow duration-300",
        "hover:shadow-[0_0_30px_rgba(0,240,255,0.12),0_0_60px_rgba(0,240,255,0.06)]",
        className,
      )}
    >
      {/* Spotlight glow following mouse */}
      {!disabled && (
        <motion.div
          className="pointer-events-none absolute inset-0 rounded-xl"
          style={{ background: spotlightBg, opacity: 0.8 }}
          aria-hidden="true"
        />
      )}

      {/* Animated top edge light streak */}
      <div
        className="absolute top-0 left-0 right-0 h-px pointer-events-none"
        style={{
          background: `linear-gradient(90deg, transparent, ${glowColor}, transparent)`,
          opacity: 0.6,
        }}
        aria-hidden="true"
      />

      {/* Content */}
      <div style={{ transform: "translateZ(8px)" }}>{children}</div>
    </motion.div>
  );
}
