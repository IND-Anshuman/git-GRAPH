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

    // Default rail definition if config isn't loaded yet
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
      controller.setLookAtTarget("origin"); // fallback target
    }

    cameraControllerRef.current = controller;
  }, [currentScene, isReady]);

  useFrame((state) => {
    // Sync spatial audio listener with the camera position/rotation
    AudioSystem.getInstance().updateListener(camera);

    if (!shouldAnimate || !cameraControllerRef.current) return;

    const store = useOnboardingStore.getState();
    const { start, end } = store.getSceneBoundaries(currentScene);
    const range = end - start;
    const localProgress = range === 0 ? 1.0 : (store.scrollProgress - start) / range;

    // Parallax effect based on pointer (mouse/touch coordinates in [-1, 1] range)
    const mouseX = state.pointer.x * 2.0; // scale to 2 units range
    const mouseY = state.pointer.y * 2.0;
    cameraControllerRef.current.addOffset(new THREE.Vector3(mouseX, mouseY, 0));

    const cameraState = cameraControllerRef.current.updateCamera(localProgress);

    // Smooth lerp for position, rotation, and fov to prevent jerky motion
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
    // Poll current scene opacities from SceneManager
    const newOpacities: Record<number, number> = {};
    for (let i = 1; i <= 8; i++) {
      newOpacities[i] = sceneManager.getSceneOpacity(i as any);
    }
    setOpacities(newOpacities);

    // Update active GPU shader-based particle animations
    ParticleAnimator.getInstance().update(delta);

    // Apply Level of Detail (LOD) and Frustum Culling to active particle groups
    activeGroups.forEach((group) => {
      // Swap geometries based on distance & cull out-of-screen instances concurrently
      ParticleLODManager.getInstance().updateLOD(group, state.camera);
    });
  });

  return (
    <group>
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />

      {/* Render GPU particles for active scenes */}
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
      // Adjust particle count limits instantly
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
 * OnboardingCanvas provides the core canvas workspace for R3F,
 * checking WebGL availability and executing fallback configurations.
 */
export function OnboardingCanvas() {
  const [hasWebGL, setHasWebGL] = useState<boolean | null>(null);
  const currentScene = useOnboardingStore((s) => s.currentScene);
  const setCurrentScene = useOnboardingStore((s) => s.setCurrentScene);
  const qualityTier = useOnboardingStore((s) => s.qualityTier);

  // Determine initial antialiasing once on mount to prevent WebGL context recreation crashes
  const [initialAntialias] = useState(() => {
    if (typeof window !== "undefined") {
      const tier = useOnboardingStore.getState().qualityTier;
      return tier !== "low";
    }
    return true;
  });

  // Global keyboard accessibility listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      InteractionHandler.getInstance().handleKeyDown(e);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  // Scene 7 -> Scene 8 automatic transition timer at scroll bounds progress 1.00
  useEffect(() => {
    if (currentScene === 7) {
      const timer = setTimeout(() => {
        setCurrentScene(8);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [currentScene, setCurrentScene]);

  // Audio system transition trigger
  useEffect(() => {
    const audio = AudioSystem.getInstance();
    audio.playWhoosh();
    audio.adjustVolumeForScene(currentScene);
  }, [currentScene]);

  useEffect(() => {
    try {
      const canvas = document.createElement("canvas");
      const support = !!(
        (window.WebGL2RenderingContext && canvas.getContext("webgl2")) ||
        (window.WebGLRenderingContext && (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")))
      );
      setHasWebGL(support);
    } catch {
      setHasWebGL(false);
    }
  }, []);

  if (hasWebGL === null) {
    return <div className="h-full w-full bg-slate-950" />;
  }

  if (hasWebGL === false) {
    return (
      <div className="flex h-screen w-[calc(100vw-380px)] ml-[380px] items-center justify-center bg-slate-950 text-white p-6 text-center z-50 relative select-none">
        <div className="max-w-md">
          <h2 className="text-2xl font-black text-rose-500 tracking-wider font-mono uppercase">
            WebGL Context Failed
          </h2>
          <p className="mt-4 text-xs text-slate-400 leading-relaxed font-sans">
            Your browser or graphics driver failed to allocate a WebGL context. Please enable hardware acceleration in your browser settings, restart your browser, or close other heavy WebGL tabs to free up GPU resources.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full bg-slate-950 overflow-hidden">
      <Canvas
        dpr={qualityTier === "low" ? 1.0 : qualityTier === "medium" ? 1.0 : qualityTier === "high" ? 1.25 : [1, 1.5]}
        gl={{
          antialias: initialAntialias, // Avoid WebGL context recreation crashes on quality change
          alpha: false,
          powerPreference: "high-performance"
        }}
        shadows={false} // Explicitly disable shadow maps to prevent dynamic shadow calculation overhead
        camera={{ position: [0, 0, -50], fov: 75 }}
      >
        <color attach="background" args={["#000000"]} />
        <CameraRig />
        <SceneContainer />
        <PerformanceMonitorHelper />
        <InteractionBridge />
        <InfoCardOverlay />
        <PostProcessingEffects />
      </Canvas>
      <SceneOneExplanationHUD />
    </div>
  );
}



/**
 * Animated Holographic HUD overlay that displays explanatory logs and introduction metadata
 * for Scene 1 (The Chaos). It automatically fades out when the user scrolls to subsequent scenes.
 */
function SceneOneExplanationHUD() {
  const currentScene = useOnboardingStore((s) => s.currentScene);
  const [visible, setVisible] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  // Fade in HUD on mount/scene active
  useEffect(() => {
    if (currentScene === 1) {
      const timer = setTimeout(() => setVisible(true), 600);
      return () => clearTimeout(timer);
    } else {
      setVisible(false);
    }
  }, [currentScene]);

  // Type simulated system log lines sequentially
  useEffect(() => {
    if (currentScene !== 1) {
      setLogs([]);
      return;
    }

    const logMessages = [
      "INITIALIZING INTEL SCAN...",
      "FOUND: 10,231 COMPONENT NODES",
      "STATUS: COGNITIVE OVERLOAD",
      "READY FOR SEMANTIC COMPILATION"
    ];

    let currentLogIndex = 0;
    const interval = setInterval(() => {
      if (currentLogIndex < logMessages.length) {
        setLogs((prev) => [...prev, logMessages[currentLogIndex]]);
        currentLogIndex++;
      } else {
        clearInterval(interval);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [currentScene]);

  if (!visible) return null;

  return (
    <div className="absolute top-[48%] left-[62%] -translate-x-1/2 -translate-y-1/2 z-30 w-full max-w-md px-4 transition-all duration-700 ease-out pointer-events-none select-none">
      {/* Holographic container */}
      <div className="relative bg-slate-950/80 backdrop-blur-lg border border-cyan-500/20 rounded-xl p-6 shadow-2xl shadow-cyan-500/5 animate-fade-in flex flex-col gap-4">
        
        {/* Animated laser line */}
        <div className="absolute inset-x-0 top-0 h-[1.5px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-scan" />

        {/* HUD Brackets */}
        <span className="absolute top-0 left-0 w-3.5 h-3.5 border-t-2 border-l-2 border-cyan-500/40 rounded-tl" />
        <span className="absolute top-0 right-0 w-3.5 h-3.5 border-t-2 border-r-2 border-cyan-500/40 rounded-tr" />
        <span className="absolute bottom-0 left-0 w-3.5 h-3.5 border-b-2 border-l-2 border-cyan-500/40 rounded-bl" />
        <span className="absolute bottom-0 right-0 w-3.5 h-3.5 border-b-2 border-r-2 border-cyan-500/40 rounded-br" />

        {/* System Title */}
        <div className="flex items-center justify-between border-b border-slate-900 pb-2.5">
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-ping" />
            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-400 font-mono">
              System Monitor: raw chaos
            </h3>
          </div>
          <span className="text-[9px] font-bold text-slate-650 font-mono">
            SEC_LOG // 01
          </span>
        </div>

        {/* Content details */}
        <div className="flex flex-col gap-1.5">
          <h2 className="text-base font-extrabold tracking-tight text-white leading-snug">
            Why We Are Building Git-Graph
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed font-medium">
            Modern enterprise repositories are too vast to comprehend. We are building Git-Graph to compile this chaotic drift of isolated source files into a unified, interactive semantic map. By automatically mapping dependencies and resolving relations, we turn raw code into searchable, visible structural intelligence.
          </p>
        </div>

        {/* Holographic system shell logs */}
        <div className="bg-slate-950/90 border border-slate-900 rounded p-2.5 font-mono text-[9px] text-cyan-400/80 flex flex-col gap-1 min-h-[70px] justify-end">
          {logs.map((log, idx) => (
            <div key={idx} className="flex gap-1.5 items-center">
              <span className="text-cyan-500/40">&gt;</span>
              <span>{log}</span>
            </div>
          ))}
          <div className="flex gap-1.5 items-center animate-pulse">
            <span className="text-cyan-500/40">&gt;</span>
            <span className="h-2.5 w-1 bg-cyan-400" />
          </div>
        </div>

        {/* HUD control hotkeys */}
        <div className="border-t border-slate-900 pt-2.5 flex justify-between items-center text-[9px] font-mono text-slate-500">
          <div className="flex items-center gap-1.5">
            <span className="text-cyan-400/75 font-semibold">[MOUSE]</span>
            <span>Hover files to query node</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-indigo-400/75 font-semibold">[SCROLL]</span>
            <span>Scroll down to build order</span>
          </div>
        </div>
      </div>
    </div>
  );
}
