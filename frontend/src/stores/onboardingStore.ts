/**
 * Onboarding Store — State management for cinematic onboarding experience
 * 
 * This store manages the state for the 3D scroll-driven journey through the
 * Software Intelligence Platform visualization. It tracks scroll progress,
 * scene transitions, interaction state, and quality settings.
 * 
 * **Validates: Requirements 1.1, 19.3**
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

/**
 * Quality tier for rendering performance optimization
 * @see Design: Performance Monitor (Requirement 12)
 */
export type QualityTier = 'ultra' | 'high' | 'medium' | 'low';

/**
 * Scene numbers 1-8 representing the narrative journey
 * @see Design: Visual Narrative Flow
 */
export type SceneNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

/**
 * Loading status for scene assets
 * @see Design: Scene Manager
 */
export type SceneStatus = 'unloaded' | 'loading' | 'ready' | 'active';

/**
 * Core onboarding state interface
 */
interface OnboardingState {
  // ========== Scroll Progress (Requirement 2) ==========
  /**
   * Current scroll position normalized to [0, 1]
   * 0 = journey start, 1 = journey end
   */
  scrollProgress: number;
  
  /**
   * Update scroll progress
   */
  setScrollProgress: (progress: number) => void;

  // ========== Current Scene (Requirement 3-10) ==========
  /**
   * Current active scene (1-8)
   */
  currentScene: SceneNumber;
  
  /**
   * Set current scene
   */
  setCurrentScene: (scene: SceneNumber) => void;

  // ========== Quality Tier (Requirement 12) ==========
  /**
   * Current rendering quality tier
   * Determines particle counts and effects
   */
  qualityTier: QualityTier;
  
  /**
   * Set quality tier (manual or automatic)
   */
  setQualityTier: (tier: QualityTier) => void;

  // ========== Interaction State (Requirement 11) ==========
  /**
   * Currently hovered 3D object ID (null if none)
   */
  hoveredObjectId: string | null;
  
  /**
   * Set hovered object
   */
  setHoveredObject: (id: string | null) => void;
  
  /**
   * Currently expanded info card object ID (null if none)
   */
  expandedCardId: string | null;
  
  /**
   * Expand an info card (pauses camera progression)
   */
  expandCard: (id: string) => void;
  
  /**
   * Close expanded card (resumes camera progression)
   */
  closeCard: () => void;

  // ========== Scene Loading Status (Requirement 16) ==========
  /**
   * Map of scene loading statuses
   */
  sceneStatuses: Record<SceneNumber, SceneStatus>;
  
  /**
   * Update scene loading status
   */
  setSceneStatus: (scene: SceneNumber, status: SceneStatus) => void;

  // ========== Audio State (Requirement 13) ==========
  /**
   * Audio enabled flag
   */
  audioEnabled: boolean;
  
  /**
   * Toggle audio
   */
  toggleAudio: () => void;
  
  /**
   * Set audio enabled
   */
  setAudioEnabled: (enabled: boolean) => void;

  // ========== Accessibility (Requirement 14) ==========
  /**
   * Reduced motion mode (disables animations)
   */
  reducedMotion: boolean;
  
  /**
   * Set reduced motion
   */
  setReducedMotion: (enabled: boolean) => void;
  
  /**
   * Animation skipped flag
   */
  animationSkipped: boolean;
  
  /**
   * Skip to final scene
   */
  skipAnimation: () => void;

  // ========== Progress Persistence (Requirement 19.3, 19.4) ==========
  /**
   * Last completed scene for resume functionality
   */
  lastCompletedScene: SceneNumber | null;
  
  /**
   * Mark scene as completed
   */
  completeScene: (scene: SceneNumber) => void;
  
  /**
   * Reset onboarding progress
   */
  resetProgress: () => void;
  
  /**
   * Journey completed flag
   */
  journeyCompleted: boolean;
  
  /**
   * Mark journey as completed
   */
  completeJourney: () => void;

  // ========== Camera State ==========
  /**
   * Camera progression paused flag
   * True when info card is expanded or user is interacting
   */
  cameraPaused: boolean;
  
  /**
   * Pause camera progression
   */
  pauseCamera: () => void;
  
  /**
   * Resume camera progression
   */
  resumeCamera: () => void;

  // ========== Derived Selectors ==========
  /**
   * Get scene boundaries for a given scene number
   */
  getSceneBoundaries: (scene: SceneNumber) => { start: number; end: number };
  
  /**
   * Check if a scene is loaded and ready
   */
  isSceneReady: (scene: SceneNumber) => boolean;
  
  /**
   * Check if currently in a scene transition
   */
  isInTransition: () => boolean;
}

/**
 * Scene boundary definitions
 * Maps scroll progress ranges to scenes
 */
const SCENE_BOUNDARIES: Record<SceneNumber, { start: number; end: number }> = {
  1: { start: 0.00, end: 0.17 },
  2: { start: 0.17, end: 0.33 },
  3: { start: 0.33, end: 0.50 },
  4: { start: 0.50, end: 0.67 },
  5: { start: 0.67, end: 0.83 },
  6: { start: 0.83, end: 1.00 },
  7: { start: 1.00, end: 1.00 },
  8: { start: 1.00, end: 1.00 },
};

/**
 * Determine current scene from scroll progress
 */
const getSceneFromProgress = (progress: number): SceneNumber => {
  if (progress < 0.17) return 1;
  if (progress < 0.33) return 2;
  if (progress < 0.50) return 3;
  if (progress < 0.67) return 4;
  if (progress < 0.83) return 5;
  if (progress < 1.00) return 6;
  if (progress >= 1.00) return 8; // Final scene
  return 1;
};

/**
 * Detect hardware capabilities and return recommended quality tier
 */
const detectQualityTier = (): QualityTier => {
  if (typeof window === 'undefined') return 'medium';
  
  // Check for GPU tier via WebGL
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  
  if (!gl) return 'low';
  
  // Check hardware concurrency (CPU cores)
  const cores = navigator.hardwareConcurrency || 2;
  
  // Check device memory (if available)
  const memory = (navigator as any).deviceMemory || 4;
  
  // Check screen size
  const width = window.innerWidth;
  
  // Determine tier based on hardware
  if (cores >= 8 && memory >= 8 && width >= 1920) return 'ultra';
  if (cores >= 4 && memory >= 4 && width >= 1280) return 'high';
  if (cores >= 2 && memory >= 2) return 'medium';
  return 'low';
};

/**
 * Onboarding store with persistence for progress tracking
 */
export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      // Initial state
      scrollProgress: 0,
      currentScene: 1,
      qualityTier: detectQualityTier(),
      hoveredObjectId: null,
      expandedCardId: null,
      sceneStatuses: {
        1: 'unloaded',
        2: 'unloaded',
        3: 'unloaded',
        4: 'unloaded',
        5: 'unloaded',
        6: 'unloaded',
        7: 'unloaded',
        8: 'unloaded',
      },
      audioEnabled: false, // Default to disabled per autoplay policies
      reducedMotion: false,
      animationSkipped: false,
      lastCompletedScene: null,
      journeyCompleted: false,
      cameraPaused: false,

      // Actions
      setScrollProgress: (progress) => {
        const clampedProgress = Math.max(0, Math.min(1, progress));
        const newScene = getSceneFromProgress(clampedProgress);
        
        set({
          scrollProgress: clampedProgress,
          currentScene: newScene,
        });
      },

      setCurrentScene: (scene) => set({ currentScene: scene }),

      setQualityTier: (tier) => set({ qualityTier: tier }),

      setHoveredObject: (id) => set({ hoveredObjectId: id }),

      expandCard: (id) => set({ 
        expandedCardId: id,
        cameraPaused: true, // Pause camera when card expands
      }),

      closeCard: () => set({ 
        expandedCardId: null,
        cameraPaused: false, // Resume camera when card closes
      }),

      setSceneStatus: (scene, status) => set((state) => ({
        sceneStatuses: {
          ...state.sceneStatuses,
          [scene]: status,
        },
      })),

      toggleAudio: () => set((state) => ({ audioEnabled: !state.audioEnabled })),

      setAudioEnabled: (enabled) => set({ audioEnabled: enabled }),

      setReducedMotion: (enabled) => set({ reducedMotion: enabled }),

      skipAnimation: () => set({
        animationSkipped: true,
        scrollProgress: 1.0,
        currentScene: 8,
      }),

      completeScene: (scene) => set((state) => ({
        lastCompletedScene: scene > (state.lastCompletedScene || 0) ? scene : state.lastCompletedScene,
      })),

      resetProgress: () => set({
        scrollProgress: 0,
        currentScene: 1,
        lastCompletedScene: null,
        journeyCompleted: false,
        animationSkipped: false,
        expandedCardId: null,
        hoveredObjectId: null,
        cameraPaused: false,
      }),

      completeJourney: () => set({
        journeyCompleted: true,
        lastCompletedScene: 8,
      }),

      pauseCamera: () => set({ cameraPaused: true }),

      resumeCamera: () => set({ cameraPaused: false }),

      // Derived selectors
      getSceneBoundaries: (scene) => SCENE_BOUNDARIES[scene],

      isSceneReady: (scene) => {
        const status = get().sceneStatuses[scene];
        return status === 'ready' || status === 'active';
      },

      isInTransition: () => {
        const { scrollProgress } = get();
        // Check if near a boundary (within 2% threshold)
        const threshold = 0.02;
        const boundaries = [0.17, 0.33, 0.50, 0.67, 0.83, 1.00];
        return boundaries.some(
          (boundary) => Math.abs(scrollProgress - boundary) < threshold
        );
      },
    }),
    {
      name: "sip-onboarding-store",
      storage: createJSONStorage(() => {
        // Graceful localStorage degradation
        if (typeof window !== "undefined") {
          try {
            return localStorage;
          } catch {
            console.warn("[OnboardingStore] localStorage unavailable — progress not persisted");
            return sessionStorage;
          }
        }
        return {
          getItem: () => null,
          setItem: () => {},
          removeItem: () => {},
        };
      }),
      // Only persist progress tracking and preferences
      partialize: (state) => ({
        lastCompletedScene: state.lastCompletedScene,
        journeyCompleted: state.journeyCompleted,
        audioEnabled: state.audioEnabled,
        reducedMotion: state.reducedMotion,
        qualityTier: state.qualityTier,
      }),
    }
  )
);

/**
 * Selector hooks for common derived state
 */

/**
 * Get scene-local progress (0-1 within current scene)
 */
export const useSceneLocalProgress = (): number => {
  return useOnboardingStore((state) => {
    const { start, end } = state.getSceneBoundaries(state.currentScene);
    const range = end - start;
    if (range === 0) return 1.0;
    return (state.scrollProgress - start) / range;
  });
};

/**
 * Check if camera should be animating
 */
export const useShouldAnimateCamera = (): boolean => {
  return useOnboardingStore((state) => 
    !state.cameraPaused && !state.reducedMotion && !state.animationSkipped
  );
};

/**
 * Get particle count for current quality tier
 */
export const useParticleCount = (baseCounts: Record<QualityTier, number>): number => {
  return useOnboardingStore((state) => baseCounts[state.qualityTier]);
};

/**
 * Check if postprocessing effects should be enabled
 */
export const useShouldUsePostProcessing = (): boolean => {
  return useOnboardingStore((state) => 
    state.qualityTier !== 'low' && !state.reducedMotion
  );
};
