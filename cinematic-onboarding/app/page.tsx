"use client";

import { useEffect, useRef, useState } from "react";
import { OnboardingCanvas } from "@/components/OnboardingCanvas";
import { getScrollController } from "@/lib/ScrollController";
import { SceneManager } from "@/lib/SceneManager";
import { useOnboardingStore } from "@/stores/onboardingStore";
<<<<<<< HEAD
import { AudioToggle } from "@/components/AudioToggle";
import { AudioSystem } from "@/lib/AudioSystem";
=======
>>>>>>> 1ed8369a21b3194523231ccb83db6a2ca4e39902

/**
 * Home page component renders the split screen layout based on the design mockup:
 * - Left panel: Fixed informational sidebar detailing tech stack, concept, data flow, and journeys.
 * - Right panel: Scrollable sequence of glassmorphic narrative cards synced with R3F.
 */
export default function Home() {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const currentScene = useOnboardingStore((s) => s.currentScene);
  const qualityTier = useOnboardingStore((s) => s.qualityTier);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
<<<<<<< HEAD

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
=======
>>>>>>> 1ed8369a21b3194523231ccb83db6a2ca4e39902
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

<<<<<<< HEAD
    // Preload Scene 1 and Scene 2 immediately on mount to prevent any delay
    sceneManager.updateSceneLifecycle(1);

=======
>>>>>>> 1ed8369a21b3194523231ccb83db6a2ca4e39902
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

      {/* Main Split Layout */}
      <div className="relative z-10 flex min-h-screen w-full">
        
        {/* Left Fixed Sidebar (Glassmorphic) */}
        <aside className="fixed left-0 top-0 z-20 h-screen w-[380px] bg-slate-950/85 backdrop-blur-md border-r border-slate-900 p-6 overflow-y-auto flex flex-col justify-between select-none">
<<<<<<< HEAD
          {currentScene === 1 ? (
            <div className="flex flex-col gap-6 select-none transition-all duration-300">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-[0.25em] text-purple-400">
                  Workspace Discovery
                </span>
                <h1 className="text-3xl font-black text-white mt-1 tracking-tight leading-tight">
                  The Chaos of <br />Raw Code
                </h1>
                <p className="text-xs text-slate-400 mt-3 leading-relaxed">
                  Modern software is growing exponentially. Overwhelming lines of code, legacy microservices, and untracked files drift in disorganized confusion.
                </p>
              </div>

              {/* Repository Metrics Panel */}
              <div className="flex flex-col gap-3 mt-4 bg-slate-900/40 border border-slate-900 p-4 rounded-xl">
                {[
                  { label: "Files", val: "10,231", desc: "Source files & configurations", color: "text-purple-400" },
                  { label: "Functions", val: "128,430", desc: "Compiled methods & call blocks", color: "text-pink-400" },
                  { label: "Services", val: "342", desc: "Microservices & bounded APIs", color: "text-orange-400" },
                  { label: "Lines of Code", val: "28.7M", desc: "Raw source syntax lines", color: "text-cyan-400" }
                ].map((stat) => (
                  <div key={stat.label} className="flex justify-between items-center py-1.5 border-b border-slate-950/40 last:border-0">
                    <div>
                      <div className="text-xs font-bold text-slate-200">{stat.label}</div>
                      <div className="text-[9px] text-slate-500 mt-0.5">{stat.desc}</div>
                    </div>
                    <div className={`text-xl font-extrabold tracking-tight ${stat.color}`}>
                      {stat.val}
                    </div>
                  </div>
                ))}
              </div>

              <div className="text-[10px] text-slate-500 flex items-center gap-2 mt-4">
                <span className="animate-pulse h-1.5 w-1.5 rounded-full bg-purple-500" />
                Scroll down to observe SEEE extract structure from chaos
              </div>
            </div>
          ) : (
            <div>
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

              {/* Data Flow vertical chart */}
              <div className="mt-6">
                <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-300 border-b border-slate-900 pb-1">Data Flow</h3>
                <div className="flex flex-col gap-1 mt-2 pl-2.5 border-l border-cyan-500/20">
                  {[
                    { title: "Repository", desc: "Git, Files, Commits" },
                    { title: "SEEE Processing", desc: "Extraction & Analysis" },
                    { title: "Knowledge Graph", desc: "Entities, Relations, Events" },
                    { title: "Intelligence Layers", desc: "Capabilities, Architecture, Decisions" },
                    { title: "Insights & Actions", desc: "Understanding & Impact" }
                  ].map((step, idx) => (
                    <div key={step.title} className="relative py-1">
                      <div className="text-[10px] font-bold text-slate-200">{step.title}</div>
                      <div className="text-[9px] text-slate-500">{step.desc}</div>
                      {idx < 4 && (
                        <span className="absolute -left-[14px] top-[70%] text-[8px] text-cyan-400">↓</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
=======
          <div>
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

            {/* Data Flow vertical chart */}
            <div className="mt-6">
              <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-300 border-b border-slate-900 pb-1">Data Flow</h3>
              <div className="flex flex-col gap-1 mt-2 pl-2.5 border-l border-cyan-500/20">
                {[
                  { title: "Repository", desc: "Git, Files, Commits" },
                  { title: "SEEE Processing", desc: "Extraction & Analysis" },
                  { title: "Knowledge Graph", desc: "Entities, Relations, Events" },
                  { title: "Intelligence Layers", desc: "Capabilities, Architecture, Decisions" },
                  { title: "Insights & Actions", desc: "Understanding & Impact" }
                ].map((step, idx) => (
                  <div key={step.title} className="relative py-1">
                    <div className="text-[10px] font-bold text-slate-200">{step.title}</div>
                    <div className="text-[9px] text-slate-500">{step.desc}</div>
                    {idx < 4 && (
                      <span className="absolute -left-[14px] top-[70%] text-[8px] text-cyan-400">↓</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
>>>>>>> 1ed8369a21b3194523231ccb83db6a2ca4e39902

          {/* Bottom Performance and Controls */}
          <div className="mt-6 pt-4 border-t border-slate-900">
            {/* Performance metrics with checklist style */}
            <div className="grid grid-cols-2 gap-1.5 mb-4">
              <div className="text-[10px] text-slate-400 flex items-center gap-1">
                <span className="text-emerald-500 font-bold">✓</span> LOD for 3D models
              </div>
              <div className="text-[10px] text-slate-400 flex items-center gap-1">
                <span className="text-emerald-500 font-bold">✓</span> Frustum culling
              </div>
              <div className="text-[10px] text-slate-400 flex items-center gap-1">
                <span className="text-emerald-500 font-bold">✓</span> Instanced meshes
              </div>
              <div className="text-[10px] text-slate-400 flex items-center gap-1">
                <span className="text-emerald-500 font-bold">✓</span> 60 FPS target
              </div>
            </div>

            <div className="flex justify-between items-center bg-slate-900/80 border border-slate-900 px-3 py-2 rounded-lg">
              <div>
                <div className="text-[9px] uppercase tracking-wider text-slate-500">Active Quality</div>
                <div className="text-xs font-bold text-cyan-400">{mounted ? qualityTier.toUpperCase() : "MEDIUM"}</div>
              </div>
              <button 
                onClick={() => getScrollController().setProgress(0.0)} 
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-bold py-1 px-3 rounded border border-slate-700 cursor-pointer transition"
              >
                Reset Progress
              </button>
            </div>
          </div>
        </aside>

        {/* Right Scroll Panel */}
        <main ref={scrollContainerRef} className="ml-[380px] w-[calc(100%-380px)] min-h-screen relative z-10 flex flex-col items-center">
          
          {/* Spacer to push first card down */}
          <div className="h-[25vh]" />

          {/* Scrollable scene cards list */}
          <div className="w-full max-w-xl px-6 flex flex-col gap-[35vh]">
            {scenes.map((scene) => {
              // Highlight scene card if active in store (supports scene 7 & 8 mapping to final slide)
              const isActive = currentScene === scene.num || (scene.num === 7 && currentScene === 8);
              
              return (
                <section
                  key={scene.num}
                  onClick={() => getScrollController().setProgress(scene.progress)}
                  className={`group relative bg-slate-900/40 backdrop-blur-md border rounded-xl p-6 cursor-pointer transition-all duration-500 flex flex-col justify-between min-h-[220px] ${
                    isActive
                      ? "border-cyan-500 bg-slate-900/70 shadow-lg shadow-cyan-500/10 scale-[1.02]"
                      : "border-slate-900 hover:border-slate-800 hover:bg-slate-900/50"
                  }`}
                >
                  {/* Subtle Neon Glow for Active Cards */}
                  {isActive && (
                    <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 blur opacity-75 pointer-events-none" />
                  )}

                  {/* Header Row */}
                  <div className="flex w-full justify-between items-start">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
                        Scene {scene.num}
                      </span>
                      <h2 className="text-xl font-extrabold text-white mt-0.5 tracking-tight group-hover:text-cyan-300 transition-colors">
                        {scene.name}
                      </h2>
                    </div>
                    <span className="text-xs font-bold text-slate-500 tracking-wider">
                      {scene.pct}
                    </span>
                  </div>

                  {/* Subtitle */}
                  <div className="text-xs font-semibold text-slate-400 mt-2">
                    {scene.sub}
                  </div>

                  {/* Description */}
                  <p className="text-xs text-slate-300 mt-3 leading-relaxed">
                    {scene.desc}
                  </p>

                  {/* Tags and CTA */}
                  <div className="mt-6 flex flex-wrap justify-between items-center gap-4">
                    <div className="flex flex-wrap gap-1.5">
                      {scene.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-[9px] font-medium bg-slate-950/60 text-slate-400 px-2 py-0.5 rounded border border-slate-900"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>

                    {/* Final Action Button */}
                    {scene.isLast && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          alert("Welcome to the Software Intelligence Universe!");
                        }}
                        className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold py-1.5 px-4 rounded-full shadow-lg shadow-purple-500/20 transition cursor-pointer border-none outline-none"
                      >
                        Enter The Universe
                      </button>
                    )}
                  </div>
                </section>
              );
            })}
          </div>

          {/* Bottom spacing to ensure final scene cards can be scrolled into view */}
          <div className="h-[35vh]" />
        </main>
<<<<<<< HEAD

        {/* Audio Control UI Overlay */}
        <AudioToggle />
=======
>>>>>>> 1ed8369a21b3194523231ccb83db6a2ca4e39902
      </div>
    </div>
  );
}
