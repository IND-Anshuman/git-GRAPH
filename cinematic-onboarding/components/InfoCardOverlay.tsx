"use client";

import { useEffect, useState, useRef } from "react";
import { useThree } from "@react-three/fiber";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { Html } from "@react-three/drei";

/**
 * InfoCardOverlay renders the glassmorphic informational cards for hovered
 * or selected elements, projecting 3D positions to 2D screen coordinates.
 */
export function InfoCardOverlay() {
  const { camera } = useThree();
  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);
  const closeCard = useOnboardingStore((s) => s.closeCard);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  const activeId = expandedCardId || hoveredObjectId;
  const isExpanded = !!expandedCardId;

  const [metadata, setMetadata] = useState<any>(null);
  const [coords, setCoords] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [visible, setVisible] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  // 1. Fetch metadata when active object changes
  useEffect(() => {
    if (activeId) {
      const handler = InteractionHandler.getInstance();
      const meta = handler.getObjectMetadata(activeId);
      if (meta) {
        setMetadata(meta);
        setVisible(true);
      } else {
        setVisible(false);
      }
    } else {
      setVisible(false);
    }
  }, [activeId]);

  // 2. Project 3D vector to 2D screen coordinates on every frame
  useEffect(() => {
    if (!activeId || isExpanded || !visible) return;

    let activeFrame = true;
    const project = () => {
      if (!activeFrame) return;

      const handler = InteractionHandler.getInstance();
      const obj = (handler as any).registry.get(activeId);
      if (obj && camera) {
        const tempV = obj.position.clone();
        tempV.project(camera);

        // Map to 2D pixel coordinates
        let x = (tempV.x * 0.5 + 0.5) * window.innerWidth;
        let y = (-tempV.y * 0.5 + 0.5) * window.innerHeight;

        // Offset the card slightly from the center node
        x += 20;
        y -= 50;

        // Viewport clamping: check card dimensions and prevent edge overflow
        if (cardRef.current) {
          const width = cardRef.current.offsetWidth || 280;
          const height = cardRef.current.offsetHeight || 150;

          // Clamp X coordinate
          if (x + width > window.innerWidth - 20) {
            x = window.innerWidth - width - 20;
          }
          if (x < 20) x = 20;

          // Clamp Y coordinate
          if (y + height > window.innerHeight - 20) {
            y = window.innerHeight - height - 20;
          }
          if (y < 20) y = 20;
        }

        setCoords({ x, y });
      }

      requestAnimationFrame(project);
    };

    project();
    return () => {
      activeFrame = false;
    };
  }, [activeId, isExpanded, visible, camera]);

  if (!visible || !metadata) return null;

  // Render Expanded Card Centered
  if (isExpanded) {
    return (
      <Html fullscreen style={{ pointerEvents: "auto" }}>
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm pointer-events-auto p-4 select-none animate-fade-in-fast">
          <style>{`
            .animate-fade-in-fast {
              animation: fadeInCard 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }
            @keyframes fadeInCard {
              from { opacity: 0; transform: scale(0.95); }
              to { opacity: 1; transform: scale(1); }
            }
          `}</style>

          <div className="w-full max-w-lg rounded-2xl border border-purple-500/30 bg-slate-950/95 p-6 shadow-[0_0_30px_rgba(156,39,176,0.25)] flex flex-col gap-4 text-left">
            {/* Header */}
            <div className="flex justify-between items-start border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-widest text-purple-400">
                  {metadata.type || "Repository Node"}
                </span>
                <h2 className="text-xl font-extrabold text-white mt-1 tracking-tight">
                  {metadata.title}
                </h2>
              </div>
              <button
                onClick={closeCard}
                className="text-slate-400 hover:text-white bg-slate-900 border border-slate-800 hover:bg-slate-800 px-3 py-1 rounded-lg text-xs font-bold transition cursor-pointer"
              >
                Close
              </button>
            </div>

            {/* Description */}
            <p className="text-sm text-slate-300 leading-relaxed font-normal">
              {metadata.description}
            </p>

            {/* Details list (WCAG contrast compliant: white on dark slate) */}
            {metadata.details && (
              <div className="grid grid-cols-2 gap-3 bg-slate-900/60 border border-slate-900 p-4 rounded-xl">
                {Object.entries(metadata.details).map(([key, val]) => (
                  <div key={key} className="flex flex-col">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">
                      {key}
                    </span>
                    <span className="text-xs font-semibold text-slate-100 mt-0.5">
                      {String(val)}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-3 mt-2">
              {metadata.actions?.map((act: any, idx: number) => (
                <button
                  key={idx}
                  onClick={() => {
                    if (act.href) window.location.href = act.href;
                    else if (act.onClick) alert(`Triggered: ${act.onClick}`);
                  }}
                  className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-extrabold py-2 px-4 rounded-lg shadow-md transition cursor-pointer border-none"
                >
                  {act.label}
                </button>
              ))}
              <button
                onClick={closeCard}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold py-2 px-4 rounded-lg transition cursor-pointer border-none"
              >
                Back to Experience
              </button>
            </div>
          </div>
        </div>
      </Html>
    );
  }

  // Render Compact Hover Tooltip
  return (
    <Html fullscreen style={{ pointerEvents: "none" }}>
      <div
        ref={cardRef}
        style={{
          position: "absolute",
          left: `${coords.x}px`,
          top: `${coords.y}px`,
        }}
        className="z-40 pointer-events-auto w-64 rounded-xl border border-cyan-500/30 bg-slate-950/90 p-4 shadow-[0_0_15px_rgba(0,229,255,0.15)] flex flex-col gap-1.5 transition-all duration-300 ease-out animate-fade-in-fast text-left"
      >
        <div>
          <span className="text-[8px] font-bold uppercase tracking-wider text-cyan-400">
            {metadata.type || "Node Info"}
          </span>
          <h3 className="text-sm font-bold text-white tracking-tight leading-tight mt-0.5">
            {metadata.title}
          </h3>
        </div>

        <p className="text-[11px] text-slate-300 leading-relaxed font-normal">
          {metadata.description.length > 95 ? `${metadata.description.substring(0, 95)}...` : metadata.description}
        </p>

        {/* Keyboard action hint (Requirement 13.1) */}
        <div className="flex justify-between items-center mt-1.5 pt-1.5 border-t border-slate-900 text-[9px] text-slate-500">
          <span>Click or press [Space] to inspect</span>
          <button
            onClick={() => activeId && expandCard(activeId)}
            className="text-cyan-400 hover:text-cyan-300 font-bold bg-transparent border-none cursor-pointer p-0"
          >
            Inspect
          </button>
        </div>
      </div>
    </Html>
  );
}
