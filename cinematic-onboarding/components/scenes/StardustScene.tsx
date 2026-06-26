"use client";

import { useRef, useEffect, useState } from "react";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { ParticleSystemEngine } from "@/lib/ParticleSystemEngine";
import { ParticleAnimator } from "@/lib/ParticleAnimator";
import { SceneConfig } from "@/types";
import * as THREE from "three";

interface StardustSceneProps {
  active: boolean;
  config: SceneConfig;
}

export function StardustScene({ active, config }: StardustSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [initialized, setInitialized] = useState(false);
  const [explosionTriggered, setExplosionTriggered] = useState(false);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);

  // Lazy Initialization: Only create particles when scene becomes active for the first time
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
    }
  }, [active, initialized]);

  // Recolor particles based on entity type ratios and counts
  const applySemanticColors = (group: any) => {
    const entityTypes = config.particles.entityTypes;
    if (!entityTypes) return;

    const totalCount = group.count;
    const colors: THREE.Color[] = [];
    const types = Object.entries(entityTypes);
    let index = 0;

    types.forEach(([_, spec]: [string, any]) => {
      const count = Math.floor(totalCount * spec.ratio);
      const col = new THREE.Color(spec.color);
      for (let i = 0; i < count; i++) {
        if (index < totalCount) {
          colors.push(col);
          index++;
        }
      }
    });

    const defaultColor = new THREE.Color(config.particles.material.color ?? "#ffffff");
    while (colors.length < totalCount) {
      colors.push(defaultColor);
    }

    // Apply colors to all LOD meshes
    for (let i = 0; i < totalCount; i++) {
      group.lodMeshes.sphere.setColorAt(i, colors[i]);
      group.lodMeshes.quad.setColorAt(i, colors[i]);
      group.lodMeshes.point.setColorAt(i, colors[i]);
    }

    // Flag GPU attribute updates
    if (group.lodMeshes.sphere.instanceColor) {
      group.lodMeshes.sphere.instanceColor.needsUpdate = true;
    }
    if (group.lodMeshes.quad.instanceColor) {
      group.lodMeshes.quad.instanceColor.needsUpdate = true;
    }
    if (group.lodMeshes.point.instanceColor) {
      group.lodMeshes.point.instanceColor.needsUpdate = true;
    }
  };

  useEffect(() => {
    if (!initialized) return;

    const engine = ParticleSystemEngine.getInstance();
    const group = engine.createParticles("scene-2", config.particles);

    // Initial coloring
    applySemanticColors(group);

    return () => {
      const animator = ParticleAnimator.getInstance();
      animator.stop("scene-2");
      engine.destroyParticles("scene-2");
    };
  }, [initialized, config]);

  // Sync Quality Tier updates
  useEffect(() => {
    if (initialized) {
      const engine = ParticleSystemEngine.getInstance();
      const group = engine.getGroup("scene-2");
      if (group) {
        engine.adjustQuality(qualityTier);
        applySemanticColors(group);
      }
    }
  }, [qualityTier, initialized]);

  // Trigger explosion on scene activation
  useEffect(() => {
    if (!active) {
      setExplosionTriggered(false);
      return;
    }

    if (explosionTriggered || !initialized) return;

    const animator = ParticleAnimator.getInstance();

    // 1. Play physics-based explosion animation
    animator.play("scene-2", {
      type: "explosion",
      loop: false,
      duration: 3.0,
      params: {
        origin: new THREE.Vector3(0, 0, 0),
        force: config.particles.behavior.explosion?.force[0] ?? 5.0,
        gravity: new THREE.Vector3(...(config.particles.behavior.explosion?.gravity ?? [0, -0.5, 0])),
        damping: config.particles.behavior.explosion?.damping ?? 0.3,
      },
    });

    setExplosionTriggered(true);

    // 2. After 3 seconds, transition into a gentle floating drift
    const timer = setTimeout(() => {
      animator.play("scene-2", {
        type: "drift",
        loop: true,
        params: {
          turbulence: 1.0,
          windDirection: new THREE.Vector3(0.05, 0.02, 0.05),
        },
      });
    }, 3000);

    return () => {
      clearTimeout(timer);
    };
  }, [active, initialized, explosionTriggered, config]);

  // Pause / Resume animation based on camera rail state
  useEffect(() => {
    if (!initialized) return;
    const animator = ParticleAnimator.getInstance();
    if (shouldAnimate) {
      animator.resume("scene-2");
    } else {
      animator.pause("scene-2");
    }
  }, [shouldAnimate, initialized]);

  return (
    <group ref={groupRef} visible={active}>
      {/* Lighting */}
      <ambientLight 
        color={config.lighting.ambient.color} 
        intensity={config.lighting.ambient.intensity} 
      />
      {config.lighting.directional?.map((light, i) => (
        <directionalLight
          key={`dir-${i}`}
          color={light.color}
          intensity={light.intensity}
          position={new THREE.Vector3(...light.position)}
        />
      ))}
    </group>
  );
}
