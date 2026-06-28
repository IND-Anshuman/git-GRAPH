"use client";

import { useRef, useEffect, useState } from "react";
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

  const planetsRef = useRef<THREE.Mesh[]>([]);
  const glowMeshesRef = useRef<THREE.Mesh[]>([]);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);

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

  // Lazy Initialization: Only create planets when scene becomes active for the first time
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
    }
  }, [active, initialized]);

  // Convert health metric (0-1) to healthy (green), warning (yellow), or critical (red)
  const getHealthColor = (health: number): THREE.Color => {
    if (health >= 0.8) {
      return new THREE.Color("#4CAF50"); // healthy green
    } else if (health >= 0.6) {
      return new THREE.Color("#FFEB3B"); // warning yellow
    } else {
      return new THREE.Color("#F44336"); // critical red
    }
  };

  // Create capability planets and atmospheric glows
  const createPlanets = () => {
    if (!groupRef.current || !config.planets) return;

    // Dispose old planets
    planetsRef.current.forEach((mesh) => {
      if (groupRef.current) groupRef.current.remove(mesh);
      mesh.geometry.dispose();
      const mat = mesh.material;
      if (Array.isArray(mat)) {
        mat.forEach((m) => m.dispose());
      } else {
        (mat as THREE.Material).dispose();
      }
    });
    planetsRef.current = [];

    glowMeshesRef.current.forEach((mesh) => {
      if (groupRef.current) groupRef.current.remove(mesh);
      mesh.geometry.dispose();
      (mesh.material as THREE.Material).dispose();
    });
    glowMeshesRef.current = [];

    config.planets.forEach((planetData) => {
      const positionVec = new THREE.Vector3(...planetData.position);
      const sizeVal = planetData.size;

      // 1. Create Core Planet Mesh
      const geometry = new THREE.SphereGeometry(sizeVal, 32, 32);
      const healthColor = getHealthColor(planetData.health);

      const material = new THREE.MeshStandardMaterial({
        color: healthColor,
        emissive: healthColor,
        emissiveIntensity: 0.3,
        metalness: 0.4,
        roughness: 0.6,
      });

      const planetMesh = new THREE.Mesh(geometry, material);
      planetMesh.position.copy(positionVec);
      planetMesh.userData = planetData;
      
      groupRef.current?.add(planetMesh);
      planetsRef.current.push(planetMesh);

      // 2. Create Atmospheric Fresnel Glow Mesh
      // The atmosphere mesh is 20% larger than the planet core
      const glowGeometry = new THREE.SphereGeometry(sizeVal * 1.2, 32, 32);

      const glowMaterial = new THREE.ShaderMaterial({
        uniforms: {
          c: { value: 0.4 },
          p: { value: 3.5 },
          glowColor: { value: new THREE.Color(planetData.color) },
        },
        vertexShader: `
          varying vec3 vNormal;
          varying vec3 vViewPosition;
          void main() {
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
            vNormal = normalize(normalMatrix * normal);
            vViewPosition = -mvPosition.xyz;
            gl_Position = projectionMatrix * mvPosition;
          }
        `,
        fragmentShader: `
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
        `,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending,
        transparent: true,
        depthWrite: false,
      });

      const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
      glowMesh.position.copy(positionVec);

      groupRef.current?.add(glowMesh);
      glowMeshesRef.current.push(glowMesh);
    });
  };

  useEffect(() => {
    if (!initialized) return;

    createPlanets();

    return () => {
      planetsRef.current.forEach((mesh) => {
        if (groupRef.current) groupRef.current.remove(mesh);
        mesh.geometry.dispose();
        const mat = mesh.material;
        if (Array.isArray(mat)) {
          mat.forEach((m) => m.dispose());
        } else {
          (mat as THREE.Material).dispose();
        }
      });

      glowMeshesRef.current.forEach((mesh) => {
        if (groupRef.current) groupRef.current.remove(mesh);
        mesh.geometry.dispose();
        (mesh.material as THREE.Material).dispose();
      });
    };
  }, [initialized, config]);

  // Adjust geometry details or display visibility based on Quality Tier changes
  useEffect(() => {
    if (initialized) {
      // Re-create geometry with segments adjusted by quality if needed,
      // or filter glow meshes dynamically. For spheres, 32 segments is optimal,
      // but on low quality we can skip rendering the glowing halos completely.
      glowMeshesRef.current.forEach((glowMesh) => {
        glowMesh.visible = (qualityTier !== "low");
      });
    }
  }, [qualityTier, initialized]);

  // Framerate updates: Individual Y-axis rotations and atmospheric glow pulses
  useFrame((state, delta) => {
    if (!active) return;

    const time = state.clock.getElapsedTime();

    // Rotate core planets at slightly variable speeds
    planetsRef.current.forEach((mesh, idx) => {
      if (shouldAnimate) {
        mesh.rotation.y += delta * 0.08 * (1.0 + idx * 0.15);
      }
    });

    // Update atmospheric glow intensities ( Fresnel factor pulses over uTime )
    glowMeshesRef.current.forEach((glowMesh, idx) => {
      if (shouldAnimate) {
        glowMesh.rotation.y += delta * 0.08 * (1.0 + idx * 0.15);
      }

      const planetData = config.planets?.[idx];
      if (planetData && glowMesh.material instanceof THREE.ShaderMaterial) {
        // Modulate rim glow strength 'c' dynamically
        const activityPulse = 0.4 + Math.sin(time * 2.5 + idx) * 0.18;
        glowMesh.material.uniforms.c.value = activityPulse * planetData.importance;
      }
    });
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
