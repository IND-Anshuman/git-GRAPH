"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { SceneConfig, DecisionRingData, DecisionNodeData } from "@/types";
import { SceneManager } from "@/lib/SceneManager";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { SelectionHighlight } from "../SelectionHighlight";
import { useOnboardingStore } from "@/stores/onboardingStore";

interface UniverseSceneProps {
  active: boolean;
  config: SceneConfig;
  previousSceneConfigs?: SceneConfig[];
}

// ----------------------------------------------------
// 1. Layer 0 - Chaos Particles (0 - 50 units)
// ----------------------------------------------------
function ChaosLayer({ count }: { count: number }) {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = Math.random() * 45;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
    }
    return { positions: pos };
  }, [count]);

  useFrame((_state, _delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += 0.0001;
      pointsRef.current.rotation.x += 0.00005;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        color="#a5b4fc"
        size={0.06}
        transparent
        opacity={0.2}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

// ----------------------------------------------------
// 2. Layer 1 - Semantic Entities (50 - 80 units)
// ----------------------------------------------------
function SemanticEntitiesLayer({ count }: { count: number }) {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions, colors } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const cols = new Float32Array(count * 3);
    const palette = [
      new THREE.Color("#2196F3"), // blue
      new THREE.Color("#9C27B0"), // purple
      new THREE.Color("#4CAF50"), // green
      new THREE.Color("#FF9800"), // orange
    ];

    for (let i = 0; i < count; i++) {
      const r = 50 + Math.random() * 25;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);

      const color = palette[i % palette.length];
      cols[i * 3] = color.r;
      cols[i * 3 + 1] = color.g;
      cols[i * 3 + 2] = color.b;
    }
    return { positions: pos, colors: cols };
  }, [count]);

  useFrame((_state, _delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += 0.00015;
      pointsRef.current.rotation.z -= 0.00008;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        vertexColors
        transparent
        opacity={0.3}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

// ----------------------------------------------------
// 3. Layer 2 - Constellations (80 - 120 units)
// ----------------------------------------------------
function ConstellationsLayer({ count }: { count: number }) {
  const groupRef = useRef<THREE.Group>(null);

  const { positions, lineIndices } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const linePairs: number[] = [];

    // Define 5 cluster centers at radius 100
    const centers: THREE.Vector3[] = [];
    for (let c = 0; c < 5; c++) {
      const theta = (c / 5) * Math.PI * 2;
      const phi = Math.PI / 3 + (Math.random() * Math.PI) / 3;
      centers.push(
        new THREE.Vector3(
          100 * Math.sin(phi) * Math.cos(theta),
          100 * Math.sin(phi) * Math.sin(theta),
          100 * Math.cos(phi)
        )
      );
    }

    // Populate points around centers
    for (let i = 0; i < count; i++) {
      const center = centers[i % centers.length];
      const offset = new THREE.Vector3(
        (Math.random() - 0.5) * 18,
        (Math.random() - 0.5) * 18,
        (Math.random() - 0.5) * 18
      );
      const pointPos = center.clone().add(offset);
      
      pos[i * 3] = pointPos.x;
      pos[i * 3 + 1] = pointPos.y;
      pos[i * 3 + 2] = pointPos.z;

      // Draw lines between very close neighbors (to keep it fast, sample sparsely)
      if (i > 0 && i % 4 === 0) {
        linePairs.push(i - 1, i);
      }
    }

    return { positions: pos, lineIndices: new Uint16Array(linePairs) };
  }, [count]);

  useFrame((_state, _delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.0002;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Constellation Star points */}
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[positions, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          color="#38bdf8"
          size={0.1}
          transparent
          opacity={0.35}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>

      {/* Constellation Lines */}
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[positions, 3]}
          />
          <bufferAttribute
            attach="index"
            args={[lineIndices, 1]}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color="#0ea5e9"
          transparent
          opacity={0.08}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </lineSegments>
    </group>
  );
}

// ----------------------------------------------------
// Helper to render static elements of previous scenes
// ----------------------------------------------------
export function UniverseScene({ active, config }: UniverseSceneProps) {
  const [loadedConfigs, setLoadedConfigs] = useState<{
    s4: SceneConfig | null;
    s5: SceneConfig | null;
    s6: SceneConfig | null;
    s7: SceneConfig | null;
  }>({ s4: null, s5: null, s6: null, s7: null });

  // Load previous scene configs asynchronously
  useEffect(() => {
    const loadAllConfigs = async () => {
      try {
        const sm = SceneManager.getInstance();
        
        let s4 = sm.getSceneConfig(4);
        if (!s4) {
          await sm.loadScene(4);
          s4 = sm.getSceneConfig(4);
        }
        
        let s5 = sm.getSceneConfig(5);
        if (!s5) {
          await sm.loadScene(5);
          s5 = sm.getSceneConfig(5);
        }

        let s6 = sm.getSceneConfig(6);
        if (!s6) {
          await sm.loadScene(6);
          s6 = sm.getSceneConfig(6);
        }

        let s7 = sm.getSceneConfig(7);
        if (!s7) {
          await sm.loadScene(7);
          s7 = sm.getSceneConfig(7);
        }

        setLoadedConfigs({ s4: s4 ?? null, s5: s5 ?? null, s6: s6 ?? null, s7: s7 ?? null });
      } catch (err) {
        console.error("[UniverseScene] Failed to load previous configs:", err);
      }
    };

    if (active) {
      loadAllConfigs();
    }
  }, [active]);

  if (!active) return null;

  return (
    <group visible={active}>
      {/* Ambient and general lighting for Universe view */}
      <ambientLight
        color={config.lighting.ambient.color}
        intensity={config.lighting.ambient.intensity}
      />
      {config.lighting.point?.map((light, i) => (
        <pointLight
          key={`pt-${i}`}
          color={light.color}
          intensity={light.intensity}
          position={light.position}
          distance={light.distance}
          decay={2}
        />
      ))}

      {/* 7 Concentric Layers */}
      <ChaosLayer count={1500} />
      <SemanticEntitiesLayer count={600} />
      <ConstellationsLayer count={400} />

      <CompositeLayers
        active={active}
        configs={loadedConfigs}
      />

      {/* HTML Overlay UI details card */}
      <HtmlOverlay config={config} />
    </group>
  );
}

// ----------------------------------------------------
// Local Interactive Wrappers for Universe Elements
// ----------------------------------------------------

interface UniversePlanetProps {
  planet: any;
  scaledPos: [number, number, number];
  healthColor: THREE.Color;
}

function UniversePlanet({ planet, scaledPos, healthColor }: UniversePlanetProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  useEffect(() => {
    return () => {
      InteractionHandler.getInstance().unregisterObject(planet.id);
    };
  }, [planet.id]);

  useFrame(() => {
    if (!meshRef.current) return;
    const worldPos = new THREE.Vector3();
    meshRef.current.getWorldPosition(worldPos);

    InteractionHandler.getInstance().registerObject(planet.id, worldPos, planet.size * 0.7, {
      type: "Capability Planet",
      title: planet.name,
      description: `A capability consisting of ${planet.entityCount} components. Systems health: ${(planet.health * 100).toFixed(0)}%.`,
      layerName: "Capability Planets",
      details: {
        "Lines of Code": planet.linesOfCode,
        "System Health": `${(planet.health * 100).toFixed(0)}%`,
        "Importance Index": planet.importance
      }
    });
  });

  return (
    <group>
      <SelectionHighlight
        position={scaledPos}
        radius={planet.size * 0.7}
        hovered={hoveredObjectId === planet.id || focusedObjectId === planet.id}
        selected={expandedCardId === planet.id}
        color={planet.color}
      />
      <mesh
        ref={meshRef}
        position={scaledPos}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHoveredObject(planet.id);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHoveredObject(null);
        }}
        onClick={(e) => {
          e.stopPropagation();
          expandCard(planet.id);
        }}
      >
        <sphereGeometry args={[planet.size * 0.7, 16, 16]} />
        <meshStandardMaterial
          color={healthColor}
          emissive={healthColor}
          emissiveIntensity={0.12}
          metalness={0.4}
          roughness={0.6}
        />
      </mesh>
    </group>
  );
}

interface UniverseDomainProps {
  domain: any;
  idx: number;
  scaledSunPos: [number, number, number];
  color: THREE.Color;
}

function UniverseDomain({ domain, idx, scaledSunPos, color }: UniverseDomainProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const id = `domain-${idx}`;

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  useEffect(() => {
    return () => {
      InteractionHandler.getInstance().unregisterObject(id);
    };
  }, [id]);

  useFrame(() => {
    if (!meshRef.current) return;
    const worldPos = new THREE.Vector3();
    meshRef.current.getWorldPosition(worldPos);

    InteractionHandler.getInstance().registerObject(id, worldPos, domain.sunSize * 0.55, {
      type: "Architectural Domain",
      title: `${domain.name} Domain`,
      description: `Architectural domain sun organizing ${domain.planets.length} capability planets.`,
      layerName: "Architectural Domains",
      details: {
        "Orbital Radius": domain.orbitalRadius,
        "Orbital Speed": domain.orbitalSpeed
      }
    });
  });

  return (
    <group>
      <SelectionHighlight
        position={scaledSunPos}
        radius={domain.sunSize * 0.55}
        hovered={hoveredObjectId === id || focusedObjectId === id}
        selected={expandedCardId === id}
        color={domain.color}
      />
      <mesh
        ref={meshRef}
        position={scaledSunPos}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHoveredObject(id);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHoveredObject(null);
        }}
        onClick={(e) => {
          e.stopPropagation();
          expandCard(id);
        }}
      >
        <sphereGeometry args={[domain.sunSize * 0.55, 16, 16]} />
        <meshBasicMaterial color={color} />
      </mesh>
    </group>
  );
}

interface UniverseDecisionNodeProps {
  node: DecisionNodeData;
  planetPos: [number, number, number];
}

function UniverseDecisionNode({ node, planetPos }: UniverseDecisionNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  useEffect(() => {
    return () => {
      InteractionHandler.getInstance().unregisterObject(node.id);
    };
  }, [node.id]);

  const localX = Math.cos(node.anglePosition) * node.distanceFromCenter * 0.75;
  const localZ = Math.sin(node.anglePosition) * node.distanceFromCenter * 0.75;
  const localPos: [number, number, number] = [localX, 0, localZ];

  useFrame(() => {
    if (!meshRef.current) return;
    const worldPos = new THREE.Vector3();
    meshRef.current.getWorldPosition(worldPos);

    InteractionHandler.getInstance().registerObject(node.id, worldPos, 0.55, {
      type: "Decision Node",
      title: node.metadata.title,
      description: node.metadata.description,
      layerName: "Decision Rings",
      details: {
        "Lifecycle Status": node.status
      }
    });
  });

  return (
    <group position={planetPos}>
      <SelectionHighlight
        position={localPos}
        radius={0.55}
        hovered={hoveredObjectId === node.id || focusedObjectId === node.id}
        selected={expandedCardId === node.id}
        color="#4CAF50"
      />
      <mesh
        ref={meshRef}
        position={localPos}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHoveredObject(node.id);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHoveredObject(null);
        }}
        onClick={(e) => {
          e.stopPropagation();
          expandCard(node.id);
        }}
      >
        <sphereGeometry args={[0.55, 8, 8]} />
        <meshBasicMaterial color="#4CAF50" />
      </mesh>
    </group>
  );
}

interface UniverseReasoningNodeProps {
  node: any;
  scaledNodePos: [number, number, number];
  colorObj: THREE.Color;
  colorHex: string;
}

function UniverseReasoningNode({ node, scaledNodePos, colorObj, colorHex }: UniverseReasoningNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  useEffect(() => {
    return () => {
      InteractionHandler.getInstance().unregisterObject(node.id);
    };
  }, [node.id]);

  useFrame(() => {
    if (!meshRef.current) return;
    const worldPos = new THREE.Vector3();
    meshRef.current.getWorldPosition(worldPos);

    InteractionHandler.getInstance().registerObject(node.id, worldPos, node.size * 0.6, {
      type: "Reasoning Node",
      title: node.metadata.title,
      description: node.metadata.description,
      layerName: "Reasoning Network",
      details: {
        "Evidence Type": node.type,
        "Confidence Score": `${(node.confidenceScore * 100).toFixed(0)}%`
      }
    });
  });

  return (
    <group>
      <SelectionHighlight
        position={scaledNodePos}
        radius={node.size * 0.6}
        hovered={hoveredObjectId === node.id || focusedObjectId === node.id}
        selected={expandedCardId === node.id}
        color={colorHex}
      />
      <mesh
        ref={meshRef}
        position={scaledNodePos}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHoveredObject(node.id);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHoveredObject(null);
        }}
        onClick={(e) => {
          e.stopPropagation();
          expandCard(node.id);
        }}
      >
        <sphereGeometry args={[node.size * 0.6, 12, 12]} />
        <meshStandardMaterial
          color={colorObj}
          emissive={colorObj}
          emissiveIntensity={0.25}
          metalness={0.4}
          roughness={0.5}
        />
      </mesh>
    </group>
  );
}

// ----------------------------------------------------
// 4. Layers 3-6: Planets, Solar Systems, Rings, Network
// ----------------------------------------------------
function CompositeLayers({
  active,
  configs,
}: {
  active: boolean;
  configs: { s4: SceneConfig | null; s5: SceneConfig | null; s6: SceneConfig | null; s7: SceneConfig | null };
}) {
  const groupRef = useRef<THREE.Group>(null);
  const frameCountRef = useRef(0);

  // Slow frame rate throttling (updating only every 3rd frame)
  useFrame((_state, _delta) => {
    if (!active) return;
    frameCountRef.current++;

    if (frameCountRef.current % 3 === 0 && groupRef.current) {
      // Gentle spin to the outer architecture
      groupRef.current.rotation.y += 0.0003;
    }
  });

  // Position scaling helpers (concentric shells)
  const scalePlanetPos = (pos: [number, number, number]): [number, number, number] => {
    const vec = new THREE.Vector3(...pos).normalize();
    return vec.multiplyScalar(135).toArray() as [number, number, number];
  };

  const scaleSunPos = (pos: [number, number, number]): [number, number, number] => {
    const vec = new THREE.Vector3(...pos).normalize();
    return vec.multiplyScalar(190).toArray() as [number, number, number];
  };

  const scaleNetworkNodePos = (pos: [number, number, number]): [number, number, number] => {
    const vec = new THREE.Vector3(...pos).normalize();
    return vec.multiplyScalar(300).toArray() as [number, number, number];
  };

  // Memoize connection lines for Scene 7 outermost shell
  const networkConnections = useMemo(() => {
    if (!configs.s7?.networkNodes) return [];
    
    // Sample only a subset (e.g. 18 nodes) of the nodes to maintain FPS in composite view
    const nodes = configs.s7.networkNodes.slice(0, 20);
    const list: Array<{ id: string; from: THREE.Vector3; to: THREE.Vector3 }> = [];
    const threshold = 55.0; // wider threshold because nodes are normalized and scaled outwards

    for (let i = 0; i < nodes.length; i++) {
      const posI = new THREE.Vector3(...scaleNetworkNodePos(nodes[i].position));
      for (let j = i + 1; j < nodes.length; j++) {
        const posJ = new THREE.Vector3(...scaleNetworkNodePos(nodes[j].position));
        if (posI.distanceTo(posJ) < threshold) {
          list.push({
            id: `net-conn-${i}-${j}`,
            from: posI,
            to: posJ
          });
        }
      }
    }
    return list;
  }, [configs.s7]);

  // Planet color mapping helper
  const getHealthColor = (health: number): string => {
    if (health >= 0.8) return "#4CAF50";
    if (health >= 0.6) return "#FFEB3B";
    return "#F44336";
  };

  // Scene 7 type color helper
  const getNodeColor = (type: string): string => {
    switch (type) {
      case "code_reference": return "#2196F3";
      case "test_result": return "#4CAF50";
      case "metric": return "#FF9800";
      case "documentation": return "#9C27B0";
      case "decision_record": return "#00BCD4";
      default: return "#ffffff";
    }
  };

  return (
    <group ref={groupRef}>
      {/* 4. Layer 3 - Capability Planets */}
      {configs.s4?.planets?.map((planet) => {
        const scaledPos = scalePlanetPos(planet.position);
        const healthColor = new THREE.Color(getHealthColor(planet.health));

        return (
          <UniversePlanet
            key={`l3-${planet.id}`}
            planet={planet}
            scaledPos={scaledPos}
            healthColor={healthColor}
          />
        );
      })}

      {/* 5. Layer 4 - Domain Solar Systems */}
      {configs.s5?.domains?.map((domain, idx) => {
        const scaledSunPos = scaleSunPos(domain.sunPosition);
        const color = new THREE.Color(domain.color);

        return (
          <UniverseDomain
            key={`l4-${idx}`}
            domain={domain}
            idx={idx}
            scaledSunPos={scaledSunPos}
            color={color}
          />
        );
      })}

      {/* 6. Layer 5 - Decision Rings */}
      {configs.s6?.rings?.map((ring: DecisionRingData) => {
        const matchingPlanet = configs.s4?.planets?.find((p) => p.id === ring.planetId);
        if (!matchingPlanet) return null;

        const scaledPlanetPos = scalePlanetPos(matchingPlanet.position);
        const planetColor = new THREE.Color(matchingPlanet.color);

        return (
          <group key={`l5-ring-${ring.planetId}`}>
            {/* Subtle Ring flat XZ */}
            <mesh position={scaledPlanetPos} rotation={[Math.PI / 2, 0, 0]}>
              <ringGeometry args={[ring.innerRadius * 0.75, ring.outerRadius * 0.75, 32]} />
              <meshBasicMaterial
                color={planetColor}
                transparent
                opacity={0.06}
                side={THREE.DoubleSide}
                depthWrite={false}
              />
            </mesh>

            {/* Render decision nodes */}
            {ring.decisionNodes
              ?.filter((n: DecisionNodeData) => n.status === "accepted")
              .map((node: DecisionNodeData) => (
                <UniverseDecisionNode
                  key={`l5-node-${node.id}`}
                  node={node}
                  planetPos={scaledPlanetPos}
                />
              ))}
          </group>
        );
      })}

      {/* 7. Layer 6 - Reasoning Network (Outermost shell) */}
      {configs.s7?.networkNodes?.slice(0, 20).map((node) => {
        const scaledNodePos = scaleNetworkNodePos(node.position);
        const colorHex = getNodeColor(node.type);
        const colorObj = new THREE.Color(colorHex);

        return (
          <UniverseReasoningNode
            key={`l6-${node.id}`}
            node={node}
            scaledNodePos={scaledNodePos}
            colorObj={colorObj}
            colorHex={colorHex}
          />
        );
      })}

      {/* Scene 7 Outermost Connection Lines */}
      {networkConnections.map((conn) => (
        <line
          key={`l6-conn-${conn.id}`}
          {...{
            geometry: new THREE.BufferGeometry().setFromPoints([conn.from, conn.to])
          } as any}
        >
          <lineBasicMaterial
            color="#00E5FF"
            transparent
            opacity={0.08}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
          />
        </line>
      ))}
    </group>
  );
}

// ----------------------------------------------------
// 5. HTML Overlay Component
// ----------------------------------------------------
function HtmlOverlay({ config }: { config: SceneConfig }) {
  return (
    <div className="absolute inset-0 pointer-events-none z-10 flex flex-col justify-between p-8 text-white select-none">
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .animate-fade-in-delayed {
          opacity: 0;
          animation: fadeIn 1.5s cubic-bezier(0.16, 1, 0.3, 1) 0.8s forwards;
        }
      `}</style>

      {/* Top Banner title */}
      <div className="text-center mt-2">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-widest uppercase pointer-events-auto animate-fade-in text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-purple-400 drop-shadow-[0_0_15px_rgba(0,229,255,0.35)] font-sans">
          {config.overlayUI?.centerText || "Your Repository as a Living Knowledge Universe"}
        </h1>
      </div>

      {/* Bottom middle Panel */}
      <div className="flex flex-col items-center justify-end flex-grow pb-4">
        {/* Primary Call to Action Button */}
        {config.overlayUI?.callToAction && (
          <button
            onClick={() => {
              if (typeof window !== "undefined") {
                alert("Navigating to Software Intelligence Platform Dashboard!");
                window.location.href = config.overlayUI?.callToAction?.href ?? "/dashboard";
              }
            }}
            className="pointer-events-auto px-8 py-3.5 text-sm font-bold uppercase tracking-[0.25em] rounded-full border border-cyan-500/40 bg-cyan-950/20 backdrop-blur-md text-cyan-200 hover:text-white hover:bg-cyan-500/25 shadow-[0_0_15px_rgba(0,229,255,0.15)] hover:shadow-[0_0_25px_rgba(0,229,255,0.4)] hover:scale-105 transition-all duration-300 cursor-pointer animate-fade-in-delayed outline-none"
          >
            {config.overlayUI.callToAction.label}
          </button>
        )}

        {/* Secondary Navigation Options */}
        {config.overlayUI?.navigationOptions && (
          <div className="flex flex-wrap justify-center gap-4 mt-5 pointer-events-auto animate-fade-in-delayed">
            {config.overlayUI.navigationOptions.map((opt) => (
              <button
                key={opt.label}
                onClick={() => {
                  if (typeof window !== "undefined") {
                    window.location.href = opt.href;
                  }
                }}
                className="px-4 py-2 text-xs font-semibold rounded-lg border border-white/10 bg-slate-950/30 backdrop-blur-sm text-slate-400 hover:text-white hover:bg-white/5 hover:border-white/15 transition-all duration-200 cursor-pointer outline-none"
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
