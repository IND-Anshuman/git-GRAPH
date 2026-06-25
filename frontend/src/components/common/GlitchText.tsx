"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface GlitchTextProps {
  children: string;
  trigger?: "hover" | "always" | "interval";
  intensity?: "low" | "medium" | "high";
  className?: string;
}

export function GlitchText({
  children,
  trigger = "hover",
  intensity = "medium",
  className = "",
}: GlitchTextProps) {
  const [isGlitching, setIsGlitching] = useState(trigger === "always");

  useEffect(() => {
    if (trigger === "interval") {
      const interval = setInterval(() => {
        setIsGlitching(true);
        setTimeout(() => setIsGlitching(false), 300);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [trigger]);

  const glitchIntensity = {
    low: 1,
    medium: 2,
    high: 3,
  }[intensity];

  return (
    <span
      className={`glitch-text relative inline-block ${className}`}
      data-text={children}
      onMouseEnter={() => trigger === "hover" && setIsGlitching(true)}
      onMouseLeave={() => trigger === "hover" && setIsGlitching(false)}
      style={{
        ...(isGlitching && {
          animation: `glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite`,
        }),
      }}
    >
      {children}
      {isGlitching && (
        <>
          <motion.span
            className="absolute top-0 left-0 text-neon-blue opacity-80"
            style={{
              clipPath: "polygon(0 0, 100% 0, 100% 45%, 0 45%)",
            }}
            animate={{
              x: [-glitchIntensity, glitchIntensity, -glitchIntensity],
              y: [glitchIntensity, -glitchIntensity, glitchIntensity],
            }}
            transition={{
              duration: 0.15,
              repeat: Infinity,
              repeatType: "mirror",
            }}
          >
            {children}
          </motion.span>
          <motion.span
            className="absolute top-0 left-0 text-neon-pink opacity-80"
            style={{
              clipPath: "polygon(0 60%, 100% 60%, 100% 100%, 0 100%)",
            }}
            animate={{
              x: [glitchIntensity, -glitchIntensity, glitchIntensity],
              y: [-glitchIntensity, glitchIntensity, -glitchIntensity],
            }}
            transition={{
              duration: 0.15,
              repeat: Infinity,
              repeatType: "mirror",
            }}
          >
            {children}
          </motion.span>
        </>
      )}
    </span>
  );
}
