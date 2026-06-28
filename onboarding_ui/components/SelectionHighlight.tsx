"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface SelectionHighlightProps {
  position: [number, number, number] | THREE.Vector3;
  radius: number;
  hovered: boolean;
  selected: boolean;
  color?: string; // Optional override color
}

/**
 * SelectionHighlight renders a glowing silhouette edge outline mesh
 * behind interactive sphere objects, performing 300ms fade transitions.
 */
export function SelectionHighlight({
  position,
  radius,
  hovered,
  selected,
  color,
}: SelectionHighlightProps) {
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const opacityRef = useRef(0.0);

  const posVec = useMemo(() => {
    return position instanceof THREE.Vector3 ? position : new THREE.Vector3(...position);
  }, [position]);

  // Determine target outline color
  const outlineColor = useMemo(() => {
    if (color) return new THREE.Color(color);
    if (selected) return new THREE.Color("#9C27B0"); // Deep Purple for Selected
    return new THREE.Color("#00E5FF"); // Cyan for Hovered
  }, [selected, color]);

  // Expanded scale factors
  const thickness = selected ? 1.35 : 1.2;

  // Custom vertex normal expansion + volumetric fresnel glow shader
  const shader = useMemo(() => {
    return {
      uniforms: {
        glowColor: { value: outlineColor },
        opacity: { value: 0.0 },
        thickness: { value: thickness },
        time: { value: 0.0 },
      },
      vertexShader: `
        uniform float thickness;
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        void main() {
          // Push vertices outwards along their normals to expand the outline mesh
          vec3 expandedPosition = position + normal * (thickness - 1.0);
          vec4 mvPosition = modelViewMatrix * vec4(expandedPosition, 1.0);
          vNormal = normalize(normalMatrix * normal);
          vViewPosition = -mvPosition.xyz;
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        uniform vec3 glowColor;
        uniform float opacity;
        uniform float time;
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        void main() {
          vec3 normalVec = normalize(vNormal);
          vec3 viewVec = normalize(vViewPosition);
          // Volumetric fresnel edge glow
          float dotProd = max(0.0, dot(normalVec, viewVec));
          float intensity = pow(1.0 - dotProd, 3.5);
          
          // Subtle pulse shimmer on selected items
          float pulse = 1.0;
          if (time > 0.0) {
            pulse = 0.85 + sin(time * 6.0) * 0.15;
          }
          
          gl_FragColor = vec4(glowColor, intensity * opacity * pulse);
        }
      `,
    };
  }, [outlineColor, thickness]);

  // 300ms fade transition loop (interpolating opacity ref inside useFrame)
  useFrame((state, delta) => {
    if (!materialRef.current) return;

    const targetOpacity = hovered || selected ? (selected ? 0.95 : 0.75) : 0.0;
    
    // Smooth lerp for 300ms transition time: approx 0.1 lerp factor at 60 FPS
    opacityRef.current = THREE.MathUtils.lerp(opacityRef.current, targetOpacity, delta * 12.0);
    materialRef.current.uniforms.opacity.value = opacityRef.current;

    if (selected) {
      materialRef.current.uniforms.time.value = state.clock.getElapsedTime();
    } else {
      materialRef.current.uniforms.time.value = 0.0;
    }
    
    // Update color in uniform if it changes dynamically
    materialRef.current.uniforms.glowColor.value = outlineColor;
  });

  return (
    <mesh position={posVec}>
      <sphereGeometry args={[radius * 1.08, 24, 24]} />
      <shaderMaterial
        ref={materialRef}
        args={[shader]}
        side={THREE.BackSide}
        blending={THREE.AdditiveBlending}
        transparent
        depthWrite={false}
      />
    </mesh>
  );
}
