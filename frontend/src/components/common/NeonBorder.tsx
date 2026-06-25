"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface NeonBorderProps {
  children: ReactNode;
  color?: "blue" | "purple" | "pink" | "green";
  animated?: boolean;
  glow?: boolean;
  className?: string;
}

const colorMap = {
  blue: {
    border: "rgba(0, 240, 255, 0.3)",
    glow: "0 0 20px rgba(0, 240, 255, 0.4), 0 0 40px rgba(0, 240, 255, 0.2)",
    gradient: "linear-gradient(135deg, rgba(0, 240, 255, 0.3), rgba(176, 38, 255, 0.3), rgba(255, 16, 240, 0.3), rgba(0, 240, 255, 0.3))",
  },
  purple: {
    border: "rgba(176, 38, 255, 0.3)",
    glow: "0 0 20px rgba(176, 38, 255, 0.4), 0 0 40px rgba(176, 38, 255, 0.2)",
    gradient: "linear-gradient(135deg, rgba(176, 38, 255, 0.3), rgba(255, 16, 240, 0.3), rgba(0, 240, 255, 0.3), rgba(176, 38, 255, 0.3))",
  },
  pink: {
    border: "rgba(255, 16, 240, 0.3)",
    glow: "0 0 20px rgba(255, 16, 240, 0.4), 0 0 40px rgba(255, 16, 240, 0.2)",
    gradient: "linear-gradient(135deg, rgba(255, 16, 240, 0.3), rgba(176, 38, 255, 0.3), rgba(0, 240, 255, 0.3), rgba(255, 16, 240, 0.3))",
  },
  green: {
    border: "rgba(57, 255, 20, 0.3)",
    glow: "0 0 20px rgba(57, 255, 20, 0.4), 0 0 40px rgba(57, 255, 20, 0.2)",
    gradient: "linear-gradient(135deg, rgba(57, 255, 20, 0.3), rgba(0, 240, 255, 0.3), rgba(57, 255, 20, 0.3))",
  },
};

export function NeonBorder({
  children,
  color = "blue",
  animated = true,
  glow = true,
  className = "",
}: NeonBorderProps) {
  const colors = colorMap[color];

  return (
    <motion.div
      className={`relative ${className}`}
      whileHover={glow ? { scale: 1.02 } : undefined}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* Animated holographic border */}
      {animated ? (
        <motion.div
          className="absolute inset-0 rounded-lg pointer-events-none"
          style={{
            background: colors.gradient,
            backgroundSize: "400% 400%",
            padding: "1px",
            mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
            WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
            maskComposite: "exclude",
            WebkitMaskComposite: "xor",
          }}
          animate={{
            backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      ) : (
        <div
          className="absolute inset-0 rounded-lg pointer-events-none"
          style={{
            border: `1px solid ${colors.border}`,
            boxShadow: glow ? colors.glow : undefined,
          }}
        />
      )}

      {/* Content */}
      <div className="relative">{children}</div>
    </motion.div>
  );
}
