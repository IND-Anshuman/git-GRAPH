"use client";

import { useEffect, useRef } from "react";
import { OnboardingCanvas } from "@/components/OnboardingCanvas";
import { Scene2Sidebar } from "@/components/scenes/Scene2Overlay";
import { getScrollController } from "@/lib/ScrollController";
import { SceneManager } from "@/lib/SceneManager";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { AudioToggle } from "@/components/AudioToggle";
import { AudioSystem } from "@/lib/AudioSystem";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Suppress the THREE.Clock deprecation warning from the console globally in the browser
if (typeof window !== "undefined") {
  const originalWarn = console.warn;
  console.warn = (...args: any[]) => {
    if (args[0] && typeof args[0] === "string" && (args[0].includes("THREE.Clock") || args[0].includes("Clock has been deprecated"))) {
      return;
    }
    originalWarn.apply(console, args);
  };
}

const FolderIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-19.5 0A2.25 2.25 0 0 0 4.5 15h15a2.25 2.25 0 0 0 2.25-2.25m-19.5 0v.25A2.25 2.25 0 0 0 4.5 15.25h15a2.25 2.25 0 0 0 2.25-2.25v-.25M9 3h1.378a2.249 2.249 0 0 1 1.747.836l1.28 1.542a2.25 2.25 0 0 0 1.747.836H19.5A2.25 2.25 0 0 1 21.75 8.25v1.5H2.25V8.25A2.25 2.25 0 0 1 4.5 6H9V3z" />
  </svg>
);

const CodeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5" />
  </svg>
);

const CubeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
  </svg>
);

const DocumentIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9z" />
  </svg>
);

const MouseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 animate-bounce">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 9V6a3 3 0 1 1 6 0v3m-6 0a3 3 0 0 0 6 0m-6 0h6m-6 9a6 6 0 0 0 12 0v-3a6 6 0 0 0-12 0v3z" />
  </svg>
);

/**
 * Home page component renders the split screen layout based on the design mockup:
 * - Left panel: Fixed informational sidebar detailing tech stack, concept, data flow, and journeys.
 * - Right panel: Scrollable sequence of glassmorphic narrative cards synced with R3F.
 */
export default function Home() {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const currentScene = useOnboardingStore((s) => s.currentScene);

  useEffect(() => {

    // Audio autoplay compliance sequence
    const handleFirstInteraction = () => {
      const audio = AudioSystem.getInstance();
      audio.initContext();
      
      // Cleanup listeners once the AudioContext is activated
      window.removeEventListener("click", handleFirstInteraction);
      window.removeEventListener("keydown", handleFirstInteraction);
      window.removeEventListener("scroll", handleFirstInteraction);
    };

    window.addEventListener("click", handleFirstInteraction, { passive: true });
    window.addEventListener("keydown", handleFirstInteraction, { passive: true });
    window.addEventListener("scroll", handleFirstInteraction, { passive: true });

    return () => {
      window.removeEventListener("click", handleFirstInteraction);
      window.removeEventListener("keydown", handleFirstInteraction);
      window.removeEventListener("scroll", handleFirstInteraction);
    };
  }, []);

  // Initialize Lenis smooth scroll and connect with GSAP ScrollTrigger
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Register GSAP Plugin
    gsap.registerPlugin(ScrollTrigger);

    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // smooth exponential ease-out
      orientation: "vertical",
      gestureOrientation: "vertical",
      smoothWheel: true
    });

    // Notify ScrollTrigger on Lenis scroll updates
    lenis.on("scroll", () => {
      ScrollTrigger.update();
    });

    // Hook Lenis render loops into GSAP's optimized ticker loop
    const rafCallback = (time: number) => {
      lenis.raf(time * 1000);
    };
    gsap.ticker.add(rafCallback);
    gsap.ticker.lagSmoothing(0);

    return () => {
      lenis.destroy();
      gsap.ticker.remove(rafCallback);
    };
  }, []);

  useEffect(() => {
    // Initialize ScrollController with the container
    const scrollCtrl = getScrollController();
    if (scrollContainerRef.current) {
      scrollCtrl.initialize(scrollContainerRef.current);
    }
    
    // Subscribe to scroll progress to update SceneManager
    const sceneManager = SceneManager.getInstance();
    
    const unsubscribe = scrollCtrl.onProgressChange(() => {
      const activeScene = scrollCtrl.getCurrentScene();
      sceneManager.updateSceneLifecycle(activeScene);
    });

    // Preload Scene 1 and Scene 2 immediately on mount to prevent any delay
    sceneManager.updateSceneLifecycle(1);

    return () => {
      unsubscribe();
      scrollCtrl.destroy();
    };
  }, []);

  const scenes = [
    {
      num: 1,
      name: "The Chaos",
      sub: "Raw Code Universe",
      desc: "Billions of lines of code scattered across countless files, services, and systems. Scroll to begin structuring the source code.",
      pct: "0%",
      tags: ["Files", "Services", "Commits"],
      progress: 0.0,
    },
    {
      num: 2,
      name: "Stardust of Code",
      sub: "Extraction & Understanding",
      desc: "We break down code into its fundamental building blocks and connect the dots. Repository decomposed into semantic particles.",
      pct: "17%",
      tags: ["Classes", "Functions", "APIs", "DBs"],
      progress: 0.17,
    },
    {
      num: 3,
      name: "Planets of Capability",
      sub: "What Your Software Does",
      desc: "Related components orbit together forming capabilities that deliver business value, clustered into concept constellations.",
      pct: "33%",
      tags: ["Authentication", "Payments", "Inventory", "Search"],
      progress: 0.33,
    },
    {
      num: 4,
      name: "Solar Systems of Architecture",
      sub: "How It's Structured",
      desc: "Capabilities form systems. Systems form architecture. Architecture domains organize capabilities into solar systems.",
      pct: "50%",
      tags: ["Bounded Contexts", "Services", "Domains"],
      progress: 0.50,
    },
    {
      num: 5,
      name: "Rings of Decisions",
      sub: "Why It Evolved",
      desc: "Every architectural choice has a reason. Architectural decisions orbit capabilities like planetary rings.",
      pct: "67%",
      tags: ["ADRs", "Choices", "Trade-offs"],
      progress: 0.67,
    },
    {
      num: 6,
      name: "Constellation of Reasoning",
      sub: "Ask. Analyze. Understand.",
      desc: "We apply reasoning over all evidence to answer questions and surface insights through a neural network of reasoning.",
      pct: "83%",
      tags: ["Evidence", "Hypotheses", "Insights"],
      progress: 0.83,
    },
    {
      num: 7,
      name: "The Knowledge Universe",
      sub: "From Code to Understanding",
      desc: "Everything unified in a living knowledge universe. You're ready to explore and query the Software Intelligence Platform.",
      pct: "100%",
      tags: ["Explore", "Understand", "Impact"],
      progress: 1.0,
      isLast: true,
    },
  ];

  return (
    <div className="relative min-h-screen w-full bg-slate-950 text-slate-100 overflow-x-hidden font-sans">
      {/* 3D Background Canvas */}
      <div className="fixed inset-0 z-0 h-screen w-screen">
        <OnboardingCanvas />
      </div>

      {/* Top Navigation Bar matching reference image exactly */}
      <header className="fixed top-5 left-8 right-8 z-40 flex items-center justify-between pointer-events-none select-none">
        {/* Left: Progress Dots */}
        <div className="flex items-center gap-3 bg-[#080710]/60 backdrop-blur border border-white/10 px-4 py-2 rounded-full shadow-lg pointer-events-auto">
          <span className="text-[10px] font-black uppercase tracking-widest text-slate-300 font-mono leading-none">
            SCENE {currentScene} OF 8
          </span>
          <div className="flex items-center gap-1.5 h-1.5">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
              <span 
                key={s} 
                className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${
                  s === currentScene 
                    ? "bg-purple-500 ring-2 ring-purple-500/50 scale-125" 
                    : s < currentScene 
                      ? "bg-purple-400/40" 
                      : "bg-slate-700"
                }`} 
              />
            ))}
          </div>
        </div>

        {/* Right: Skip Journey button */}
        <button 
          onClick={() => getScrollController().setProgress(1.0)} 
          className="pointer-events-auto bg-[#080710]/70 hover:bg-[#080710]/90 border border-white/10 hover:border-purple-500/20 text-slate-300 hover:text-white text-[10px] font-bold uppercase tracking-wider py-2 px-5 rounded-full transition shadow-lg cursor-pointer"
        >
          Skip Journey &rarr;
        </button>
      </header>

      {/* Main Split Layout */}
      <div className="relative z-10 flex min-h-screen w-full">
        
        {/* Left Fixed Sidebar (Glassmorphic) */}
        <aside className="fixed left-0 top-0 z-20 h-screen w-[380px] bg-transparent p-6 overflow-y-auto flex flex-col justify-between select-none">
          <div className="relative flex-1 flex flex-col">
            
            {/* Panel 1: Scene 1 Overlay */}
            <div 
              className="w-full transition-all duration-500 ease-out select-none flex flex-col gap-5"
              style={{
                opacity: currentScene === 1 ? 1 : 0,
                transform: `translateY(${currentScene === 1 ? 0 : currentScene > 1 ? -16 : 16}px)`,
                pointerEvents: currentScene === 1 ? "auto" : "none",
                position: currentScene === 1 ? "relative" : "absolute",
                top: 0,
                left: 0,
                right: 0,
              }}
            >
              <div className="stats-header">
                <span className="text-[11px] font-bold uppercase tracking-[0.3em] text-purple-400 mb-2 block">
                  THE CHAOS
                </span>
                <h1 className="text-3xl font-extrabold text-white leading-tight mb-3 tracking-tight">
                  Modern software<br />is <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 font-black">too complex.</span>
                </h1>
                <p className="text-xs leading-relaxed text-slate-400">
                  Billions of lines of code scattered across countless files, services, and systems.
                </p>
              </div>

              {/* Repository Metrics Panel */}
              <div className="flex flex-col gap-4 mt-2 bg-slate-900/25 border border-slate-900/60 p-5 rounded-2xl backdrop-blur-sm shadow-xl">
                {[
                  { label: "Files", val: "10,231", icon: <FolderIcon />, color: "text-purple-400" },
                  { label: "Functions", val: "128,430", icon: <CodeIcon />, color: "text-pink-400" },
                  { label: "Services", val: "342", icon: <CubeIcon />, color: "text-orange-400" },
                  { label: "Lines of Code", val: "28.7M", icon: <DocumentIcon />, color: "text-cyan-400" }
                ].map((stat) => (
                  <div key={stat.label} className="flex items-center gap-4 py-1.5 first:pt-0 last:pb-0 border-b border-slate-900/40 last:border-0">
                    <div className={`${stat.color} p-2 bg-slate-950/60 rounded-xl border border-slate-800/45`}>
                      {stat.icon}
                    </div>
                    <div>
                      <div className={`text-2xl font-extrabold tracking-tight ${stat.color}`}>
                        {stat.val}
                      </div>
                      <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 mt-0.5">
                        {stat.label}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="text-[10px] text-slate-500 flex items-center gap-2 mt-4">
                <MouseIcon />
                <span className="tracking-wide">Scroll to explore the journey</span>
              </div>
            </div>

            {/* Panel 2: Scene 2 Overlay */}
            <div 
              className="w-full transition-all duration-500 ease-out select-none"
              style={{
                opacity: currentScene === 2 ? 1 : 0,
                transform: `translateY(${currentScene === 2 ? 0 : currentScene > 2 ? -16 : 16}px)`,
                pointerEvents: currentScene === 2 ? "auto" : "none",
                position: currentScene === 2 ? "relative" : "absolute",
                top: 0,
                left: 0,
                right: 0,
              }}
            >
              <Scene2Sidebar />
            </div>

            {/* Panel 3: Fallback Scene Overlay */}
            <div 
              className="w-full transition-all duration-500 ease-out select-none flex flex-col"
              style={{
                opacity: currentScene >= 3 ? 1 : 0,
                transform: `translateY(${currentScene >= 3 ? 0 : 16}px)`,
                pointerEvents: currentScene >= 3 ? "auto" : "none",
                position: currentScene >= 3 ? "relative" : "absolute",
                top: 0,
                left: 0,
                right: 0,
              }}
            >
              <span className="text-[10px] font-bold uppercase tracking-[0.25em] text-purple-400">Onboarding Experience</span>
              <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">Space Universe Journey</h1>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                A 3D scrollable experience that takes users on a journey from raw code to deep understanding.
              </p>

              {/* Concept Overview */}
              <div className="mt-6">
                <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-300 border-b border-slate-900 pb-1">Concept Overview</h3>
                <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                  The universe represents your codebase. As the user scrolls, we zoom out from chaos to clarity, revealing layers of intelligence and understanding.
                </p>
              </div>

              {/* Tech Stack */}
              <div className="mt-6">
                <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-300 border-b border-slate-900 pb-1">Tech Stack</h3>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {[
                    { name: "React Three Fiber", color: "bg-cyan-500" },
                    { name: "Three.js", color: "bg-emerald-500" },
                    { name: "GSAP ScrollTrigger", color: "bg-teal-500" },
                    { name: "Drei", color: "bg-indigo-500" },
                    { name: "Framer Motion", color: "bg-pink-500" }
                  ].map((tech) => (
                    <div key={tech.name} className="flex items-center gap-1.5 bg-slate-900/60 px-2 py-1 rounded border border-slate-900">
                      <span className={`h-1.5 w-1.5 rounded-full ${tech.color} shadow-sm`} />
                      <span className="text-[10px] font-medium text-slate-300">{tech.name}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>
        </aside>

        {/* Right Scroll Panel */}
        <main ref={scrollContainerRef} className="ml-[380px] w-[calc(100%-380px)] min-h-screen relative z-10 flex flex-col items-center">
          
          {/* Spacer to push first card down */}
          <div className="h-[100vh]" />

          {/* Scrollable scene cards list */}
          <div className="w-full max-w-xl px-6 flex flex-col gap-[280vh]">
            {scenes.map((scene) => (
              <div key={scene.num} className="min-h-[220px] pointer-events-none opacity-0" />
            ))}
          </div>

          {/* Bottom spacing to ensure final scene cards can be scrolled into view */}
          <div className="h-[100vh]" />
        </main>



        {/* Audio Control UI Overlay */}
        <AudioToggle />
      </div>
    </div>
  );
}
