import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SceneNumber } from '@/types';
import { useOnboardingStore } from '@/stores/onboardingStore';

// Register ScrollTrigger plugin
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

/**
 * Type definition for progress change callback
 */
type ProgressCallback = (progress: number) => void;

/**
 * Type definition for unsubscribe function
 */
type UnsubscribeFn = () => void;

/**
 * Scene boundaries defining progress ranges for each scene
 * Scene 1: [0.00, 0.17]
 * Scene 2: [0.17, 0.33]
 * Scene 3: [0.33, 0.50]
 * Scene 4: [0.50, 0.67]
 * Scene 5: [0.67, 0.83]
 * Scene 6: [0.83, 1.00]
 * Scene 7-8: [1.00, 1.00] (Scene 7 and 8 are at the end)
 */
const SCENE_BOUNDARIES = [0, 0.17, 0.33, 0.5, 0.67, 0.83, 1.0] as const;

/**
 * ScrollController
 * 
 * Manages scroll-to-progress mapping for the cinematic onboarding experience.
 * Uses GSAP ScrollTrigger to provide smooth, 1:1 scroll-to-progress synchronization
 * with interpolated settling time when scrolling stops.
 * 
 * Features:
 * - Scroll position normalized to [0, 1] progress range
 * - Smooth interpolation with 200ms settling time on scroll stop
 * - Progress clamping to prevent over-scroll
 * - Scene boundary detection
 * - Event subscription pattern for progress changes
 * 
 * Requirements: 2.1, 2.2, 2.4, 2.6
 */
export class ScrollController {
  private _progress: number = 0;
  private _targetProgress: number = 0;
  private scrollTrigger: ScrollTrigger | null = null;
  private callbacks: Set<ProgressCallback> = new Set();
  private animationFrame: number | null = null;
  private interpolationTween: gsap.core.Tween | null = null;
  private isInitialized: boolean = false;

  /**
   * Current scroll progress normalized to [0, 1]
   */
  get progress(): number {
    return this._progress;
  }

  /**
   * Initialize the ScrollController with GSAP ScrollTrigger
   * 
   * Sets up a scroll-triggered animation that maps the entire page scroll
   * to a progress value between 0 and 1. The scroll trigger is pinned to
   * prevent page scrolling beyond the experience.
   * 
   * @param scrollContainer - The container element to track scroll on (default: document.body)
   */
  initialize(scrollContainer?: HTMLElement): void {
    if (typeof window === 'undefined') {
      console.warn('ScrollController: Cannot initialize on server side');
      return;
    }

    if (this.isInitialized) {
      console.warn('ScrollController: Already initialized');
      return;
    }


    this.scrollTrigger = ScrollTrigger.create({
      trigger: scrollContainer || document.body,
      start: 'top top',
      end: 'bottom bottom',
      scrub: true, // 1:1 scroll-to-progress mapping
      pin: false,
      onUpdate: (self) => {
        // Get raw progress from ScrollTrigger (already 0-1)
        const rawProgress = self.progress;
        
        // Set target progress (will be clamped)
        this._targetProgress = this.clampProgress(rawProgress);
        
        // Start smooth interpolation to target
        this.smoothInterpolate();
      },
    });

    this.isInitialized = true;
  }

  /**
   * Clamp progress value to [0, 1] range
   * Requirement: 2.6
   * 
   * @param value - Raw progress value
   * @returns Clamped progress value
   */
  private clampProgress(value: number): number {
    return Math.max(0, Math.min(1, value));
  }

  /**
   * Smooth interpolation to target progress with 200ms settling time
   * Requirement: 2.2, 2.7
   * 
   * Uses GSAP to animate from current progress to target progress
   * with a 200ms duration for smooth settling when scroll stops.
   */
  private smoothInterpolate(): void {
    // Kill existing interpolation tween if any
    if (this.interpolationTween) {
      this.interpolationTween.kill();
    }

    // Create new interpolation tween with 200ms duration
    this.interpolationTween = gsap.to(this, {
      _progress: this._targetProgress,
      duration: 0.2, // 200ms settling time
      ease: 'power2.out',
      onUpdate: () => {
        // Sync with onboarding store
        useOnboardingStore.getState().setScrollProgress(this._progress);
        // Notify all subscribers of progress change
        this.notifyProgressChange(this._progress);
      },
    });
  }

  /**
   * Notify all subscribed callbacks of progress change
   * 
   * @param progress - Current progress value
   */
  private notifyProgressChange(progress: number): void {
    this.callbacks.forEach((callback) => {
      try {
        callback(progress);
      } catch (error) {
        console.error('ScrollController: Error in progress callback', error);
      }
    });
  }

  /**
   * Subscribe to scroll progress changes
   * Requirement: Event subscription pattern
   * 
   * @param callback - Function to call when progress changes
   * @returns Unsubscribe function
   */
  onProgressChange(callback: ProgressCallback): UnsubscribeFn {
    this.callbacks.add(callback);
    
    // Immediately call with current progress
    callback(this._progress);
    
    // Return unsubscribe function
    return () => {
      this.callbacks.delete(callback);
    };
  }

  /**
   * Manually set scroll progress
   * Requirement: 2.1, 2.6
   * 
   * Useful for programmatic navigation (e.g., keyboard shortcuts, skip button)
   * 
   * @param progress - Target progress value (will be clamped to [0, 1])
   */
  setProgress(progress: number): void {
    const clampedProgress = this.clampProgress(progress);
    this._targetProgress = clampedProgress;
    this._progress = clampedProgress;
    
    // Update ScrollTrigger position to match
    if (this.scrollTrigger) {
      this.scrollTrigger.scroll(
        this.scrollTrigger.start + 
        (this.scrollTrigger.end - this.scrollTrigger.start) * clampedProgress
      );
    }
    
    // Sync with onboarding store
    useOnboardingStore.getState().setScrollProgress(clampedProgress);
    // Notify subscribers immediately
    this.notifyProgressChange(clampedProgress);
  }

  /**
   * Get current scene number based on scroll progress
   * Requirement: 2.4
   * 
   * Maps progress to scene number using defined scene boundaries:
   * - Scene 1: [0.00, 0.17)
   * - Scene 2: [0.17, 0.33)
   * - Scene 3: [0.33, 0.50)
   * - Scene 4: [0.50, 0.67)
   * - Scene 5: [0.67, 0.83)
   * - Scene 6: [0.83, 1.00)
   * - Scene 7: [1.00, 1.00] (at exact 1.0)
   * - Scene 8: Reached after Scene 7 completion
   * 
   * @returns Current scene number (1-8)
   */
  getCurrentScene(): SceneNumber {
    const progress = this._progress;
    
    // Handle edge case: exactly at 1.0 is Scene 7 start
    if (progress >= 1.0) {
      return 7;
    }
    
    // Find the scene by checking which boundary range progress falls into
    for (let i = 0; i < SCENE_BOUNDARIES.length - 1; i++) {
      const start = SCENE_BOUNDARIES[i];
      const end = SCENE_BOUNDARIES[i + 1];
      
      if (progress >= start && progress < end) {
        return (i + 1) as SceneNumber;
      }
    }
    
    // Fallback (should never reach here if boundaries are correct)
    return 1;
  }

  /**
   * Get scene boundaries for a specific scene
   * 
   * @param sceneNumber - Scene number (1-8)
   * @returns Object with start and end progress values
   */
  getSceneBoundaries(sceneNumber: SceneNumber): { start: number; end: number } {
    const index = sceneNumber - 1;
    
    // Scenes 7-8 are special cases at the end
    if (sceneNumber >= 7) {
      return { start: 1.0, end: 1.0 };
    }
    
    return {
      start: SCENE_BOUNDARIES[index],
      end: SCENE_BOUNDARIES[index + 1],
    };
  }

  /**
   * Check if currently at a scene boundary (transition point)
   * 
   * @param threshold - Distance from boundary to consider "at boundary" (default: 0.01)
   * @returns True if within threshold of any scene boundary
   */
  isAtSceneBoundary(threshold: number = 0.01): boolean {
    return SCENE_BOUNDARIES.some((boundary) => 
      Math.abs(this._progress - boundary) < threshold
    );
  }

  /**
   * Get all scene boundaries
   * 
   * @returns Array of scene boundary progress values
   */
  getSceneBoundariesArray(): readonly number[] {
    return SCENE_BOUNDARIES;
  }

  /**
   * Clean up resources and unregister ScrollTrigger
   */
  destroy(): void {
    // Kill interpolation tween
    if (this.interpolationTween) {
      this.interpolationTween.kill();
      this.interpolationTween = null;
    }
    
    // Kill animation frame
    if (this.animationFrame !== null) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
    
    // Kill ScrollTrigger
    if (this.scrollTrigger) {
      this.scrollTrigger.kill();
      this.scrollTrigger = null;
    }
    
    // Clear all callbacks
    this.callbacks.clear();
    
    // Reset state
    this._progress = 0;
    this._targetProgress = 0;
    this.isInitialized = false;
  }
}

// Export singleton instance
let scrollControllerInstance: ScrollController | null = null;

/**
 * Get or create ScrollController singleton instance
 * 
 * @returns ScrollController instance
 */
export function getScrollController(): ScrollController {
  if (!scrollControllerInstance) {
    scrollControllerInstance = new ScrollController();
    if (typeof window !== 'undefined') {
      (window as any).scrollController = scrollControllerInstance;
    }
  }
  return scrollControllerInstance;
}

/**
 * Reset ScrollController singleton (useful for testing)
 */
export function resetScrollController(): void {
  if (scrollControllerInstance) {
    scrollControllerInstance.destroy();
    scrollControllerInstance = null;
  }
}
