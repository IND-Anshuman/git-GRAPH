// Task 1.12: Performance Monitor - FPS tracking and auto-tuning quality tiers

import { QualityTier } from "@/types";
import { useOnboardingStore } from "@/stores/onboardingStore";

type QualityCallback = (tier: QualityTier) => void;

/**
 * PerformanceMonitor singleton class tracks rendering frame rates and auto-tunes
 * the rendering quality tier to maintain a targets FPS of 60.
 */
export class PerformanceMonitor {
  private static instance: PerformanceMonitor | null = null;
  
  private active: boolean = false;
  private lastTime: number = 0;
  private framesCount: number = 0;
  private animationFrameId: number | null = null;
  private fpsSamples: number[] = [];
  private consecutiveLowCount: number = 0;
  private stableHighStartTime: number | null = null;
  private callbacks: Set<QualityCallback> = new Set();

  private constructor() {}

  /**
   * Returns the singleton instance of PerformanceMonitor.
   */
  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  /**
   * Starts tracking FPS and auto-tuning.
   */
  start(): void {
    if (this.active || typeof window === "undefined") return;
    this.active = true;
    this.lastTime = performance.now();
    this.framesCount = 0;
    this.fpsSamples = [];
    this.consecutiveLowCount = 0;
    this.stableHighStartTime = null;
    this.tick();
  }

  /**
   * Stops tracking FPS.
   */
  stop(): void {
    this.active = false;
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  /**
   * Registers a callback for quality tier updates.
   * @param callback Callback function.
   * @returns Unsubscribe function.
   */
  onQualityChange(callback: QualityCallback): () => void {
    this.callbacks.add(callback);
    return () => {
      this.callbacks.delete(callback);
    };
  }

  /**
   * Programmatically overrides the quality tier.
   */
  setQualityTier(tier: QualityTier): void {
    useOnboardingStore.getState().setQualityTier(tier);
    this.notifyQualityChange(tier);
    // Reset tuning state when manually overridden
    this.consecutiveLowCount = 0;
    this.stableHighStartTime = null;
  }

  private tick = (): void => {
    if (!this.active) return;

    this.framesCount++;
    const now = performance.now();
    const elapsed = now - this.lastTime;

    if (elapsed >= 1000) {
      const fps = (this.framesCount * 1000) / elapsed;
      this.framesCount = 0;
      this.lastTime = now;

      this.processFPSSample(fps);
    }

    this.animationFrameId = requestAnimationFrame(this.tick);
  };

  private processFPSSample(fps: number): void {
    // Keep a sliding window of 3 samples
    this.fpsSamples.push(fps);
    if (this.fpsSamples.length > 3) {
      this.fpsSamples.shift();
    }

    // Calculate averaged FPS over samples
    const sum = this.fpsSamples.reduce((a, b) => a + b, 0);
    const avgFps = sum / this.fpsSamples.length;

    const store = useOnboardingStore.getState();
    const currentTier = store.qualityTier;

    // 1. Check for auto-downgrade
    let threshold = 60;
    if (currentTier === QualityTier.ULTRA) threshold = 60;
    else if (currentTier === QualityTier.HIGH) threshold = 50;
    else if (currentTier === QualityTier.MEDIUM) threshold = 30;
    else if (currentTier === QualityTier.LOW) threshold = 0;

    if (avgFps < threshold && currentTier !== QualityTier.LOW) {
      this.consecutiveLowCount++;
      this.stableHighStartTime = null; // Reset stable high timer

      if (this.consecutiveLowCount >= 3) {
        // Trigger downgrade
        let newTier: QualityTier = currentTier;
        if (currentTier === QualityTier.ULTRA) newTier = QualityTier.HIGH;
        else if (currentTier === QualityTier.HIGH) newTier = QualityTier.MEDIUM;
        else if (currentTier === QualityTier.MEDIUM) newTier = QualityTier.LOW;

        this.setQualityTier(newTier);
        console.warn(`[PerformanceMonitor] Downgraded quality to: ${newTier} (avg FPS: ${avgFps.toFixed(1)})`);
      }
    } else {
      this.consecutiveLowCount = 0; // Reset low count if FPS is above current threshold
    }

    // 2. Check for auto-upgrade (stable > 60 FPS for 10s)
    if (avgFps >= 60 && currentTier !== QualityTier.ULTRA) {
      const now = performance.now();
      if (this.stableHighStartTime === null) {
        this.stableHighStartTime = now;
      } else if (now - this.stableHighStartTime >= 10000) {
        // Trigger upgrade
        let newTier: QualityTier = currentTier;
        if (currentTier === QualityTier.LOW) newTier = QualityTier.MEDIUM;
        else if (currentTier === QualityTier.MEDIUM) newTier = QualityTier.HIGH;
        else if (currentTier === QualityTier.HIGH) newTier = QualityTier.ULTRA;

        this.setQualityTier(newTier);
        console.info(`[PerformanceMonitor] Upgraded quality to: ${newTier} (stable >60 FPS for 10s)`);
      }
    } else {
      this.stableHighStartTime = null; // Reset if FPS dips below 60
    }
  }

  private notifyQualityChange(tier: QualityTier): void {
    this.callbacks.forEach((callback) => {
      try {
        callback(tier);
      } catch (err) {
        console.error("[PerformanceMonitor] Error in quality change callback", err);
      }
    });
  }

  public destroy(): void {
    this.stop();
    this.callbacks.clear();
    this.fpsSamples = [];
  }
}
