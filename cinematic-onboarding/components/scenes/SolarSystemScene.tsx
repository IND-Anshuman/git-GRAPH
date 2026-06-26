"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { SceneConfig, PlanetData } from "@/types";
import { SceneManager } from "@/lib/SceneManager";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { SelectionHighlight } from "../SelectionHighlight";

interface SolarSystemSceneProps {
  active: boolean;
  config: SceneConfig;
}

// 1. Energy Beam Component using high-performance GPU shaders
interface EnergyBeamProps {
  fromId: string;
  toId: string;
  intensity: number;
  flowSpeed: number;
  color: string;
  planetPositionsRef: React.MutableRefObject<Record<string, THREE.Vector3>>;
}

function EnergyBeam({ fromId, toId, intensity, flowSpeed, color, planetPositionsRef }: EnergyBeamProps) {
  const lineRef = useRef<THREE.Line>(null);
  const sparksRef = useRef<THREE.Points>(null);
  const lineMatRef = useRef<THREE.ShaderMaterial>(null);
  const sparksMatRef = useRef<THREE.ShaderMaterial>(null);

  // Setup static progress attribute arrays for GPU Bezier calculation
  const pointsCount = 100;
  const { progressArray, dummyPositions } = useMemo(() => {
    const progress = new Float32Array(pointsCount);
    const dummy = new Float32Array(pointsCount * 3);
    for (let i = 0; i < pointsCount; i++) {
      progress[i] = i / (pointsCount - 1);
    }
    return { progressArray: progress, dummyPositions: dummy };
  }, []);

  const uniforms = useMemo(() => {
    return {
      uFrom: { value: new THREE.Vector3() },
      uTo: { value: new THREE.Vector3() },
      uControl: { value: new THREE.Vector3() },
      uColor: { value: new THREE.Color(color) },
      uTime: { value: 0 },
      uFlowSpeed: { value: flowSpeed },
      uIntensity: { value: intensity },
    };
  }, [color, flowSpeed, intensity]);

  useFrame((state) => {
    const fromPos = planetPositionsRef.current[fromId];
    const toPos = planetPositionsRef.current[toId];

    if (!fromPos || !toPos) return;

    // Calculate mid-point and control point for a 3D arching Bezier curve
    const distance = fromPos.distanceTo(toPos);
    const midPoint = new THREE.Vector3().addVectors(fromPos, toPos).multiplyScalar(0.5);
    const arcHeight = distance * 0.25; // 25% of distance as arc height
    const controlPoint = midPoint.clone().add(new THREE.Vector3(0, arcHeight, 0));

    if (lineMatRef.current) {
      lineMatRef.current.uniforms.uFrom.value.copy(fromPos);
      lineMatRef.current.uniforms.uTo.value.copy(toPos);
      lineMatRef.current.uniforms.uControl.value.copy(controlPoint);
      lineMatRef.current.uniforms.uTime.value = state.clock.getElapsedTime();
    }
    if (sparksMatRef.current) {
      sparksMatRef.current.uniforms.uFrom.value.copy(fromPos);
      sparksMatRef.current.uniforms.uTo.value.copy(toPos);
      sparksMatRef.current.uniforms.uControl.value.copy(controlPoint);
      sparksMatRef.current.uniforms.uTime.value = state.clock.getElapsedTime();
    }
  });

  return (
    <group>
      {/* 1. Base Bezier connection line */}
      <line ref={lineRef as any}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[dummyPositions, 3]}
          />
          <bufferAttribute
            attach="attributes-aProgress"
            args={[progressArray, 1]}
          />
        </bufferGeometry>
        <shaderMaterial
          ref={lineMatRef}
          uniforms={uniforms}
          transparent
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          vertexShader={`
            uniform vec3 uFrom;
            uniform vec3 uTo;
            uniform vec3 uControl;
            attribute float aProgress;
            varying float vProgress;
            void main() {
              vProgress = aProgress;
              float t = aProgress;
              float oneMinusT = 1.0 - t;
              // Bezier quadratic formula on GPU
              vec3 pos = oneMinusT * oneMinusT * uFrom + 2.0 * oneMinusT * t * uControl + t * t * uTo;
              vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
              gl_Position = projectionMatrix * mvPosition;
            }
          `}
          fragmentShader={`
            uniform vec3 uColor;
            uniform float uTime;
            uniform float uFlowSpeed;
            uniform float uIntensity;
            varying float vProgress;
            void main() {
              // Pulse gradient pattern traveling along the connection path
              float pulse = sin(vProgress * 15.0 - uTime * uFlowSpeed * 4.0) * 0.5 + 0.5;
              float alpha = (0.2 + 0.8 * pulse) * uIntensity * 0.4;
              gl_FragColor = vec4(uColor, alpha);
            }
          `}
        />
      </line>

      {/* 2. Flowing spark particles */}
      <points ref={sparksRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[dummyPositions, 3]}
          />
          <bufferAttribute
            attach="attributes-aProgress"
            args={[progressArray, 1]}
          />
        </bufferGeometry>
        <shaderMaterial
          ref={sparksMatRef}
          uniforms={uniforms}
          transparent
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          vertexShader={`
            uniform vec3 uFrom;
            uniform vec3 uTo;
            uniform vec3 uControl;
            uniform float uTime;
            uniform float uFlowSpeed;
            attribute float aProgress;
            varying float vT;
            void main() {
              // Animate flow over time
              float t = fract(aProgress + uTime * uFlowSpeed * 0.15);
              vT = t;
              float oneMinusT = 1.0 - t;
              vec3 pos = oneMinusT * oneMinusT * uFrom + 2.0 * oneMinusT * t * uControl + t * t * uTo;
              vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
              gl_Position = projectionMatrix * mvPosition;
              
              // Soft scale/fade near ends of the connection
              float sizePulse = sin(t * 3.14159);
              gl_PointSize = 12.0 * sizePulse * (300.0 / -mvPosition.z);
            }
          `}
          fragmentShader={`
            uniform vec3 uColor;
            uniform float uIntensity;
            varying float vT;
            void main() {
              float dist = distance(gl_PointCoord, vec2(0.5));
              if (dist > 0.5) discard;
              // Soft alpha gradient for glowing point particle
              float alpha = smoothstep(0.5, 0.05, dist) * uIntensity;
              gl_FragColor = vec4(uColor, alpha);
            }
          `}
        />
      </points>
    </group>
  );
}

// 2. Wavy circular orbit lines
interface OrbitPathProps {
  sunPos: THREE.Vector3;
  orbitalRadius: number;
  color: string;
}

function OrbitPath({ sunPos, orbitalRadius, color }: OrbitPathProps) {
  const pointsData = useMemo(() => {
    const pts = [];
    const segments = 128;
    for (let i = 0; i <= segments; i++) {
      const theta = (i / segments) * Math.PI * 2;
      const x = Math.cos(theta) * orbitalRadius;
      const z = Math.sin(theta) * orbitalRadius;
      const y = Math.sin(theta * 2.0) * orbitalRadius * 0.08;
      pts.push(x, y, z);
    }
    return new Float32Array(pts);
  }, [orbitalRadius]);

  return (
    <lineLoop position={sunPos} ref={null}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[pointsData, 3]}
        />
      </bufferGeometry>
      <lineBasicMaterial
        color={color}
        transparent
        opacity={0.18}
        depthWrite={false}
      />
    </lineLoop>
  );
}

// 3. Domain Sun Component
interface DomainSunProps {
  name: string;
  sunPosition: [number, number, number];
  sunSize: number;
  color: string;
  qualityTier: string;
  shouldAnimate: boolean;
  setHoveredObject: (id: string | null) => void;
  expandCard: (id: string) => void;
}

function DomainSun({
  name,
  sunPosition,
  sunSize,
  color,
  qualityTier,
  shouldAnimate,
  setHoveredObject,
  expandCard,
}: DomainSunProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const sunPosVec = useMemo(() => new THREE.Vector3(...sunPosition), [sunPosition]);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);

  const domainId = `domain-${name.toLowerCase()}`;

  // Register domain sun with InteractionHandler
  useEffect(() => {
    const handler = InteractionHandler.getInstance();
    handler.registerObject(domainId, sunPosition, sunSize * 0.8, {
      type: "Architectural Domain",
      title: `${name} Domain`,
      description: `Architectural domain sun organizing capability planets.`,
      details: {
        "Sun Size": sunSize
      }
    });
    return () => {
      handler.unregisterObject(domainId);
    };
  }, [domainId, sunPosition, sunSize, name]);

  useFrame((state, delta) => {
    if (shouldAnimate) {
      if (meshRef.current) meshRef.current.rotation.y += delta * 0.1;
      if (glowRef.current && glowRef.current.material instanceof THREE.ShaderMaterial) {
        glowRef.current.material.uniforms.uTime.value = state.clock.getElapsedTime();
      }
    }
  });

  const glowUniforms = useMemo(() => {
    return {
      c: { value: 0.55 },
      p: { value: 3.2 },
      glowColor: { value: new THREE.Color(color) },
      uTime: { value: 0 },
    };
  }, [color]);

  return (
    <group>
      {/* Core Sun */}
      <mesh
        ref={meshRef}
        position={sunPosVec}
        onClick={(e) => {
          e.stopPropagation();
          expandCard(domainId);
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHoveredObject(domainId);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHoveredObject(null);
        }}
      >
        <sphereGeometry args={[sunSize * 0.8, 32, 32]} />
        <meshBasicMaterial color={color} />
      </mesh>

      {/* Selection Highlight */}
      <SelectionHighlight
        position={sunPosVec}
        radius={sunSize * 0.8}
        hovered={hoveredObjectId === domainId || focusedObjectId === domainId}
        selected={expandedCardId === domainId}
        color={color}
      />

      {/* Atmospheric Corona */}
      {qualityTier !== "low" && (
        <mesh ref={glowRef} position={sunPosVec}>
          <sphereGeometry args={[sunSize * 1.2, 32, 32]} />
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
              uniform float uTime;
              varying vec3 vNormal;
              varying vec3 vViewPosition;
              void main() {
                vec3 normalVec = normalize(vNormal);
                vec3 viewVec = normalize(vViewPosition);
                float dotProd = max(0.0, dot(normalVec, viewVec));
                float pulse = sin(uTime * 3.5) * 0.12 + 0.88;
                float intensity = pow(1.0 - dotProd, p) * pulse;
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

// 4. Orbiting Capability Planet Component
interface OrbitingPlanetProps {
  pData: PlanetData;
  orbitalRadius: number;
  orbitalSpeed: number;
  spacingAngle: number;
  sunPos: THREE.Vector3;
  planetPositionsRef: React.MutableRefObject<Record<string, THREE.Vector3>>;
  shouldAnimate: boolean;
  qualityTier: string;
  setHoveredObject: (id: string | null) => void;
  expandCard: (id: string) => void;
}

function OrbitingPlanet({
  pData,
  orbitalRadius,
  orbitalSpeed,
  spacingAngle,
  sunPos,
  planetPositionsRef,
  shouldAnimate,
  qualityTier,
  setHoveredObject,
  expandCard,
}: OrbitingPlanetProps) {
  const groupRef = useRef<THREE.Group>(null);
  const coreMeshRef = useRef<THREE.Mesh>(null);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);

  // Unregister planet on unmount
  useEffect(() => {
    return () => {
      InteractionHandler.getInstance().unregisterObject(pData.id);
    };
  }, [pData.id]);

  const getHealthColor = (health: number): THREE.Color => {
    if (health >= 0.8) return new THREE.Color("#4CAF50");
    if (health >= 0.6) return new THREE.Color("#FFEB3B");
    return new THREE.Color("#F44336");
  };

  const healthColor = useMemo(() => getHealthColor(pData.health), [pData.health]);
  const sizeVal = pData.size * 0.75; // Increased scale factor for visual clarity

  useFrame((state, delta) => {
    const time = state.clock.getElapsedTime();
    
    // Compute current position along wavy inclined orbit in 3D
    const orbitAngle = spacingAngle + (shouldAnimate ? time * orbitalSpeed * 0.15 : 0);
    const x = sunPos.x + Math.cos(orbitAngle) * orbitalRadius;
    const z = sunPos.z + Math.sin(orbitAngle) * orbitalRadius;
    const y = sunPos.y + Math.sin(orbitAngle * 2.0) * orbitalRadius * 0.08;

    const currentPos = new THREE.Vector3(x, y, z);
    
    if (groupRef.current) {
      groupRef.current.position.copy(currentPos);
    }
    if (coreMeshRef.current && shouldAnimate) {
      coreMeshRef.current.rotation.y += delta * 0.4;
    }

    // Save coordinates to share with EnergyBeams
    planetPositionsRef.current[pData.id] = currentPos;

    // Register coordinates with InteractionHandler dynamically
    InteractionHandler.getInstance().registerObject(pData.id, currentPos, sizeVal, {
      type: "Capability Planet",
      title: pData.name,
      description: `A capability planet composed of ${pData.entityCount} components. Systems health: ${(pData.health * 100).toFixed(0)}%.`,
      details: {
        "Lines of Code": pData.linesOfCode,
        "System Health": `${(pData.health * 100).toFixed(0)}%`,
        "Importance Rank": pData.importance
      }
    });
  });

  const glowUniforms = useMemo(() => {
    return {
      c: { value: 0.5 }, // Increased glow intensity
      p: { value: 3.0 }, // Softer rim falloff
      glowColor: { value: new THREE.Color(pData.color) },
    };
  }, [pData.color]);

  return (
    <group ref={groupRef}>
      {/* Selection Highlight */}
      <SelectionHighlight
        position={[0, 0, 0]}
        radius={sizeVal}
        hovered={hoveredObjectId === pData.id || focusedObjectId === pData.id}
        selected={expandedCardId === pData.id}
        color={pData.color}
      />

      {/* Planet Sphere Core */}
      <mesh
        ref={coreMeshRef}
        onClick={(e) => {
          e.stopPropagation();
          expandCard(pData.id);
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHoveredObject(pData.id);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHoveredObject(null);
        }}
      >
        <sphereGeometry args={[sizeVal, 32, 32]} />
        <meshStandardMaterial
          color={healthColor}
          emissive={healthColor}
          emissiveIntensity={0.5} // Increased emissive power
          metalness={0.7} // More reflective metal look
          roughness={0.15} // Glossy, polished surface
        />
      </mesh>

      {/* Dynamic planetary ring around the orbiting capability planet */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[sizeVal * 1.35, sizeVal * 1.65, 32]} />
        <meshBasicMaterial
          color={new THREE.Color(pData.color)}
          transparent
          opacity={0.22}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Planet Atmospheric Glow */}
      {qualityTier !== "low" && (
        <mesh>
          <sphereGeometry args={[sizeVal * 1.35, 32, 32]} />
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

// 5. Main Solar System Scene Component
export function SolarSystemScene({ active, config }: SolarSystemSceneProps) {
  const [initialized, setInitialized] = useState(false);
  const [scene4Planets, setScene4Planets] = useState<PlanetData[]>([]);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  // Sharing coordinates with energy beams dynamically
  const planetPositionsRef = useRef<Record<string, THREE.Vector3>>({});

  useEffect(() => {
    if (active && !initialized) {
      const loadScene4Config = async () => {
        try {
          const sm = SceneManager.getInstance();
          let s4Config = sm.getSceneConfig(4);
          if (!s4Config) {
            await sm.loadScene(4);
            s4Config = sm.getSceneConfig(4);
          }
          if (s4Config && s4Config.planets) {
            setScene4Planets(s4Config.planets);
          }
          setInitialized(true);
        } catch (error) {
          console.error("[SolarSystemScene] Failed to load Scene 4 config:", error);
          setInitialized(true);
        }
      };
      loadScene4Config();
    }
  }, [active, initialized]);

  // Planet config map for quick lookup
  const planetConfigMap = useMemo(() => {
    const map = new Map<string, PlanetData>();
    scene4Planets.forEach((p) => map.set(p.id, p));
    return map;
  }, [scene4Planets]);

  if (!active || !initialized) return null;

  return (
    <group visible={active}>
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

      {/* Render Domains */}
      {config.domains?.map((domain) => {
        const sunPosVec = new THREE.Vector3(...domain.sunPosition);

        return (
          <group key={domain.name}>
            {/* Core Sun and Corona Glow */}
            <DomainSun
              name={domain.name}
              sunPosition={domain.sunPosition}
              sunSize={domain.sunSize}
              color={domain.color}
              qualityTier={qualityTier}
              shouldAnimate={shouldAnimate}
              setHoveredObject={setHoveredObject}
              expandCard={expandCard}
            />

            {/* Orbit Path lines */}
            <OrbitPath
              sunPos={sunPosVec}
              orbitalRadius={domain.orbitalRadius}
              color={domain.color}
            />

            {/* Orbiting Capability Planets */}
            {domain.planets.map((pId, pIdx) => {
              const pData = planetConfigMap.get(pId);
              if (!pData) return null;

              // Space planets evenly on same orbits
              const spacingAngle = (pIdx / domain.planets.length) * Math.PI * 2;

              return (
                <OrbitingPlanet
                  key={pId}
                  pData={pData}
                  orbitalRadius={domain.orbitalRadius}
                  orbitalSpeed={domain.orbitalSpeed}
                  spacingAngle={spacingAngle}
                  sunPos={sunPosVec}
                  planetPositionsRef={planetPositionsRef}
                  shouldAnimate={shouldAnimate}
                  qualityTier={qualityTier}
                  setHoveredObject={setHoveredObject}
                  expandCard={expandCard}
                />
              );
            })}
          </group>
        );
      })}

      {/* Dynamic arcing energy beams */}
      {config.energyBeams?.map((beam, idx) => {
        const domainColor =
          config.domains?.find((d) => d.planets.includes(beam.fromPlanetId))?.color ?? "#9c27b0";

        return (
          <EnergyBeam
            key={`beam-${idx}`}
            fromId={beam.fromPlanetId}
            toId={beam.toPlanetId}
            intensity={beam.intensity}
            flowSpeed={beam.flowSpeed}
            color={domainColor}
            planetPositionsRef={planetPositionsRef}
          />
        );
      })}
    </group>
  );
}
