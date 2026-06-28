"use client";

import { useRef, useEffect, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { ParticleSystemEngine } from "@/lib/ParticleSystemEngine";
import { ParticleAnimator } from "@/lib/ParticleAnimator";
import { Text } from "@react-three/drei";
import { SceneConfig } from "@/types";
import * as THREE from "three";
import gsap from "gsap";

interface ConstellationSceneProps {
  active: boolean;
  config: SceneConfig;
}

export function ConstellationScene({ active, config }: ConstellationSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [initialized, setInitialized] = useState(false);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);

  const connectionLinesRef = useRef<THREE.LineSegments | null>(null);
  const [labelOpacity, setLabelOpacity] = useState(0);

  // Lazy Initialization: Only create particles when scene becomes active for the first time
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
    }
  }, [active, initialized]);

  // Label fade-in animation timer synced with clustering duration
  useEffect(() => {
    if (active && initialized) {
      const animObj = { val: 0 };
      const tween = gsap.to(animObj, {
        val: 0.9,
        duration: 1.5,
        delay: 1.5,
        onUpdate: () => setLabelOpacity(animObj.val)
      });
      return () => {
        tween.kill();
        setLabelOpacity(0);
      };
    }
  }, [active, initialized]);

  // Create connection lines between particles in the same cluster
  const createConnectionLines = (group: any, centers: THREE.Vector3[]) => {
    if (!groupRef.current) return;

    // Dispose previous connection lines if any
    if (connectionLinesRef.current) {
      groupRef.current.remove(connectionLinesRef.current);
      connectionLinesRef.current.geometry.dispose();
      (connectionLinesRef.current.material as THREE.Material).dispose();
      connectionLinesRef.current = null;
    }

    const geom = group.lodMeshes.sphere.geometry;
    const initialPosAttr = geom.getAttribute("aInitialPosition") as THREE.BufferAttribute;
    const clusterIdxAttr = geom.getAttribute("aClusterIndex") as THREE.BufferAttribute;

    if (!initialPosAttr || !clusterIdxAttr) return;

    const totalCount = group.count;
    // Sample a subset of particles (target ~1000) to keep complexity O(N_sample^2) low
    const sampleRate = Math.max(1, Math.floor(totalCount / 1000));
    
    // Group sampled coordinates by their target cluster center
    const clusterParticles: THREE.Vector3[][] = Array.from({ length: 10 }, () => []);

    for (let i = 0; i < totalCount; i += sampleRate) {
      const x = initialPosAttr.getX(i);
      const y = initialPosAttr.getY(i);
      const z = initialPosAttr.getZ(i);
      const clusterIdx = Math.floor(clusterIdxAttr.getX(i));

      if (clusterIdx >= 0 && clusterIdx < 10) {
        const center = centers[clusterIdx];
        const initialPos = new THREE.Vector3(x, y, z);
        
        // Compute final clustered target position
        const clusterRadius = config.particles.behavior.cluster?.clusterRadius ?? 15.0;
        const clusteredPos = new THREE.Vector3()
          .copy(initialPos)
          .normalize()
          .multiplyScalar(Math.random() * clusterRadius * 0.4)
          .add(center);

        clusterParticles[clusterIdx].push(clusteredPos);
      }
    }

    // Connect close neighbors within the same cluster
    const linePositions: number[] = [];
    const connectionThreshold = (config.particles.behavior.cluster?.clusterRadius ?? 15.0) * 0.6;

    clusterParticles.forEach((particlesInCluster) => {
      const len = particlesInCluster.length;
      for (let i = 0; i < len; i++) {
        for (let j = i + 1; j < len; j++) {
          const dist = particlesInCluster[i].distanceTo(particlesInCluster[j]);
          if (dist < connectionThreshold) {
            linePositions.push(particlesInCluster[i].x, particlesInCluster[i].y, particlesInCluster[i].z);
            linePositions.push(particlesInCluster[j].x, particlesInCluster[j].y, particlesInCluster[j].z);
          }
        }
      }
    });

    const lineGeom = new THREE.BufferGeometry();
    lineGeom.setAttribute("position", new THREE.Float32BufferAttribute(linePositions, 3));

    const lineMat = new THREE.LineBasicMaterial({
      color: new THREE.Color("#4fc3f7"),
      transparent: true,
      opacity: 0, // starts hidden and fades in
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const lineSegments = new THREE.LineSegments(lineGeom, lineMat);
    groupRef.current.add(lineSegments);
    connectionLinesRef.current = lineSegments;

    // Fade in lines smoothly after particles start clustering
    gsap.to(lineMat, {
      opacity: 0.3,
      duration: 2.0,
      delay: 1.0,
      ease: "power1.inOut",
    });
  };

  useEffect(() => {
    if (!initialized) return;

    const engine = ParticleSystemEngine.getInstance();
    const animator = ParticleAnimator.getInstance();

    const centers = config.particles.behavior.cluster!.centers.map(c => new THREE.Vector3(...c));
    // Pad array to exactly 10 elements to match WebGL GLSL shader layout size limits
    const paddedCenters = [...centers];
    while (paddedCenters.length < 10) {
      paddedCenters.push(centers[paddedCenters.length % centers.length].clone());
    }

    // Create particles group
    const group = engine.createParticles("scene-3", config.particles);

    // Apply active quality level instantly
    engine.adjustQuality(qualityTier);

    // Play cluster animation
    animator.play("scene-3", {
      type: "cluster",
      loop: false,
      duration: 2.0,
      params: {
        clusterCenters: paddedCenters,
        attractionStrength: config.particles.behavior.cluster?.attractionStrength ?? 2.5,
        clusterRadius: config.particles.behavior.cluster?.clusterRadius ?? 15.0,
      },
    });

    // Create visual overlays
    createConnectionLines(group, paddedCenters);

    return () => {
      animator.stop("scene-3");
      engine.destroyParticles("scene-3");

      if (connectionLinesRef.current && groupRef.current) {
        groupRef.current.remove(connectionLinesRef.current);
        connectionLinesRef.current.geometry.dispose();
        (connectionLinesRef.current.material as THREE.Material).dispose();
      }
    };
  }, [initialized, config]);

  // Sync Quality Tier updates
  useEffect(() => {
    if (initialized) {
      const engine = ParticleSystemEngine.getInstance();
      const group = engine.getGroup("scene-3");
      if (group) {
        engine.adjustQuality(qualityTier);
        const centers = config.particles.behavior.cluster!.centers.map(c => new THREE.Vector3(...c));
        const paddedCenters = [...centers];
        while (paddedCenters.length < 10) {
          paddedCenters.push(centers[paddedCenters.length % centers.length].clone());
        }
        createConnectionLines(group, paddedCenters);
      }
    }
  }, [qualityTier, initialized]);

  // Pause / Resume animation based on camera rails active state
  useEffect(() => {
    if (!initialized) return;
    const animator = ParticleAnimator.getInstance();
    if (shouldAnimate) {
      animator.resume("scene-3");
    } else {
      animator.pause("scene-3");
    }
  }, [shouldAnimate, initialized]);

  // Framerate updates: Pulsing emissive glow (0.5Hz) and slow scene Y-spin
  useFrame((state, delta) => {
    if (!active) return;

    // Slowly rotate the entire constellation scene
    if (groupRef.current && shouldAnimate) {
      groupRef.current.rotation.y += delta * 0.08;
    }

    const engine = ParticleSystemEngine.getInstance();
    const group = engine.getGroup("scene-3");
    if (group) {
      // 0.5Hz sine pulse (period = 2 seconds)
      const time = state.clock.getElapsedTime();
      const pulse = 0.6 + Math.sin(time * Math.PI) * 0.3; // ranges 0.3 to 0.9

      group.material.opacity = pulse * (config.particles.material.opacity ?? 0.8);
      group.material.uniforms.uSize.value = pulse * (config.particles.geometry.size ?? 0.3);
    }
  });

  return (
    <group ref={groupRef} visible={active}>
      {/* Lighting */}
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

      {/* Vector-sharp Constellation Labels */}
      {active && config.constellations?.map((constellation) => {
        const center = constellation.center;
        return (
          <Text
            key={constellation.name}
            position={[center[0], center[1] + 20, center[2]]}
            fontSize={5.0}
            color="#ffffff"
            font="https://fonts.gstatic.com/s/outfit/v11/QGYxz_oLhx70648tMSsL.woff"
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.25}
            outlineColor={constellation.color}
            outlineOpacity={labelOpacity}
            fillOpacity={labelOpacity}
          >
            {constellation.name.toUpperCase()}
          </Text>
        );
      })}
    </group>
  );
}
