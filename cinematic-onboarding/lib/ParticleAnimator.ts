// Task 3.7: Particle Animation System - Orchestrates shader-based animations with play/pause/reset controls

import { ParticleSystemEngine } from "./ParticleSystemEngine";

export interface ParticleAnimation {
  type: "static" | "drift" | "orbit" | "explosion" | "cluster" | "network";
  duration?: number;
  loop?: boolean;
  params?: Record<string, any>;
}

interface AnimationInstance {
  groupId: string;
  animation: ParticleAnimation;
  elapsedTime: number;
  playing: boolean;
}

/**
 * ParticleAnimator singleton class updates uniform variables in custom particle shaders
 * over time. It supports play, pause, resume, and stop controls.
 */
export class ParticleAnimator {
  private static instance: ParticleAnimator | null = null;
  private activeAnimations: Map<string, AnimationInstance> = new Map();

  private constructor() {}

  /**
   * Returns the singleton instance of ParticleAnimator.
   */
  static getInstance(): ParticleAnimator {
    if (!ParticleAnimator.instance) {
      ParticleAnimator.instance = new ParticleAnimator();
    }
    return ParticleAnimator.instance;
  }

  /**
   * Plays a GPU-based shader animation on a registered particle group.
   */
  play(groupId: string, animation: ParticleAnimation): void {
    const engine = ParticleSystemEngine.getInstance();
    const group = engine.getGroup(groupId);
    if (!group) {
      console.warn(`[ParticleAnimator] Cannot play animation: Group ${groupId} not found.`);
      return;
    }

    // Initialize/Update uniforms with params
    const material = group.material;
    const params = animation.params || {};

    Object.keys(params).forEach((key) => {
      // Map parameter 'turbulence' -> 'uTurbulence' etc.
      const uniformName = `u${key.charAt(0).toUpperCase()}${key.slice(1)}`;
      if (material.uniforms[uniformName]) {
        material.uniforms[uniformName].value = params[key];
      }
    });

    // Reset shader time
    if (material.uniforms.uTime) {
      material.uniforms.uTime.value = 0;
    }

    const instance: AnimationInstance = {
      groupId,
      animation,
      elapsedTime: 0,
      playing: true,
    };

    this.activeAnimations.set(groupId, instance);
    group.animationState = "playing";
  }

  /**
   * Pauses an active animation.
   */
  pause(groupId: string): void {
    const instance = this.activeAnimations.get(groupId);
    if (instance) {
      instance.playing = false;
      
      const engine = ParticleSystemEngine.getInstance();
      const group = engine.getGroup(groupId);
      if (group) group.animationState = "paused";
    }
  }

  /**
   * Resumes a paused animation.
   */
  resume(groupId: string): void {
    const instance = this.activeAnimations.get(groupId);
    if (instance) {
      instance.playing = true;
      
      const engine = ParticleSystemEngine.getInstance();
      const group = engine.getGroup(groupId);
      if (group) group.animationState = "playing";
    }
  }

  /**
   * Stops an active animation and resets the uniform clock.
   */
  stop(groupId: string): void {
    const instance = this.activeAnimations.get(groupId);
    if (instance) {
      this.activeAnimations.delete(groupId);
      
      const engine = ParticleSystemEngine.getInstance();
      const group = engine.getGroup(groupId);
      if (group) {
        group.animationState = "idle";
        if (group.material.uniforms.uTime) {
          group.material.uniforms.uTime.value = 0;
        }
      }
    }
  }

  /**
   * Updates uTime for all playing animations. Should be called inside the render loop.
   * @param deltaTime The elapsed frame time in seconds.
   */
  update(deltaTime: number): void {
    const engine = ParticleSystemEngine.getInstance();

    this.activeAnimations.forEach((instance, groupId) => {
      if (!instance.playing) return;

      instance.elapsedTime += deltaTime;

      // Check if duration has ended (non-looping animations)
      const duration = instance.animation.duration;
      if (duration !== undefined && instance.elapsedTime >= duration) {
        if (instance.animation.loop) {
          instance.elapsedTime = 0; // restart
        } else {
          this.stop(groupId);
          return;
        }
      }

      const group = engine.getGroup(groupId);
      if (group && group.material.uniforms.uTime) {
        // Sync uniform clock with elapsed animation time
        group.material.uniforms.uTime.value = instance.elapsedTime;
      }
    });
  }

  /**
   * Disposes the animator.
   */
  destroy(): void {
    this.activeAnimations.clear();
  }
}
