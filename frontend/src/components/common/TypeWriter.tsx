"use client";

import { useState, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface TypeWriterProps {
  lines: string[];
  speed?: number;
  pauseBetween?: number;
  loop?: boolean;
  cursor?: boolean;
  className?: string;
  lineClassName?: string;
  prefix?: string;
}

export function TypeWriter({
  lines,
  speed = 45,
  pauseBetween = 1200,
  loop = false,
  cursor = true,
  className = "",
  lineClassName = "",
  prefix = "> ",
}: TypeWriterProps) {
  const [displayedLines, setDisplayedLines] = useState<string[]>([]);
  const [currentLine, setCurrentLine] = useState(0);
  const [currentChar, setCurrentChar] = useState(0);
  const [isWaiting, setIsWaiting] = useState(false);
  const [showCursor, setShowCursor] = useState(true);
  const rafRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Blinking cursor
  useEffect(() => {
    if (!cursor) return;
    const interval = setInterval(() => setShowCursor((v) => !v), 530);
    return () => clearInterval(interval);
  }, [cursor]);

  useEffect(() => {
    if (currentLine >= lines.length) {
      if (loop) {
        rafRef.current = setTimeout(() => {
          setDisplayedLines([]);
          setCurrentLine(0);
          setCurrentChar(0);
        }, pauseBetween * 2);
      }
      return;
    }

    const target = lines[currentLine];

    if (currentChar < target.length) {
      rafRef.current = setTimeout(() => {
        setCurrentChar((c) => c + 1);
      }, speed);
    } else {
      setIsWaiting(true);
      rafRef.current = setTimeout(() => {
        setDisplayedLines((prev) => [...prev, target]);
        setCurrentLine((l) => l + 1);
        setCurrentChar(0);
        setIsWaiting(false);
      }, pauseBetween);
    }

    return () => {
      if (rafRef.current) clearTimeout(rafRef.current);
    };
  }, [currentLine, currentChar, lines, speed, pauseBetween, loop]);

  const currentTyping =
    currentLine < lines.length ? lines[currentLine].slice(0, currentChar) : "";

  return (
    <div className={cn("font-mono text-xs", className)}>
      {displayedLines.map((line, i) => (
        <div key={i} className={cn("text-[var(--color-text-secondary)]", lineClassName)}>
          <span className="text-[var(--neon-green)] opacity-60">{prefix}</span>
          {line}
        </div>
      ))}
      {currentLine < lines.length && (
        <div className={cn("text-[var(--neon-blue)]", lineClassName)}>
          <span className="text-[var(--neon-green)] opacity-60">{prefix}</span>
          {currentTyping}
          {cursor && (
            <span
              className="ml-px inline-block w-[7px] h-[13px] align-middle bg-[var(--neon-blue)]"
              style={{ opacity: showCursor ? 1 : 0, transition: "opacity 0.1s" }}
            />
          )}
        </div>
      )}
    </div>
  );
}
