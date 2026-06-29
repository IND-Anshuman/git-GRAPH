"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { SceneConfig } from "@/types";
import * as THREE from "three";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { SelectionHighlight } from "../SelectionHighlight";

interface PlanetSceneProps {
  active: boolean;
  config: SceneConfig;
}

export function PlanetScene({ active, config }: PlanetSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [initialized, setInitialized] = useState(false);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);

  // Lazy Initialization: Only start rendering when scene becomes active
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
    }
  }, [active, initialized]);

  // Register interactive planets with InteractionHandler
  useEffect(() => {
    if (active && config.planets) {
      const handler = InteractionHandler.getInstance();
      config.planets.forEach((p) => {
        handler.registerObject(p.id, p.position, p.size, {
          type: "Capability Planet",
          title: p.name,
          description: `A capability planet composed of ${p.entityCount} components. Systems health is currently at ${(p.health * 100).toFixed(0)}%.`,
          details: {
            "Lines of Code": p.linesOfCode,
            "System Health": `${(p.health * 100).toFixed(0)}%`,
            "Importance Rank": p.importance
          }
        });
      });

      return () => {
        config.planets?.forEach((p) => {
          handler.unregisterObject(p.id);
        });
      };
    }
  }, [active, config.planets]);

  if (!active) return null;

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

      {/* Render Capability Planets (JSX declarative elements) */}
      {initialized && config.planets?.map((planet, idx) => (
        <PlanetElement
          key={planet.id}
          idx={idx}
          planetData={planet}
          shouldAnimate={shouldAnimate}
          qualityTier={qualityTier}
        />
      ))}

      {/* Selection Highlights */}
      {config.planets?.map((planet) => (
        <SelectionHighlight
          key={`highlight-${planet.id}`}
          position={planet.position}
          radius={planet.size}
          hovered={hoveredObjectId === planet.id || focusedObjectId === planet.id}
          selected={expandedCardId === planet.id}
          color={planet.color}
        />
      ))}
    </group>
  );
}

interface PlanetElementProps {
  idx: number;
  planetData: any;
  shouldAnimate: boolean;
  qualityTier: string;
}

/**
 * Modular component for a single capability planet and its atmospheric Fresnel glow halo.
 */
function PlanetElement({ idx, planetData, shouldAnimate, qualityTier }: PlanetElementProps) {
  const planetMeshRef = useRef<THREE.Mesh>(null);
  const glowMeshRef = useRef<THREE.Mesh>(null);

  // Convert health metric (0-1) to healthy (green), warning (yellow), or critical (red)
  const healthColor = useMemo(() => {
    const health = planetData.health;
    if (health >= 0.8) {
      return new THREE.Color("#4CAF50"); // healthy green
    } else if (health >= 0.6) {
      return new THREE.Color("#FFEB3B"); // warning yellow
    } else {
      return new THREE.Color("#F44336"); // critical red
    }
  }, [planetData.health]);

  const glowUniforms = useMemo(() => {
    return {
      c: { value: 0.4 },
      p: { value: 3.5 },
      glowColor: { value: new THREE.Color(planetData.color) }
    };
  }, [planetData.color]);

  useFrame((state, delta) => {
    if (!shouldAnimate) return;

    const time = state.clock.getElapsedTime();
    const rotateSpeed = delta * 0.08 * (1.0 + idx * 0.15);

    if (planetMeshRef.current) {
      planetMeshRef.current.rotation.y += rotateSpeed;
    }

    if (glowMeshRef.current) {
      glowMeshRef.current.rotation.y += rotateSpeed;

      if (glowMeshRef.current.material instanceof THREE.ShaderMaterial) {
        // Modulate rim glow strength 'c' dynamically
        const activityPulse = 0.4 + Math.sin(time * 2.5 + idx) * 0.18;
        glowMeshRef.current.material.uniforms.c.value = activityPulse * planetData.importance;
      }
    }
  });

  return (
    <group position={planetData.position}>
      {/* 1. Core Planet Mesh */}
      <mesh ref={planetMeshRef} userData={planetData}>
        <sphereGeometry args={[planetData.size, 32, 32]} />
        <meshStandardMaterial
          color={healthColor}
          emissive={healthColor}
          emissiveIntensity={0.3}
          metalness={0.4}
          roughness={0.6}
        />
      </mesh>

      {/* 2. Atmospheric Fresnel Glow Mesh (bypassed on low quality tier) */}
      {qualityTier !== "low" && (
        <mesh ref={glowMeshRef}>
          <sphereGeometry args={[planetData.size * 1.2, 32, 32]} />
          <shaderMaterial
            uniforms={glowUniforms}
            vertexShader={`
              varying vec3 vNormal;
              varying vec3 vViewPosition;
              void main() {
                vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                vNormal = normalize(normalMatrix * normal);
                vViewPosition = -mvPosition.xyz;
                gl_Position = projectionMatrix * mvPosition;
              }
            `}
            fragmentShader={`
              uniform vec3 glowColor;
              uniform float c;
              uniform float p;
              varying vec3 vNormal;
              varying vec3 vViewPosition;
              void main() {
                vec3 normalVec = normalize(vNormal);
                vec3 viewVec = normalize(vViewPosition);
                float dotProd = max(0.0, dot(normalVec, viewVec));
                float intensity = pow(1.0 - dotProd, p);
                gl_FragColor = vec4(glowColor, c * intensity);
              }
            `}
            side={THREE.BackSide}
            blending={THREE.AdditiveBlending}
            transparent
            depthWrite={false}
          />
        </mesh>
      )}
    </group>
  );
}
