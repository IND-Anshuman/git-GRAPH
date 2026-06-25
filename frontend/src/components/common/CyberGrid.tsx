"use client";

import { motion } from "framer-motion";

interface CyberGridProps {
  cellSize?: number;
  color?: string;
  animated?: boolean;
  perspective?: boolean;
  className?: string;
}

export function CyberGrid({
  cellSize = 50,
  color = "rgba(0, 240, 255, 0.1)",
  animated = true,
  perspective = false,
  className = "",
}: CyberGridProps) {
  return (
    <div
      className={`fixed inset-0 pointer-events-none ${className}`}
      style={{
        backgroundImage: `
          linear-gradient(${color} 1px, transparent 1px),
          linear-gradient(90deg, ${color} 1px, transparent 1px)
        `,
        backgroundSize: `${cellSize}px ${cellSize}px`,
        maskImage: perspective
          ? "radial-gradient(ellipse 80% 50% at 50% 100%, black 0%, transparent 80%)"
          : "radial-gradient(circle 900px at 50% 240px, black, transparent)",
        WebkitMaskImage: perspective
          ? "radial-gradient(ellipse 80% 50% at 50% 100%, black 0%, transparent 80%)"
          : "radial-gradient(circle 900px at 50% 240px, black, transparent)",
        ...(perspective && {
          transform: "perspective(1000px) rotateX(60deg)",
          transformOrigin: "center bottom",
        }),
      }}
    >
      {animated && (
        <motion.div
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(${color.replace("0.1", "0.05")} 1px, transparent 1px),
              linear-gradient(90deg, ${color.replace("0.1", "0.05")} 1px, transparent 1px)
            `,
            backgroundSize: `${cellSize / 5}px ${cellSize / 5}px`,
          }}
          animate={{
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      )}
    </div>
  );
}
