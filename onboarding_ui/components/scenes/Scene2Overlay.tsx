"use client";

import { useOnboardingStore } from "@/stores/onboardingStore";

// ── SVG Icons ──
const CodeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5" />
  </svg>
);

const CubeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
  </svg>
);

const LinkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
  </svg>
);


const LightbulbIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-3m0 0a8.12 8.12 0 0 0 5-1.5 7 7 0 1 0-10 0 8.12 8.12 0 0 0 5 1.5Zm0 3v.01M9 21h6" />
  </svg>
);

const clamp = (val: number, min: number, max: number) => Math.max(min, Math.min(max, val));

// ── Scene 2 Sidebar Content (To be mounted inside the fixed <aside>) ──
export function Scene2Sidebar() {
  const scrollProgress = useOnboardingStore((s) => s.scrollProgress);
  const localProgress = Math.max(0, Math.min(1, (scrollProgress - 0.17) / 0.16));

  const extractionProgress = localProgress <= 0.3 
    ? 0 
    : localProgress <= 0.7 
      ? Math.round(((localProgress - 0.3) / 0.4) * 68) 
      : Math.round(68 + ((localProgress - 0.7) / 0.3) * 32);

  const stats = [
    { label: 'Functions Extracted', value: Math.floor(128430 * (extractionProgress / 100)), icon: <CodeIcon />, color: 'text-purple-400' },
    { label: 'Classes & Interfaces', value: Math.floor(56782 * (extractionProgress / 100)), icon: <CubeIcon />, color: 'text-blue-400' },
    { label: 'Relationships Found', value: Math.floor(342891 * (extractionProgress / 100)), icon: <LinkIcon />, color: 'text-purple-400' },
  ];

  const headerOpacity = clamp(localProgress / 0.12, 0, 1);
  const headerTranslateY = 12 * (1 - headerOpacity);

  const statsOpacity = clamp((localProgress - 0.08) / 0.12, 0, 1);
  const statsTranslateY = 12 * (1 - statsOpacity);

  const infoOpacity = clamp((localProgress - 0.3) / 0.12, 0, 1);
  const infoTranslateY = 10 * (1 - infoOpacity);

  return (
    <div className="flex flex-col flex-1 select-none w-full">
      {/* Header Block */}
      <div 
        className="stats-header transition-all duration-300 ease-out"
        style={{
          opacity: headerOpacity,
          transform: `translateY(${headerTranslateY}px)`
        }}
      >
        <span className="text-[11px] font-bold uppercase tracking-[0.3em] text-purple-400 mb-2 block animate-pulse">
          Stardust of Code
        </span>
        <h1 className="text-3xl font-extrabold text-white leading-tight mb-3 tracking-tight">
          SEEE extracts <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 font-black">evidence</span> <br />
          from the chaos.
        </h1>
        <p className="text-xs leading-relaxed text-slate-400">
          Every symbol, dependency, and relationship is captured and connected.
        </p>
      </div>

      {/* Unified Stats Card Container (Matches reference image) */}
      <div 
        className="bg-[#080710]/50 backdrop-blur-md border border-white/5 p-5 rounded-2xl shadow-xl flex flex-col gap-4 mt-4 transition-all duration-300 ease-out"
        style={{
          opacity: statsOpacity,
          transform: `translateY(${statsTranslateY}px)`
        }}
      >
        {stats.map((stat) => (
          <div 
            key={stat.label} 
            className="flex items-center gap-4 py-1.5 first:pt-0 last:pb-0 border-b border-white/5 last:border-0 transition-all duration-300 hover:scale-[1.015]"
          >
            {/* Circular glowing icon container */}
            <div className={`${stat.color} h-10 w-10 rounded-full flex items-center justify-center bg-slate-950/80 border border-slate-800/40 shadow-inner`}>
              {stat.icon}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[17px] font-extrabold text-white leading-tight font-mono">
                {stat.value.toLocaleString()}
              </div>
              <div className="text-[10px] text-slate-400 font-sans mt-0.5 uppercase tracking-wider">
                {stat.label}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Info Box Card at bottom */}
      <div 
        className="mt-auto bg-[#080710]/40 border border-white/5 rounded-xl p-4 flex gap-3.5 items-start transition-all duration-300 ease-out"
        style={{
          opacity: infoOpacity,
          transform: `translateY(${infoTranslateY}px)`
        }}
      >
        <div className="text-purple-400 mt-0.5 flex-shrink-0">
          <LightbulbIcon />
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
          SEEE (Semantic Evidence Extraction Engine) turns raw code into structured meaning.
        </p>
      </div>
    </div>
  );
}


