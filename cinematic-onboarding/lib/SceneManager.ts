// Task 1.7: Scene Manager - Orchestrates scene lifecycle, lazy loading, and transition crossfades

import gsap from "gsap";
import { SceneConfig, SceneNumber, SceneStatus } from "@/types";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { parseSceneConfig } from "./configParser";
import { ParticleSystemEngine } from "./ParticleSystemEngine";
import { ParticleAnimator } from "./ParticleAnimator";

/**
 * SceneManager singleton class orchestrates loading, activation, deactivation,
 * and unloading of scenes based on the user's progress. It manages a 500ms
 * crossfade between scenes to ensure visual transitions are smooth.
 */
export class SceneManager {
  private static instance: SceneManager | null = null;
  private sceneConfigs: Map<SceneNumber, SceneConfig> = new Map();
  private sceneStatuses: Map<SceneNumber, SceneStatus> = new Map();
  private sceneOpacities: Map<SceneNumber, number> = new Map();
  private opacityTweens: Map<SceneNumber, gsap.core.Tween> = new Map();

  private constructor() {
    // Initialize all scene statuses to UNLOADED and opacities to 0
    for (let i = 1; i <= 8; i++) {
      const s = i as SceneNumber;
      this.sceneStatuses.set(s, SceneStatus.UNLOADED);
      this.sceneOpacities.set(s, 0);
    }
  }

  /**
   * Returns the singleton instance of the SceneManager.
   */
  static getInstance(): SceneManager {
    if (!SceneManager.instance) {
      SceneManager.instance = new SceneManager();
    }
    return SceneManager.instance;
  }

  /**
   * Resets the SceneManager singleton (mainly for testing).
   */
  static resetInstance(): void {
    if (SceneManager.instance) {
      SceneManager.instance.destroy();
      SceneManager.instance = null;
    }
  }

  /**
   * Evaluates scroll progress and coordinates lazy loading and unloading.
   * Loads current and next scene, unloads scenes > 2 away.
   * 
   * @param currentScene The active scene number.
   */
  async updateSceneLifecycle(currentScene: SceneNumber): Promise<void> {
    const scenesToLoad = new Set<SceneNumber>();
    scenesToLoad.add(currentScene);
    if (currentScene < 8) {
      scenesToLoad.add((currentScene + 1) as SceneNumber);
    }

    const scenesToUnload = new Set<SceneNumber>();
    for (let i = 1; i <= 8; i++) {
      const s = i as SceneNumber;
      if (Math.abs(s - currentScene) > 2) {
        scenesToUnload.add(s);
      }
    }

    // 1. Unload distant scenes
    for (const scene of scenesToUnload) {
      this.unloadScene(scene);
    }

    // 2. Load necessary scenes
    for (const scene of scenesToLoad) {
      const status = this.getSceneStatus(scene);
      if (status === SceneStatus.UNLOADED) {
        this.loadScene(scene).catch((err) => {
          console.error(`[SceneManager] Failed to load scene ${scene}:`, err);
        });
      }
    }

    // 3. Activate current scene
    this.activateScene(currentScene);
  }

  /**
   * Loads a scene's configuration and assets.
   */
  async loadScene(sceneNumber: SceneNumber): Promise<void> {
    const currentStatus = this.getSceneStatus(sceneNumber);
    if (currentStatus === SceneStatus.LOADING || currentStatus === SceneStatus.READY || currentStatus === SceneStatus.ACTIVE) {
      return;
    }

    this.setSceneStatus(sceneNumber, SceneStatus.LOADING);

    try {
      const response = await fetch(`/config/scenes/scene${sceneNumber}.json?t=${Date.now()}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch scene config: HTTP ${response.status}`);
      }

      const json = await response.text();
      const config = parseSceneConfig(json);
      this.sceneConfigs.set(sceneNumber, config);

      // Create particles for this scene if enabled (delegated for scenes 1-8)
      if (config.particles?.enabled && sceneNumber !== 1 && sceneNumber !== 2 && sceneNumber !== 3 && sceneNumber !== 4 && sceneNumber !== 5 && sceneNumber !== 6 && sceneNumber !== 7 && sceneNumber !== 8) {
        ParticleSystemEngine.getInstance().createParticles(`scene-${sceneNumber}`, config.particles);
      }

      this.setSceneStatus(sceneNumber, SceneStatus.READY);
    } catch (error) {
      this.setSceneStatus(sceneNumber, SceneStatus.UNLOADED);
      throw error;
    }
  }

  /**
   * Activates a scene and initiates a 500ms crossfade.
   */
  activateScene(sceneNumber: SceneNumber): void {
    const currentStatus = this.getSceneStatus(sceneNumber);
    if (currentStatus === SceneStatus.READY) {
      this.setSceneStatus(sceneNumber, SceneStatus.ACTIVE);
    }

    // Play particle animation if particles are active (delegated for scenes 1-8)
    const config = this.getSceneConfig(sceneNumber);
    if (config?.particles?.enabled && sceneNumber !== 1 && sceneNumber !== 2 && sceneNumber !== 3 && sceneNumber !== 4 && sceneNumber !== 5 && sceneNumber !== 6 && sceneNumber !== 7 && sceneNumber !== 8) {
      const animator = ParticleAnimator.getInstance();
      animator.play(`scene-${sceneNumber}`, {
        type: config.particles.behavior.animation,
        params: {
          turbulence: config.particles.behavior.drift?.turbulence ?? 1.5,
          speed: config.particles.behavior.orbit?.speed?.[0] ?? 0.5,
          radius: config.particles.behavior.orbit?.radius?.[0] ?? 10.0,
          force: config.particles.behavior.explosion?.force?.[0] ?? 2.0,
          damping: config.particles.behavior.explosion?.damping ?? 0.1,
          attractionStrength: config.particles.behavior.cluster?.attractionStrength ?? 0.5,
          flowSpeed: config.particles.behavior.network?.flowSpeed ?? 0.8,
        }
      });
    }

    // Trigger crossfade: active scene opacity animates to 1
    this.fadeScene(sceneNumber, 1.0);

    // Fade out all other scenes
    for (let i = 1; i <= 8; i++) {
      const s = i as SceneNumber;
      if (s !== sceneNumber) {
        this.fadeScene(s, 0.0);
      }
    }
  }

  /**
   * Deactivates and unloads a scene from memory.
   */
  unloadScene(sceneNumber: SceneNumber): void {
    const currentStatus = this.getSceneStatus(sceneNumber);
    if (currentStatus !== SceneStatus.UNLOADED) {
      this.sceneConfigs.delete(sceneNumber);
      this.setSceneStatus(sceneNumber, SceneStatus.UNLOADED);
      this.sceneOpacities.set(sceneNumber, 0);

      // Stop particle animation and dispose buffers (delegated for scenes 1-8)
      if (sceneNumber !== 1 && sceneNumber !== 2 && sceneNumber !== 3 && sceneNumber !== 4 && sceneNumber !== 5 && sceneNumber !== 6 && sceneNumber !== 7 && sceneNumber !== 8) {
        ParticleAnimator.getInstance().stop(`scene-${sceneNumber}`);
        ParticleSystemEngine.getInstance().destroyParticles(`scene-${sceneNumber}`);
      }

      const activeTween = this.opacityTweens.get(sceneNumber);
      if (activeTween) {
        activeTween.kill();
        this.opacityTweens.delete(sceneNumber);
      }
    }
  }

  /**
   * Gets the loading/render status of a scene.
   */
  getSceneStatus(sceneNumber: SceneNumber): SceneStatus {
    return this.sceneStatuses.get(sceneNumber) || SceneStatus.UNLOADED;
  }

  /**
   * Gets the configuration object of a loaded scene.
   */
  getSceneConfig(sceneNumber: SceneNumber): SceneConfig | undefined {
    return this.sceneConfigs.get(sceneNumber);
  }

  /**
   * Gets the current transition opacity of a scene [0, 1].
   */
  getSceneOpacity(sceneNumber: SceneNumber): number {
    return this.sceneOpacities.get(sceneNumber) ?? 0;
  }

  private setSceneStatus(sceneNumber: SceneNumber, status: SceneStatus): void {
    this.sceneStatuses.set(sceneNumber, status);
    // Sync with Zustand store
    useOnboardingStore.getState().setSceneStatus(sceneNumber, status);
  }

  private fadeScene(scene: SceneNumber, targetOpacity: number): void {
    const currentOpacity = this.sceneOpacities.get(scene) ?? 0;
    if (currentOpacity === targetOpacity) {
      return;
    }

    const activeTween = this.opacityTweens.get(scene);
    if (activeTween) {
      activeTween.kill();
    }

    const animObj = { opacity: currentOpacity };
    const tween = gsap.to(animObj, {
      opacity: targetOpacity,
      duration: 0.5, // 500ms crossfade
      ease: "power1.inOut",
      onUpdate: () => {
        this.sceneOpacities.set(scene, animObj.opacity);
      },
      onComplete: () => {
        this.opacityTweens.delete(scene);
      },
    });

    this.opacityTweens.set(scene, tween);
  }

  /**
   * Disposes the SceneManager and kills all active tweens.
   */
  destroy(): void {
    this.opacityTweens.forEach((tween) => tween.kill());
    this.opacityTweens.clear();
    this.sceneConfigs.clear();
    this.sceneStatuses.clear();
    this.sceneOpacities.clear();
  }
}
