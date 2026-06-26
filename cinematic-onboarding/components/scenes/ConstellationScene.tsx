"use client";

import { useRef, useEffect, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { ParticleSystemEngine } from "@/lib/ParticleSystemEngine";
import { ParticleAnimator } from "@/lib/ParticleAnimator";
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
  const labelsRef = useRef<THREE.Sprite[]>([]);

  // Lazy Initialization: Only create particles when scene becomes active for the first time
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
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

  // Create floating canvas billboard sprite labels above constellation centers
  const createConstellationLabels = () => {
    if (!groupRef.current || !config.constellations) return;

    // Dispose old labels
    labelsRef.current.forEach((label) => {
      if (groupRef.current) groupRef.current.remove(label);
      label.material.dispose();
      label.material.map?.dispose();
    });
    labelsRef.current = [];

    const labels: THREE.Sprite[] = [];

    config.constellations.forEach((constellation) => {
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 128;
      const ctx = canvas.getContext("2d");

      if (ctx) {
        ctx.clearRect(0, 0, 512, 128);

        // Add soft typography glow
        ctx.shadowColor = constellation.color;
        ctx.shadowBlur = 12;

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 42px Arial, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(constellation.name.toUpperCase(), 256, 64);

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMat = new THREE.SpriteMaterial({
          map: texture,
          transparent: true,
          opacity: 0,
          depthWrite: false,
        });

        const sprite = new THREE.Sprite(spriteMat);
        const center = constellation.center;
        
        // Position labels float 20 units above constellation center
        sprite.position.set(center[0], center[1] + 20, center[2]);
        sprite.scale.set(24, 6, 1);

        groupRef.current?.add(sprite);
        labels.push(sprite);

        // Fade in labels after clustering completes
        gsap.to(spriteMat, {
          opacity: 0.9,
          duration: 1.5,
          delay: 1.5,
        });
      }
    });

    labelsRef.current = labels;
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
    createConstellationLabels();

    return () => {
      animator.stop("scene-3");
      engine.destroyParticles("scene-3");

      if (connectionLinesRef.current && groupRef.current) {
        groupRef.current.remove(connectionLinesRef.current);
        connectionLinesRef.current.geometry.dispose();
        (connectionLinesRef.current.material as THREE.Material).dispose();
      }

      labelsRef.current.forEach((label) => {
        if (groupRef.current) groupRef.current.remove(label);
        label.material.dispose();
        label.material.map?.dispose();
      });
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
    </group>
  );
}
