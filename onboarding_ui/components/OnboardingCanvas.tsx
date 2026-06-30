// Task 1.16: OnboardingCanvas - Sets up R3F context, CameraRig, SceneContainer, and Performance monitor

"use client";

import { useEffect, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { CameraController } from "@/lib/CameraController";
import { SceneManager } from "@/lib/SceneManager";
import { PerformanceMonitor } from "@/lib/PerformanceMonitor";
import { ParticleSystemEngine } from "@/lib/ParticleSystemEngine";
import { AudioSystem } from "@/lib/AudioSystem";
import { ParticleLODManager } from "@/lib/ParticleLOD";
import { ParticleAnimator } from "@/lib/ParticleAnimator";
import { ChaosScene } from "./scenes/ChaosScene";
import { StardustScene } from "./scenes/StardustScene";
import { ConstellationScene } from "./scenes/ConstellationScene";
import { PlanetScene } from "./scenes/PlanetScene";
import { SolarSystemScene } from "./scenes/SolarSystemScene";
import { DecisionRingScene } from "./scenes/DecisionRingScene";
import { ReasoningNetworkScene } from "./scenes/ReasoningNetworkScene";
import { UniverseScene } from "./scenes/UniverseScene";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { InfoCardOverlay } from "./InfoCardOverlay";
import { PostProcessingEffects } from "./PostProcessingEffects";

/**
 * InteractionBridge invokes the centralized raycaster on every frame
 * with R3F pointer coordinates (throttled inside the handler).
 */
function InteractionBridge() {
  const { camera, pointer } = useThree();

  useFrame(() => {
    InteractionHandler.getInstance().raycast(camera, pointer);
  });

  return null;
}

/**
 * CameraRig hooks into React Three Fiber's render loop (useFrame)
 * to smoothly animate the camera's position, rotation, and FOV along
 * spline rails based on scroll progress and active scene boundaries.
 */
function CameraRig() {
  const { camera } = useThree();
  const currentScene = useOnboardingStore((state) => state.currentScene);
  const isReady = useOnboardingStore((state) => state.isSceneReady(currentScene));
  const shouldAnimate = useShouldAnimateCamera();
  const cameraControllerRef = useRef<CameraController | null>(null);

  useEffect(() => {
    const sceneManager = SceneManager.getInstance();
    const config = sceneManager.getSceneConfig(currentScene);

    const defaultRail = {
      sceneNumber: currentScene,
      splineType: "catmullRom" as const,
      keyframes: [
        { progress: 0.0, position: [0, 0, (currentScene - 4.5) * 20 - 10] as [number, number, number], rotation: [0, 0, 0] as [number, number, number], fov: 75 },
        { progress: 1.0, position: [0, 0, (currentScene - 4.5) * 20 + 10] as [number, number, number], rotation: [0, 0, 0] as [number, number, number], fov: 75 }
      ]
    };

    const rail = config?.camera ?? defaultRail;

    const controller = new CameraController({
      sceneNumber: currentScene,
      splineType: "catmullRom",
      keyframes: rail.keyframes,
    });

    if (config?.camera?.lookAtTarget) {
      controller.setLookAtTarget(config.camera.lookAtTarget);
    } else {
      controller.setLookAtTarget("origin");
    }

    cameraControllerRef.current = controller;
  }, [currentScene, isReady]);

  useFrame((state) => {
    AudioSystem.getInstance().updateListener(camera);

    if (!shouldAnimate || !cameraControllerRef.current) return;

    const store = useOnboardingStore.getState();
    const { start, end } = store.getSceneBoundaries(currentScene);
    const range = end - start;
    const localProgress = range === 0 ? 1.0 : (store.scrollProgress - start) / range;

    const mouseX = state.pointer.x * 2.0;
    const mouseY = state.pointer.y * 2.0;
    cameraControllerRef.current.addOffset(new THREE.Vector3(mouseX, mouseY, 0));

    const cameraState = cameraControllerRef.current.updateCamera(localProgress);

    camera.position.lerp(cameraState.position, 0.1);
    camera.quaternion.slerp(new THREE.Quaternion().setFromEuler(cameraState.rotation), 0.1);

    if (camera instanceof THREE.PerspectiveCamera) {
      camera.fov = THREE.MathUtils.lerp(camera.fov, cameraState.fov, 0.1);
      camera.updateProjectionMatrix();
    }
  });

  return null;
}

/**
 * SceneContainer renders geometric representations of each scene and binds
 * their opacities to the SceneManager's active transition crossfade.
 */
function SceneContainer() {
  const sceneManager = SceneManager.getInstance();
  const currentScene = useOnboardingStore((state) => state.currentScene);
  const [opacities, setOpacities] = useState<Record<number, number>>({});

  const activeGroups: any[] = [];
  for (let i = 1; i <= 8; i++) {
    const sceneNum = i as any;
    const opacity = opacities[sceneNum] ?? 0;
    if (opacity > 0.001) {
      const group = ParticleSystemEngine.getInstance().getGroup(`scene-${sceneNum}`);
      if (group) {
        activeGroups.push(group);
      }
    }
  }

  useFrame((state, delta) => {
    const newOpacities: Record<number, number> = {};
    for (let i = 1; i <= 8; i++) {
      newOpacities[i] = sceneManager.getSceneOpacity(i as any);
    }
    setOpacities(newOpacities);

    ParticleAnimator.getInstance().update(delta);

    activeGroups.forEach((group) => {
      ParticleLODManager.getInstance().updateLOD(group, state.camera);
    });
  });

  return (
    <group>
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />

      {activeGroups.map((group) => (
        <primitive key={group.id} object={group.container} />
      ))}

      {Array.from({ length: 8 }).map((_, idx) => {
        const sceneNum = (idx + 1) as any;
        const opacity = opacities[sceneNum] ?? 0;

        if (opacity <= 0.001) return null;

        const config = sceneManager.getSceneConfig(sceneNum);

        if (sceneNum === 1 && config) {
          return <ChaosScene key={sceneNum} active={currentScene === 1} config={config} />;
        }
        if (sceneNum === 2 && config) {
          return <StardustScene key={sceneNum} active={currentScene === 2} config={config} />;
        }
        if (sceneNum === 3 && config) {
          return <ConstellationScene key={sceneNum} active={currentScene === 3} config={config} />;
        }
        if (sceneNum === 4 && config) {
          return <PlanetScene key={sceneNum} active={currentScene === 4} config={config} />;
        }
        if (sceneNum === 5 && config) {
          return <SolarSystemScene key={sceneNum} active={currentScene === 5} config={config} />;
        }
        if (sceneNum === 6 && config) {
          return <DecisionRingScene key={sceneNum} active={currentScene === 6} config={config} />;
        }
        if (sceneNum === 7 && config) {
          return <ReasoningNetworkScene key={sceneNum} active={currentScene === 7} config={config} />;
        }
        if (sceneNum === 8 && config) {
          return <UniverseScene key={sceneNum} active={currentScene === 8} config={config} />;
        }

        return null;
      })}
    </group>
  );
}

/**
 * PerformanceMonitorHelper starts FPS tracking and quality auto-tuning
 * when the component mounts and stops it when it unmounts.
 */
function PerformanceMonitorHelper() {
  useEffect(() => {
    const monitor = PerformanceMonitor.getInstance();
    monitor.start();

    const unsubscribe = monitor.onQualityChange((tier) => {
      useOnboardingStore.getState().setQualityTier(tier);
      ParticleSystemEngine.getInstance().adjustQuality(tier);
    });

    return () => {
      unsubscribe();
      monitor.stop();
    };
  }, []);

  return null;
}

/**
 * SceneTransparencyController makes the WebGL canvas transparent for Scene 1
 * (so the CSS star field gradient shows through) and opaque for all other scenes.
 */
function SceneTransparencyController() {
  const { gl } = useThree();
  const currentScene = useOnboardingStore((s) => s.currentScene);

  useEffect(() => {
    if (currentScene === 1 || currentScene === 2) {
      gl.setClearColor(0x000000, 0); // fully transparent
    } else {
      gl.setClearColor(0x000010, 1); // opaque dark blue-black
    }
  }, [currentScene, gl]);

  return null;
}

/**
 * High-performance 2D Canvas Starfield that draws organic, glowing,
 * and twinkling stars with different sizes, colors, and twinkling cycles.
 */
function StarfieldCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // Generate stars with diverse sizes, colors (white, blue, gold, purple), and twinkle cycles
    const stars = Array.from({ length: 180 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 2.2 + 0.5,
      color: ["#ffffff", "#e0f2fe", "#fef3c7", "#fae8ff"][Math.floor(Math.random() * 4)],
      speed: Math.random() * 0.015 + 0.005,
      phase: Math.random() * Math.PI * 2,
      glow: Math.random() > 0.88 // 12% of stars have a premium glow halo
    }));

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener("resize", handleResize);

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      stars.forEach((star) => {
        star.phase += star.speed;
        const opacity = 0.25 + Math.abs(Math.sin(star.phase)) * 0.75;

        ctx.fillStyle = star.color;
        ctx.globalAlpha = opacity;

        if (star.glow) {
          const glowRad = star.size * 3.5;
          const glowGrad = ctx.createRadialGradient(star.x, star.y, 0, star.x, star.y, glowRad);
          glowGrad.addColorStop(0, star.color);
          glowGrad.addColorStop(0.3, "rgba(255, 255, 255, 0.18)");
          glowGrad.addColorStop(1, "transparent");
          ctx.fillStyle = glowGrad;
          ctx.beginPath();
          ctx.arc(star.x, star.y, glowRad, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.fillStyle = star.color;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
    />
  );
}

/**
 * Scene1UniverseBackground renders a pure 2D CSS universe sky behind the WebGL canvas.
 * It uses only CSS gradients and pseudo-element dots — zero GPU compute, ideal for low-end devices.
 */
function Scene1UniverseBackground({ visible }: { visible: boolean }) {
  return (
    <div
      className="scene1-universe-bg"
      style={{
        position: "absolute",
        inset: 0,
        zIndex: 0,
        pointerEvents: "none",
        opacity: visible ? 1 : 0,
        transition: "opacity 1.2s ease",
        background: [
          // Deep space gradient — multiple layered radial gradients
          "radial-gradient(ellipse 160% 100% at 50% 120%, #1e0040 0%, transparent 55%)",
          "radial-gradient(ellipse 80% 60% at 20% 30%, #0d1b4a 0%, transparent 50%)",
          "radial-gradient(ellipse 60% 50% at 80% 70%, #0c0628 0%, transparent 45%)",
          "radial-gradient(ellipse 120% 80% at 50% 50%, #04001a 0%, #000010 100%)",
        ].join(", "),
        overflow: "hidden",
      }}
    >
      {/* Dynamic, premium HTML5 2D Canvas Starfield */}
      {visible && <StarfieldCanvas />}

      {/* Nebula color washes — soft purple/teal blobs */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: [
            "radial-gradient(ellipse 50% 35% at 15% 25%, rgba(124,58,237,0.12) 0%, transparent 70%)",
            "radial-gradient(ellipse 40% 30% at 85% 65%, rgba(6,182,212,0.09) 0%, transparent 70%)",
            "radial-gradient(ellipse 35% 25% at 55% 80%, rgba(244,63,94,0.07) 0%, transparent 65%)",
          ].join(", "),
        }}
      />
    </div>
  );
}

/**
 * OnboardingCanvas provides the core canvas workspace for R3F,
 * checking WebGL availability and executing fallback configurations.
 */
export function OnboardingCanvas() {
  const [hasWebGL, setHasWebGL] = useState<boolean | null>(null);
  const currentScene = useOnboardingStore((s) => s.currentScene);
  const setCurrentScene = useOnboardingStore((s) => s.setCurrentScene);
  const qualityTier = useOnboardingStore((s) => s.qualityTier);

  const [initialAntialias] = useState(() => {
    if (typeof window !== "undefined") {
      const tier = useOnboardingStore.getState().qualityTier;
      return tier !== "low";
    }
    return true;
  });

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      InteractionHandler.getInstance().handleKeyDown(e);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  useEffect(() => {
    if (currentScene === 7) {
      const timer = setTimeout(() => {
        setCurrentScene(8);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [currentScene, setCurrentScene]);

  useEffect(() => {
    const audio = AudioSystem.getInstance();
    audio.playWhoosh();
    audio.adjustVolumeForScene(currentScene);
  }, [currentScene]);

  useEffect(() => {
    let support = false;
    try {
      const canvas = document.createElement("canvas");
      const gl = canvas.getContext("webgl2") || canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
      if (gl) {
        const renderer = new THREE.WebGLRenderer({ canvas });
        renderer.dispose();
        support = true;
      }
    } catch (err) {
      support = false;
    }
    setHasWebGL(support);
  }, []);

  if (hasWebGL === null) {
    return <div className="h-full w-full bg-slate-950" />;
  }

  if (hasWebGL === false) {
    return (
      <div className="flex h-screen w-[calc(100vw-380px)] ml-[380px] items-center justify-center bg-slate-950 text-slate-100 p-8 select-none relative overflow-hidden font-sans">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,#0c0628_0%,#000000_100%)] opacity-80" />
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:40px_40px] opacity-25" />
        
        <div className="relative z-10 w-full max-w-md bg-slate-900/60 backdrop-blur-md border border-rose-500/30 rounded-xl p-8 shadow-2xl shadow-rose-500/5 flex flex-col gap-6">
          <span className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-rose-500/50 rounded-tl" />
          <span className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-rose-500/50 rounded-tr" />
          <span className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-rose-500/50 rounded-bl" />
          <span className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-rose-500/50 rounded-br" />

          <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-500 animate-pulse" />
            <h2 className="text-base font-black tracking-wider text-rose-500 uppercase font-mono">
              WebGL Diagnostics: Locked
            </h2>
          </div>

          <div className="flex flex-col gap-3 text-xs leading-relaxed text-slate-300">
            <p className="font-semibold text-slate-200">
              The Software Intelligence Universe requires WebGL to compile the 3D semantic graph. Your browser reported that hardware acceleration is currently disabled or blocked by the GPU software blocklist.
            </p>
            
            <div className="mt-2 bg-slate-950/80 border border-slate-900 rounded p-4 flex flex-col gap-3 font-mono text-[10px] text-cyan-400">
              <div className="font-bold border-b border-slate-800/60 pb-1.5 text-slate-400">
                QUICK REPAIR PROCEDURES:
              </div>
              <div className="flex gap-2">
                <span className="text-rose-500">1.</span>
                <span>Navigate to <code className="bg-slate-900 px-1 py-0.5 rounded text-white select-all">chrome://settings/system</code></span>
              </div>
              <div className="flex gap-2 ml-4">
                <span className="text-slate-500">-</span>
                <span>Toggle <span className="text-white">"Use graphics acceleration when available"</span> to <span className="text-green-400 font-bold">ON</span></span>
              </div>
              <div className="flex gap-2">
                <span className="text-rose-500">2.</span>
                <span>Navigate to <code className="bg-slate-900 px-1.5 py-0.5 rounded text-white select-all">chrome://flags/#ignore-gpu-blocklist</code></span>
              </div>
              <div className="flex gap-2 ml-4">
                <span className="text-slate-500">-</span>
                <span>Set <span className="text-white">"Override software rendering list"</span> to <span className="text-green-400 font-bold">Enabled</span> (forces WebGL on blocked GPUs)</span>
              </div>
              <div className="flex gap-2">
                <span className="text-rose-500">3.</span>
                <span>Relaunch the browser and refresh this tab.</span>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-4 flex justify-between items-center text-[9px] font-mono text-slate-500">
            <span>DEVICE: LOW-END PROFILE</span>
            <span>GPU STATUS: BLOCKED</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full overflow-hidden" style={{ background: "#000010" }}>
      {/* 2D universe starfield background for Scene 1 & 2 — pure CSS, zero GPU overhead */}
      <Scene1UniverseBackground visible={currentScene === 1 || currentScene === 2} />

      <Canvas
        style={{ position: "relative", zIndex: 1 }}
        dpr={qualityTier === "low" ? 1.0 : qualityTier === "medium" ? 1.0 : qualityTier === "high" ? 1.25 : [1, 1.5]}
        gl={{
          antialias: initialAntialias,
          alpha: true,
          powerPreference: "high-performance"
        }}
        shadows={false}
        camera={{ position: [0, 0, -50], fov: 75 }}
      >
        {/* SceneTransparencyController sets WebGL clearAlpha to 0 for scene 1 (shows CSS stars) */}
        <SceneTransparencyController />
        <CameraRig />
        <SceneContainer />
        <PerformanceMonitorHelper />
        <InteractionBridge />
        <InfoCardOverlay />
        <PostProcessingEffects />
      </Canvas>
      <UniversalExplanationHUD />
    </div>
  );
}

const sceneExplanations: Record<number, { title: string; subtitle: string; desc: string; reason: string; logs: string[] }> = {
  1: {
    title: "Why We Are Building Git-Graph",
    subtitle: "The Chaos of Code",
    desc: "Modern enterprise codebases have become too vast to navigate mentally. We build Git-Graph to compile this chaotic drift of isolated source files into an interactive, visible semantic map.",
    reason: "Drifting files represent the cognitive overload that developers face daily before structural compilation.",
    logs: ["SCANNING REPOSITORY FILES...", "FOUND: 10,231 COMPONENT NODES", "STATUS: COGNITIVE OVERLOAD", "READY FOR SEMANTIC COMPILATION"]
  },
  2: {
    title: "Decomposing to Stardust",
    subtitle: "Semantic Extraction",
    desc: "To map software intelligence, we must decompose code into its atomic blocks—classes, functions, APIs, and database schemas. This is the raw stardust of repository evidence.",
    reason: "By breaking code into granular semantic particles, we can index, connect, and analyze the entire architecture flow.",
    logs: ["DECOMPOSING FILE STRUCTURES...", "EXTRACTING CLASSES & METHODS", "NODES INDEXED: 128,430 UNITS", "EMITTING SEMANTIC PARTICLES"]
  },
  3: {
    title: "Assembling Capability Planets",
    subtitle: "Mapping What Code Does",
    desc: "Individual code nodes form functional clusters. Related code files orbit together to form capabilities—such as Authentication or Payments—that deliver real business value.",
    reason: "Capabilities are represented as solid planetary bodies, visualizing code functional groupings as constellations.",
    logs: ["CLUSTERING BUSINESS LOGIC...", "FOUND CONSTELLATION: AUTH_SERVER", "HEALTH METRICS COMPILED", "ORBITAL SHELLS GENERATED"]
  },
  4: {
    title: "Structuring Solar Systems",
    subtitle: "Domain Architecture Mapping",
    desc: "Capabilities do not exist in isolation; they form complex systems. We organize these systems into distinct architectural domains, forming solar systems of software topology.",
    reason: "Solar systems show bounded contexts and domain boundaries, mapping how systems communicate structurally.",
    logs: ["RESOLVING BOUNDED CONTEXTS...", "SYSTEMS CONNECTED: 8 DOMAINS", "ARCHITECTURE MAP COMPILED", "INTER-DOMAIN PATHWAYS ACTIVE"]
  },
  5: {
    title: "Uncovering Decision Rings",
    subtitle: "Evolutionary History (ADRs)",
    desc: "A codebase is a history of human choices. We compile architectural decisions (ADRs) and map them as orbiting rings around capability planets, showing the reasoning behind the structure.",
    reason: "Orbiting rings represent why capabilities evolved, exposing historical trade-offs directly over the code shape.",
    logs: ["IMPORTING ADR DOCUMENTS...", "MAPPED DECISIONS: 147 ADRs", "EVOLUTION SHAPE GENERATED", "DECISION RING BIND COMPLETE"]
  },
  6: {
    title: "Constellation of Reasoning",
    subtitle: "Interactive Impact Analysis",
    desc: "We run a reasoning neural network over the unified knowledge graph to answer questions, analyze architectural impact, and surface critical code health insights.",
    reason: "Neural sparks show active query pathways traveling between evidence nodes to resolve resolve complex questions.",
    logs: ["INITIALIZING NEURAL GRAPH...", "COMPILING EVOLVED INSIGHTS", "REASONING PATHWAYS ACTIVE", "ANALYSIS PIPELINE READY"]
  },
  7: {
    title: "The Knowledge Universe",
    subtitle: "Unified Software Intelligence",
    desc: "Everything converges into a living knowledge universe. Code, systems, decisions, and reasoning are integrated into a single interactive map of software intelligence.",
    reason: "This unified space is the final state—your entire enterprise architecture turned searchable and visible.",
    logs: ["UNIVERSE SYNCHRONIZATION COMPLETED", "SEMANTIC INTEL MAP ACTIVE", "SYSTEM STATUS: 100% ONLINE", "READY FOR OPERATOR COMMANDS"]
  }
};

function UniversalExplanationHUD() {
  const currentScene = useOnboardingStore((s) => s.currentScene);
  const scrollProgress = useOnboardingStore((s) => s.scrollProgress);
  const [logs, setLogs] = useState<string[]>([]);
  const cardRef = useRef<HTMLDivElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  const activeInfo = sceneExplanations[currentScene];
  const localProgress = Math.max(0, Math.min(1, (scrollProgress - 0.17) / 0.16));
  const extractionProgress = localProgress <= 0.3 
    ? 0 
    : localProgress <= 0.7 
      ? Math.round(((localProgress - 0.3) / 0.4) * 68) 
      : Math.round(68 + ((localProgress - 0.7) / 0.3) * 32);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouseRef.current.y = (e.clientY / window.innerHeight) * 2 - 1;
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  useEffect(() => {
    let animationFrameId: number;
    const currentRot = { x: 0, y: 0 };
    const currentScrollTrans = { x: 60, y: 0, scale: 0.9, opacity: 0 };

    const update = () => {
      if (!cardRef.current) {
        animationFrameId = requestAnimationFrame(update);
        return;
      }

      currentRot.x += (mouseRef.current.y * -16.0 - currentRot.x) * 0.07;
      currentRot.y += (mouseRef.current.x * 16.0 - currentRot.y) * 0.07;

      const store = useOnboardingStore.getState();
      const current = store.currentScene;
      const scroll = store.scrollProgress;
      const info = sceneExplanations[current];

      if (!info) {
        cardRef.current.style.opacity = "0";
        cardRef.current.style.pointerEvents = "none";
        animationFrameId = requestAnimationFrame(update);
        return;
      }

      const boundaries = store.getSceneBoundaries(current);
      const range = boundaries.end - boundaries.start;
      const localProgress = range === 0 ? 1.0 : (scroll - boundaries.start) / range;
      const clampedProgress = Math.max(0.0, Math.min(1.0, localProgress));

      let targetOpacity = 1.0;
      let targetX = 0;
      let targetY = 0;
      let targetScale = 1.0;

      if (clampedProgress < 0.20) {
        const t = clampedProgress / 0.20;
        targetOpacity = t;
        targetX = (1 - t) * 60;
        targetScale = 0.92 + t * 0.08;
      } else if (clampedProgress > 0.80) {
        const t = (clampedProgress - 0.80) / 0.20;
        targetOpacity = 1 - t;
        targetY = -t * 40;
        targetScale = 1.0 - t * 0.04;
      } else {
        const floatProgress = (clampedProgress - 0.20) / 0.60;
        targetY = Math.sin(floatProgress * Math.PI) * 12;
      }

      currentScrollTrans.opacity += (targetOpacity - currentScrollTrans.opacity) * 0.10;
      currentScrollTrans.x += (targetX - currentScrollTrans.x) * 0.10;
      currentScrollTrans.y += (targetY - currentScrollTrans.y) * 0.10;
      currentScrollTrans.scale += (targetScale - currentScrollTrans.scale) * 0.10;

      cardRef.current.style.opacity = currentScrollTrans.opacity.toString();
      cardRef.current.style.pointerEvents = currentScrollTrans.opacity > 0.1 ? "auto" : "none";
      cardRef.current.style.transform = `
        translate(-50%, -50%) 
        translate3d(${currentScrollTrans.x}px, ${currentScrollTrans.y}px, 0) 
        scale(${currentScrollTrans.scale}) 
        perspective(1200px) 
        rotateX(${currentRot.x}deg) 
        rotateY(${currentRot.y}deg)
      `;

      animationFrameId = requestAnimationFrame(update);
    };

    update();
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  useEffect(() => {
    setLogs([]);
    if (!activeInfo) return;

    let currentLogIndex = 0;
    const interval = setInterval(() => {
      if (currentLogIndex < activeInfo.logs.length) {
        setLogs((prev) => [...prev, activeInfo.logs[currentLogIndex]]);
        currentLogIndex++;
      } else {
        clearInterval(interval);
      }
    }, 600);

    return () => clearInterval(interval);
  }, [currentScene, activeInfo]);

  if (!activeInfo) return null;

  return (
    <div 
      ref={cardRef}
      className="absolute top-[80%] left-[94%] -translate-x-1/2 -translate-y-1/2 z-30 w-full max-w-md px-4 select-none"
      style={{
        transformStyle: "preserve-3d",
        willChange: "transform, opacity"
      }}
    >
      <div 
        className="relative bg-[#0d0920]/80 backdrop-blur-2xl border border-purple-500/20 border-t-purple-400/40 rounded-2xl p-6 shadow-[0_0_50px_rgba(168,85,247,0.12)] flex flex-col gap-4"
        style={{ transformStyle: "preserve-3d" }}
      >
        <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-tr from-purple-500/0 via-purple-500/10 to-cyan-400/15 pointer-events-none" />

        <div 
          className="absolute inset-x-0 top-0 h-[1.5px] bg-gradient-to-r from-transparent via-purple-400 to-transparent animate-scan"
          style={{ transform: "translateZ(40px)" }}
        />

        <span className="absolute top-0 left-0 w-3.5 h-3.5 border-t-2 border-l-2 border-purple-500/50 rounded-tl" />
        <span className="absolute top-0 right-0 w-3.5 h-3.5 border-t-2 border-r-2 border-purple-500/50 rounded-tr" />
        <span className="absolute bottom-0 left-0 w-3.5 h-3.5 border-b-2 border-l-2 border-purple-500/50 rounded-bl" />
        <span className="absolute bottom-0 right-0 w-3.5 h-3.5 border-b-2 border-r-2 border-purple-500/50 rounded-br" />

        <div 
          className="flex items-center justify-between border-b border-slate-900/60 pb-2.5"
          style={{ transform: "translateZ(25px)" }}
        >
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-purple-400 animate-ping" />
            <h3 className="text-[9px] font-bold uppercase tracking-[0.22em] text-purple-400 font-mono">
              System Monitor: {activeInfo.subtitle}
            </h3>
          </div>
          <span className="text-[9px] font-bold text-slate-500 font-mono">
            SEC_LOG // 0{currentScene}
          </span>
        </div>

        <div className="flex flex-col gap-1.5">
          <h2 
            className="text-sm font-extrabold tracking-tight bg-gradient-to-r from-purple-200 via-indigo-100 to-cyan-200 bg-clip-text text-transparent leading-snug"
            style={{ transform: "translateZ(35px)" }}
          >
            {activeInfo.title}
          </h2>
          <p 
            className="text-[11px] text-slate-350 leading-relaxed font-normal"
            style={{ transform: "translateZ(20px)" }}
          >
            {activeInfo.desc}
          </p>
        </div>

        {currentScene === 2 && (
          <div 
            className="flex flex-col gap-2 font-mono text-[9px] bg-slate-950/50 border border-purple-500/10 rounded-xl p-3"
            style={{ transform: "translateZ(20px)" }}
          >
            <style>{`
              @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
              }
              .animate-shimmer {
                animation: shimmer 2.2s infinite linear;
              }
            `}</style>
            <div className="flex items-center justify-between text-cyan-400 font-bold uppercase tracking-wider">
              <span>Extraction In Progress</span>
              <span className="text-xs">{extractionProgress}%</span>
            </div>
            <div className="relative h-2 bg-slate-900 rounded-full overflow-hidden border border-white/5">
              <div 
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-400 rounded-full transition-all duration-300 animate-pulse"
                style={{ width: `${extractionProgress}%` }}
              />
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
            </div>
          </div>
        )}

        <div 
          className="bg-slate-950/80 border border-slate-900/80 rounded-xl p-2.5 font-mono text-[9px] text-amber-500/90 flex flex-col gap-1 min-h-[70px] justify-end"
          style={{ transform: "translateZ(15px)" }}
        >
          {logs.map((log, idx) => (
            <div key={idx} className="flex gap-1.5 items-center">
              <span className="text-amber-500/30">&gt;</span>
              <span>{log}</span>
            </div>
          ))}
          <div className="flex gap-1.5 items-center animate-pulse">
            <span className="text-amber-500/30">&gt;</span>
            <span className="h-2.5 w-1 bg-amber-500" />
          </div>
        </div>

        <div 
          className="border-t border-slate-900/60 pt-2.5 flex justify-between items-center text-[9px] font-mono text-slate-500"
          style={{ transform: "translateZ(25px)" }}
        >
          <div className="flex items-center gap-1.5">
            <span className="text-purple-400/80 font-bold uppercase">[DIAGNOSTIC]</span>
            <span>{activeInfo.reason}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
