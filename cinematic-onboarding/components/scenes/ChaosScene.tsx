"use client";

import { useRef, useEffect, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { ParticleSystemEngine } from "@/lib/ParticleSystemEngine";
import { ParticleAnimator } from "@/lib/ParticleAnimator";
import { SceneConfig } from "@/types";
import * as THREE from "three";

interface ChaosSceneProps {
  active: boolean;
  config: SceneConfig;
}

export function ChaosScene({ active, config }: ChaosSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [initialized, setInitialized] = useState(false);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);

  // Lazy Initialization: Only create particles when scene becomes active for the first time
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
    }
  }, [active, initialized]);

  useEffect(() => {
    if (!initialized) return;

    const engine = ParticleSystemEngine.getInstance();
    const animator = ParticleAnimator.getInstance();

    // Create particles using our proper config-based API
    engine.createParticles("scene-1", config.particles);

    // Apply active quality level instantly
    engine.adjustQuality(qualityTier);

    // Start drift animation
    animator.play("scene-1", {
      type: "drift",
      loop: true,
      params: {
        turbulence: config.particles.behavior.drift?.turbulence ?? 2.0,
        windDirection: new THREE.Vector3(0.1, 0.05, 0.1),
      },
    });

    // Cleanup particles and animator states on unmount
    return () => {
      animator.stop("scene-1");
      engine.destroyParticles("scene-1");
    };
  }, [initialized, config, qualityTier]);

  // Pause / Resume animation based on the camera animation state hook
  useEffect(() => {
    if (!initialized) return;
    const animator = ParticleAnimator.getInstance();
    if (shouldAnimate) {
      animator.resume("scene-1");
    } else {
      animator.pause("scene-1");
    }
  }, [shouldAnimate, initialized]);

  // Spin the entire logarithmic galaxy slowly on the Z-axis (normal axis to X-Y disk plane)
  useFrame((state) => {
    if (active && groupRef.current && shouldAnimate) {
      groupRef.current.rotation.z = state.clock.getElapsedTime() * 0.035;
    }
  });

  return (
    <group ref={groupRef} visible={active}>
      {/* Scene 1 Lighting */}
      <ambientLight 
        color={config.lighting.ambient.color} 
        intensity={config.lighting.ambient.intensity} 
      />
      {config.lighting.point?.map((light, i) => (
        <pointLight
          key={`point-${i}`}
          color={light.color}
          intensity={light.intensity}
          position={light.position}
          distance={light.distance}
        />
      ))}
    </group>
  );
}
