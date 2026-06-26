"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { SceneConfig, PlanetData, DecisionNodeData } from "@/types";
import { SceneManager } from "@/lib/SceneManager";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { SelectionHighlight } from "../SelectionHighlight";

interface DecisionRingSceneProps {
  active: boolean;
  config: SceneConfig;
}

// 1. Connection Line component
interface ConnectionLineProps {
  fromNodeId: string;
  toPlanetId: string;
  style: "solid" | "dashed" | "dotted";
  color: string;
  nodePositionsRef: React.MutableRefObject<Record<string, THREE.Vector3>>;
  planetPositions: Record<string, THREE.Vector3>;
}

function ConnectionLine({
  fromNodeId,
  toPlanetId,
  style,
  color,
  nodePositionsRef,
  planetPositions,
}: ConnectionLineProps) {
  const lineRef = useRef<THREE.Line>(null);
  const geometry = useMemo(() => new THREE.BufferGeometry(), []);

  useEffect(() => {
    const initialPoints = [new THREE.Vector3(), new THREE.Vector3()];
    geometry.setFromPoints(initialPoints);
  }, [geometry]);

  useFrame(() => {
    const fromPos = nodePositionsRef.current[fromNodeId];
    const toPos = planetPositions[toPlanetId];

    if (!fromPos || !toPos || !lineRef.current) return;

    geometry.setFromPoints([fromPos, toPos]);

    if (style !== "solid") {
      lineRef.current.computeLineDistances();
    }
  });

  return (
    <line ref={lineRef as any} {...{ geometry } as any}>
      {style === "dashed" && (
        <lineDashedMaterial
          color={color}
          dashSize={1.2}
          gapSize={0.8}
          transparent
          opacity={0.7}
          depthWrite={false}
        />
      )}
      {style === "dotted" && (
        <lineDashedMaterial
          color={color}
          dashSize={0.3}
          gapSize={0.6}
          transparent
          opacity={0.7}
          depthWrite={false}
        />
      )}
      {style === "solid" && (
        <lineBasicMaterial
          color={color}
          transparent
          opacity={0.55}
          depthWrite={false}
        />
      )}
    </line>
  );
}

// 2. Static Capability Planet inside Decision Ring Scene
interface StaticPlanetProps {
  pData: PlanetData;
  qualityTier: string;
  shouldAnimate: boolean;
  setHoveredObject: (id: string | null) => void;
  expandCard: (id: string) => void;
}

function StaticPlanet({ pData, qualityTier, shouldAnimate, setHoveredObject, expandCard }: StaticPlanetProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const posVec = useMemo(() => new THREE.Vector3(...pData.position), [pData.position]);
  const sizeVal = pData.size * 0.75;

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);

  // Register static planet in Scene 6
  useEffect(() => {
    const handler = InteractionHandler.getInstance();
    handler.registerObject(pData.id, pData.position, sizeVal, {
      type: "Capability Planet",
      title: pData.name,
      description: `A capability planet composed of ${pData.entityCount} components. Systems health: ${(pData.health * 100).toFixed(0)}%.`,
      details: {
        "Lines of Code": pData.linesOfCode,
        "System Health": `${(pData.health * 100).toFixed(0)}%`,
        "Importance Rank": pData.importance
      }
    });
    return () => {
      handler.unregisterObject(pData.id);
    };
  }, [pData.id, pData.position, sizeVal, pData.name, pData.entityCount, pData.health, pData.linesOfCode, pData.importance]);

  const getHealthColor = (health: number): THREE.Color => {
    if (health >= 0.8) return new THREE.Color("#4CAF50");
    if (health >= 0.6) return new THREE.Color("#FFEB3B");
    return new THREE.Color("#F44336");
  };

  const healthColor = useMemo(() => getHealthColor(pData.health), [pData.health]);

  useFrame((_state, delta) => {
    if (shouldAnimate && meshRef.current) {
      meshRef.current.rotation.y += delta * 0.06;
    }
  });

  return (
    <group>
      {/* Selection Highlight */}
      <SelectionHighlight
        position={posVec}
        radius={sizeVal}
        hovered={hoveredObjectId === pData.id || focusedObjectId === pData.id}
        selected={expandedCardId === pData.id}
        color={pData.color}
      />

      {/* Planet Sphere */}
      <mesh
        ref={meshRef}
        position={posVec}
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
          emissiveIntensity={0.15}
          metalness={0.4}
          roughness={0.6}
        />
      </mesh>

      {/* Atmospheric Glow */}
      {qualityTier !== "low" && (
        <mesh position={posVec}>
          <sphereGeometry args={[sizeVal * 1.2, 32, 32]} />
          <shaderMaterial
            uniforms={{
              c: { value: 0.3 },
              p: { value: 3.5 },
              glowColor: { value: new THREE.Color(pData.color) },
            }}
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

// 3. Decision Node inside Ring Component
interface DecisionNodeProps {
  node: DecisionNodeData;
  nodeColor: string;
  qualityTier: string;
  shouldAnimate: boolean;
  nodePositionsRef: React.MutableRefObject<Record<string, THREE.Vector3>>;
  setHoveredObject: (id: string | null) => void;
  expandCard: (id: string) => void;
}

function DecisionNode({
  node,
  nodeColor,
  qualityTier,
  shouldAnimate,
  nodePositionsRef,
  setHoveredObject,
  expandCard,
}: DecisionNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);

  // Unregister node on unmount
  useEffect(() => {
    return () => {
      InteractionHandler.getInstance().unregisterObject(node.id);
    };
  }, [node.id]);

  const localX = Math.cos(node.anglePosition) * node.distanceFromCenter;
  const localZ = Math.sin(node.anglePosition) * node.distanceFromCenter;
  const localY = 0;

  const nodeSize = 1.3;

  useFrame((state) => {
    if (!meshRef.current) return;

    // Track rotating node absolute world coordinates
    const worldPos = new THREE.Vector3();
    meshRef.current.getWorldPosition(worldPos);
    nodePositionsRef.current[node.id] = worldPos;

    // Register rotating node coordinates dynamically
    InteractionHandler.getInstance().registerObject(node.id, worldPos, nodeSize, {
      type: "Architectural Decision",
      title: node.metadata.title,
      description: node.metadata.description,
      details: {
        "Lifecycle Status": node.status
      }
    });

    // Pulse nodes
    if (shouldAnimate && node.status === "accepted") {
      const time = state.clock.getElapsedTime();
      const pulse = Math.sin(time * 4.5 + meshRef.current.id) * 0.18 + 1.0;
      
      meshRef.current.scale.set(pulse, pulse, pulse);
      if (meshRef.current.material instanceof THREE.MeshStandardMaterial) {
        meshRef.current.material.emissiveIntensity = 0.5 + Math.sin(time * 4.5 + meshRef.current.id) * 0.25;
      }

      if (glowRef.current) {
        glowRef.current.scale.set(pulse, pulse, pulse);
        if (glowRef.current.material instanceof THREE.ShaderMaterial) {
          glowRef.current.material.uniforms.c.value = 0.55 + Math.sin(time * 4.5 + meshRef.current.id) * 0.2;
        }
      }
    }
  });

  const glowUniforms = useMemo(() => {
    return {
      c: { value: node.status === "accepted" ? 0.6 : 0.3 },
      p: { value: 3.5 },
      glowColor: { value: new THREE.Color(nodeColor) },
    };
  }, [nodeColor, node.status]);

  return (
    <group>
      {/* Selection Highlight */}
      <SelectionHighlight
        position={[localX, localY, localZ]}
        radius={nodeSize}
        hovered={hoveredObjectId === node.id || focusedObjectId === node.id}
        selected={expandedCardId === node.id}
        color={nodeColor}
      />

      {/* Node Sphere */}
      <mesh
        ref={meshRef}
        position={[localX, localY, localZ]}
        onClick={(e) => {
          e.stopPropagation();
          expandCard(node.id);
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHoveredObject(node.id);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHoveredObject(null);
        }}
      >
        <sphereGeometry args={[nodeSize, 16, 16]} />
        <meshStandardMaterial
          color={new THREE.Color(nodeColor)}
          emissive={new THREE.Color(nodeColor)}
          emissiveIntensity={node.status === "accepted" ? 0.6 : 0.25}
          metalness={0.2}
          roughness={0.4}
        />
      </mesh>

      {/* Node Glow */}
      {qualityTier !== "low" && (
        <mesh ref={glowRef} position={[localX, localY, localZ]}>
          <sphereGeometry args={[nodeSize * 1.35, 16, 16]} />
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

// 4. Decision Ring Component
interface DecisionRingProps {
  planetId: string;
  innerRadius: number;
  outerRadius: number;
  rotationSpeed: number;
  rotationAxis: [number, number, number];
  decisionNodes: DecisionNodeData[];
  planetColor: string;
  qualityTier: string;
  shouldAnimate: boolean;
  nodePositionsRef: React.MutableRefObject<Record<string, THREE.Vector3>>;
  planetPosVec: THREE.Vector3;
  getDecisionColor: (status: string) => string;
  setHoveredObject: (id: string | null) => void;
  expandCard: (id: string) => void;
}

function DecisionRing({
  innerRadius,
  outerRadius,
  rotationSpeed,
  rotationAxis,
  decisionNodes,
  planetColor,
  qualityTier,
  shouldAnimate,
  nodePositionsRef,
  planetPosVec,
  getDecisionColor,
  setHoveredObject,
  expandCard,
}: DecisionRingProps) {
  const groupRef = useRef<THREE.Group>(null);
  const axisVec = useMemo(() => new THREE.Vector3(...rotationAxis).normalize(), [rotationAxis]);

  useFrame((_state, delta) => {
    if (shouldAnimate && groupRef.current) {
      // Rotate the entire ring system local group centered at planet position
      groupRef.current.rotateOnAxis(axisVec, delta * rotationSpeed * 0.25);
    }
  });

  return (
    <group ref={groupRef} position={planetPosVec}>
      {/* 2D Ring Geometry lying flat locally in the XZ plane */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[innerRadius, outerRadius, 64]} />
        <meshBasicMaterial
          color={new THREE.Color(planetColor)}
          transparent
          opacity={0.12}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Decision Nodes placed locally within the rotatable group */}
      {decisionNodes.map((node) => {
        const nodeColor = getDecisionColor(node.status);
        return (
          <DecisionNode
            key={node.id}
            node={node}
            nodeColor={nodeColor}
            qualityTier={qualityTier}
            shouldAnimate={shouldAnimate}
            nodePositionsRef={nodePositionsRef}
            setHoveredObject={setHoveredObject}
            expandCard={expandCard}
          />
        );
      })}
    </group>
  );
}

// 5. Main Decision Ring Scene Component
export function DecisionRingScene({ active, config }: DecisionRingSceneProps) {
  const [initialized, setInitialized] = useState(false);
  const [scene4Planets, setScene4Planets] = useState<PlanetData[]>([]);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  // Tracks absolute world positions of rotating decision nodes
  const nodePositionsRef = useRef<Record<string, THREE.Vector3>>({});

  // 1. Asynchronously load Scene 4 configs
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
          console.error("[DecisionRingScene] Failed to load Scene 4 config:", error);
          setInitialized(true);
        }
      };
      loadScene4Config();
    }
  }, [active, initialized]);

  // Planet config dictionaries
  const planetConfigMap = useMemo(() => {
    const map = new Map<string, PlanetData>();
    scene4Planets.forEach((p) => map.set(p.id, p));
    return map;
  }, [scene4Planets]);

  const planetPositions = useMemo(() => {
    const pos: Record<string, THREE.Vector3> = {};
    scene4Planets.forEach((p) => {
      pos[p.id] = new THREE.Vector3(...p.position);
    });
    return pos;
  }, [scene4Planets]);

  // Decision node status color helper
  const getDecisionColor = (status: string): string => {
    switch (status) {
      case "accepted":
        return "#4CAF50";
      case "superseded":
        return "#90a4ae";
      case "deprecated":
        return "#F44336";
      default:
        return "#ffffff";
    }
  };

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

      {/* Render static capability planets */}
      {scene4Planets.map((planet) => (
        <StaticPlanet
          key={planet.id}
          pData={planet}
          qualityTier={qualityTier}
          shouldAnimate={shouldAnimate}
          setHoveredObject={setHoveredObject}
          expandCard={expandCard}
        />
      ))}

      {/* Render orbital decision rings */}
      {config.rings?.map((ring) => {
        const planet = planetConfigMap.get(ring.planetId);
        if (!planet) return null;

        const planetPosVec = planetPositions[ring.planetId];

        return (
          <DecisionRing
            key={ring.planetId}
            planetId={ring.planetId}
            innerRadius={ring.innerRadius}
            outerRadius={ring.outerRadius}
            rotationSpeed={ring.rotationSpeed}
            rotationAxis={ring.rotationAxis}
            decisionNodes={ring.decisionNodes}
            planetColor={planet.color}
            qualityTier={qualityTier}
            shouldAnimate={shouldAnimate}
            nodePositionsRef={nodePositionsRef}
            planetPosVec={planetPosVec}
            getDecisionColor={getDecisionColor}
            setHoveredObject={setHoveredObject}
            expandCard={expandCard}
          />
        );
      })}

      {/* Render connections */}
      {config.decisionConnections?.map((conn) => {
        const decisionNode = config.rings
          ?.flatMap((r) => r.decisionNodes)
          .find((n) => n.id === conn.fromDecisionId);

        const color = decisionNode ? getDecisionColor(decisionNode.status) : "#90caf9";

        return conn.toPlanetIds.map((toPlanetId) => (
          <ConnectionLine
            key={`${conn.fromDecisionId}-${toPlanetId}`}
            fromNodeId={conn.fromDecisionId}
            toPlanetId={toPlanetId}
            style={conn.lineStyle}
            color={color}
            nodePositionsRef={nodePositionsRef}
            planetPositions={planetPositions}
          />
        ));
      })}
    </group>
  );
}
