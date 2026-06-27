"use client";

import React, { useState, useEffect, useRef } from "react";
import { AudioSystem } from "../lib/AudioSystem";

export function AudioToggle() {
  const [enabled, setEnabled] = useState(false);
  const [volume, setVolume] = useState(50);
  const [expanded, setExpanded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Read stored settings on mount
    const savedEnabled = localStorage.getItem("sip-audio-enabled") === "true";
    const savedVolume = Number(localStorage.getItem("sip-audio-volume") ?? "50");

    setEnabled(savedEnabled);
    setVolume(savedVolume);

    // Sync state with singleton instance
    const audio = AudioSystem.getInstance();
    audio.setEnabled(savedEnabled);
    audio.setVolume(savedVolume / 100);
  }, []);

  const toggleSound = () => {
    const nextEnabled = !enabled;
    setEnabled(nextEnabled);

    const audio = AudioSystem.getInstance();
    audio.setEnabled(nextEnabled);

    if (nextEnabled) {
      // Play a quick click indicator to confirm audio activation
      setTimeout(() => {
        audio.playClick();
      }, 50);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const nextVolume = Number(e.target.value);
    setVolume(nextVolume);

    const audio = AudioSystem.getInstance();
    audio.setVolume(nextVolume / 100);
  };

  // Keyboard navigation helpers
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setExpanded(false);
    }
  };

  return (
    <div
      ref={containerRef}
      className={`audio-toggle-container ${expanded ? "expanded" : ""}`}
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
      onFocus={() => setExpanded(true)}
      onBlur={(e) => {
        // Only collapse if focus leaves the container
        if (!containerRef.current?.contains(e.relatedTarget as Node)) {
          setExpanded(false);
        }
      }}
      onKeyDown={handleKeyDown}
      role="region"
      aria-label="Audio controls"
    >
      <button
        onClick={toggleSound}
        className="audio-button"
        aria-label={enabled ? "Mute soundtrack and SFX" : "Unmute soundtrack and SFX"}
        aria-pressed={enabled}
      >
        {enabled ? (
          // Speaker wave icon
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="icon"
            aria-hidden="true"
          >
            <path d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.508c-1.141 0-2.063.922-2.063 2.063v4.874c0 1.141.922 2.063 2.063 2.063h1.932l4.5 4.5c.944.945 2.56.276 2.56-1.06V4.06zM17.78 9.22a.75.75 0 10-1.06 1.06L18.44 12l-1.72 1.72a.75.75 0 001.06 1.06l1.72-1.72 1.72 1.72a.75.75 0 101.06-1.06L20.56 12l1.72-1.72a.75.75 0 00-1.06-1.06l-1.72 1.72-1.72-1.72z" />
            <path d="M16.24 16.24a6 6 0 000-8.49.75.75 0 111.06-1.06 7.5 7.5 0 010 10.61.75.75 0 11-1.06-1.06z" />
          </svg>
        ) : (
          // Speaker mute/x icon
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="icon muted"
            aria-hidden="true"
          >
            <path d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.508c-1.141 0-2.063.922-2.063 2.063v4.874c0 1.141.922 2.063 2.063 2.063h1.932l4.5 4.5c.944.945 2.56.276 2.56-1.06V4.06z" />
            <path d="M19.72 9.22a.75.75 0 011.06 0L22 10.44l1.22-1.22a.75.75 0 111.06 1.06L23.06 11.5l1.22 1.22a.75.75 0 11-1.06 1.06L22 12.56l-1.22 1.22a.75.75 0 01-1.06-1.06l1.22-1.22-1.22-1.22a.75.75 0 010-1.06z" />
          </svg>
        )}
      </button>

      {expanded && (
        <div className="slider-wrapper">
          <input
            type="range"
            min="0"
            max="100"
            value={volume}
            onChange={handleVolumeChange}
            className="volume-slider"
            aria-label="Volume slider"
          />
          <span className="volume-label" aria-live="polite">
            {volume}%
          </span>
        </div>
      )}

      <style jsx global>{`
        .audio-toggle-container {
          position: fixed;
          bottom: 24px;
          left: 24px;
          z-index: 1000;
          display: flex;
          align-items: center;
          background: rgba(10, 10, 16, 0.45);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 9999px;
          padding: 6px;
          transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
          box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
          max-width: 52px;
          overflow: hidden;
        }

        .audio-toggle-container.expanded {
          max-width: 240px;
          padding: 6px 16px 6px 6px;
          border-color: rgba(0, 242, 254, 0.25);
          box-shadow: 0 0 15px rgba(0, 242, 254, 0.15), 0 4px 30px rgba(0, 0, 0, 0.45);
        }

        .audio-button {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.7);
          cursor: pointer;
          transition: all 0.2s ease;
          outline: none;
          padding: 0;
        }

        .audio-button:hover,
        .audio-button:focus {
          color: #00f2fe;
          background: rgba(255, 255, 255, 0.06);
          box-shadow: 0 0 8px rgba(0, 242, 254, 0.2);
        }

        .audio-button .icon {
          width: 20px;
          height: 20px;
          transition: transform 0.2s ease;
        }

        .audio-button:active .icon {
          transform: scale(0.9);
        }

        .audio-button .icon.muted {
          color: rgba(255, 255, 255, 0.4);
        }

        .slider-wrapper {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-left: 10px;
          animation: fadeIn 0.25s ease forwards;
          white-space: nowrap;
        }

        .volume-slider {
          -webkit-appearance: none;
          appearance: none;
          width: 100px;
          height: 4px;
          border-radius: 2px;
          background: rgba(255, 255, 255, 0.15);
          outline: none;
          cursor: pointer;
          transition: background 0.2s ease;
        }

        .volume-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #00f2fe;
          border: 2px solid #ffffff;
          box-shadow: 0 0 6px rgba(0, 242, 254, 0.5);
          cursor: pointer;
          transition: transform 0.15s ease;
        }

        .volume-slider::-webkit-slider-thumb:hover {
          transform: scale(1.2);
        }

        .volume-slider::-moz-range-thumb {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #00f2fe;
          border: 2px solid #ffffff;
          box-shadow: 0 0 6px rgba(0, 242, 254, 0.5);
          cursor: pointer;
          transition: transform 0.15s ease;
        }

        .volume-slider::-moz-range-thumb:hover {
          transform: scale(1.2);
        }

        .volume-label {
          color: rgba(255, 255, 255, 0.85);
          font-family: var(--font-outfit), sans-serif;
          font-size: 13px;
          font-weight: 500;
          min-width: 32px;
          text-align: right;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}
