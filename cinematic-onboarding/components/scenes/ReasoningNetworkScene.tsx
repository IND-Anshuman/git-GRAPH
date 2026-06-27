"use client";

import { useRef, useEffect, useMemo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { SceneConfig } from "@/types";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { SelectionHighlight } from "../SelectionHighlight";
import { AudioSystem } from "@/lib/AudioSystem";

interface ReasoningNetworkSceneProps {
  active: boolean;
  config: SceneConfig;
}

interface NetworkConnection {
  id: string;
  fromId: string;
  toId: string;
  fromPos: THREE.Vector3;
  toPos: THREE.Vector3;
  length: number;
}

interface EnergyPulse {
  mesh: THREE.Mesh;
  fromPos: THREE.Vector3;
  toPos: THREE.Vector3;
  progress: number;
  speed: number;
}

// 1. Volumetric God Ray Shaft component
interface GodRayShaftProps {
  position: [number, number, number];
  color: string;
  intensity: number;
}

function GodRayShaft({ position, color, intensity }: GodRayShaftProps) {
  const meshRef1 = useRef<THREE.Mesh>(null);
  const meshRef2 = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    if (meshRef1.current) {
      meshRef1.current.rotation.y = time * 0.15;
      meshRef1.current.rotation.x = Math.sin(time * 0.05) * 0.2;
    }
    if (meshRef2.current) {
      meshRef2.current.rotation.y = -time * 0.22;
      meshRef2.current.rotation.z = Math.cos(time * 0.07) * 0.15;
    }
  });

  const glowColor = useMemo(() => new THREE.Color(color), [color]);

  // Volumetric cylinder/cone shader
  const shader = useMemo(() => {
    return {
      uniforms: {
        color: { value: glowColor },
        intensity: { value: intensity },
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vNormal;
        void main() {
          vUv = uv;
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 color;
        uniform float intensity;
        varying vec2 vUv;
        varying vec3 vNormal;
        void main() {
          // Fade out towards the top and bottom of the cylinder
          float verticalFade = sin(vUv.y * 3.14159);
          // Horizontal wrap fade
          float horizontalFade = sin(vUv.x * 3.14159);
          // Volumetric edge fade
          float edgeFade = pow(1.0 - max(0.0, dot(vNormal, vec3(0.0, 0.0, 1.0))), 1.5);
          gl_FragColor = vec4(color, verticalFade * horizontalFade * edgeFade * intensity * 0.15);
        }
      `
    };
  }, [glowColor, intensity]);

  return (
    <group position={position}>
      {/* Dynamic volumetric shafts crossing each other */}
      <mesh ref={meshRef1}>
        <cylinderGeometry args={[0.2, 8.0, 80, 16, 4, true]} />
        <shaderMaterial
          args={[shader]}
          transparent
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          side={THREE.DoubleSide}
        />
      </mesh>
      <mesh ref={meshRef2} rotation={[0, 0, Math.PI / 4]}>
        <cylinderGeometry args={[0.1, 6.0, 60, 16, 4, true]} />
        <shaderMaterial
          args={[shader]}
          transparent
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

// 2. Main Scene Component
export function ReasoningNetworkScene({ active, config }: ReasoningNetworkSceneProps) {
  const { camera } = useThree();
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  const hoveredObjectId = useOnboardingStore((s) => s.hoveredObjectId);
  const focusedObjectId = useOnboardingStore((s) => s.focusedObjectId);
  const expandedCardId = useOnboardingStore((s) => s.expandedCardId);

  // Register evidence nodes with InteractionHandler
  useEffect(() => {
    if (active && config.networkNodes) {
      const handler = InteractionHandler.getInstance();
      config.networkNodes.forEach((node) => {
        handler.registerObject(node.id, node.position, node.size, {
          type: "Evidence Node",
          title: node.metadata.title,
          description: node.metadata.description,
          details: {
            "Evidence Type": node.type,
            "Confidence Score": `${(node.confidenceScore * 100).toFixed(0)}%`
          }
        });
      });

      return () => {
        config.networkNodes?.forEach((node) => {
          handler.unregisterObject(node.id);
        });
      };
    }
  }, [active, config.networkNodes]);

  const groupRef = useRef<THREE.Group>(null);
  const pulsesGroupRef = useRef<THREE.Group>(null);
  const connectionLinesRef = useRef<{ [pairId: string]: THREE.Line }>({});

  const pulsesRef = useRef<EnergyPulse[]>([]);
  const highlightedConnsRef = useRef<{ [id: string]: number }>({}); // connId -> timer
  const activeQuestionsRef = useRef<Array<{ id: string; sprite: THREE.Sprite; text: string; spawnTime: number }>>([]);

  const pulseGeometry = useMemo(() => new THREE.SphereGeometry(0.4, 8, 8), []);
  const pulseMaterial = useMemo(() => new THREE.MeshBasicMaterial({
    color: new THREE.Color(config.pulseColor ?? "#00E5FF"),
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending
  }), [config.pulseColor]);

  // Node Color coding helper
  const getNodeColor = (type: string): string => {
    switch (type) {
      case "code_reference":
        return "#2196F3"; // Blue
      case "test_result":
        return "#4CAF50"; // Green
      case "metric":
        return "#FF9800"; // Orange
      case "documentation":
        return "#9C27B0"; // Purple
      case "decision_record":
        return "#00BCD4"; // Cyan
      default:
        return "#ffffff";
    }
  };

  // 1. Memoize node connections based on rules
  const connections = useMemo(() => {
    const list: NetworkConnection[] = [];
    const nodesData = config.networkNodes || [];
    const threshold = config.connectionRules?.connectionThreshold ?? 35;
    const minConf = config.connectionRules?.minimumConfidence ?? 0.6;
    const maxConn = config.connectionRules?.maxConnectionsPerNode ?? 8;

    const connectedPairs = new Set<string>();

    nodesData.forEach((nodeI) => {
      if (nodeI.confidenceScore < minConf) return;

      const posI = new THREE.Vector3(...nodeI.position);

      const potentials = nodesData
        .filter((nodeJ) => nodeJ.id !== nodeI.id && nodeJ.confidenceScore >= minConf)
        .map((nodeJ) => {
          const posJ = new THREE.Vector3(...nodeJ.position);
          const dist = posI.distanceTo(posJ);
          return { nodeJ, dist, posJ };
        })
        .filter((p) => p.dist < threshold);

      // Sort by closest distance
      potentials.sort((a, b) => a.dist - b.dist);

      let count = 0;
      for (const p of potentials) {
        if (count >= maxConn) break;

        const pairId = [nodeI.id, p.nodeJ.id].sort().join("-");
        if (!connectedPairs.has(pairId)) {
          connectedPairs.add(pairId);
          list.push({
            id: pairId,
            fromId: nodeI.id,
            toId: p.nodeJ.id,
            fromPos: posI,
            toPos: p.posJ,
            length: p.dist
          });
        }
        count++;
      }
    });

    return list;
  }, [config.networkNodes, config.connectionRules]);

  // 2. Build Adjacency List for BFS Pathfinding
  const adjacencyList = useMemo(() => {
    const adj = new Map<string, string[]>();
    connections.forEach((conn) => {
      if (!adj.has(conn.fromId)) adj.set(conn.fromId, []);
      if (!adj.has(conn.toId)) adj.set(conn.toId, []);
      adj.get(conn.fromId)!.push(conn.toId);
      adj.get(conn.toId)!.push(conn.fromId);
    });
    return adj;
  }, [connections]);

  // 3. BFS Path Tracer
  const tracePath = (startId: string, endId: string): string[] | null => {
    if (startId === endId) return [startId];
    const queue: string[][] = [[startId]];
    const visited = new Set<string>([startId]);

    while (queue.length > 0) {
      const path = queue.shift()!;
      const lastNode = path[path.length - 1];

      const neighbors = adjacencyList.get(lastNode) || [];
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          const newPath = [...path, neighbor];
          if (neighbor === endId) return newPath;
          queue.push(newPath);
        }
      }
    }
    return null;
  };

  // 4. Highlight path of connections
  const highlightPath = (nodeIds: string[]) => {
    for (let k = 0; k < nodeIds.length - 1; k++) {
      const pairId = [nodeIds[k], nodeIds[k + 1]].sort().join("-");
      highlightedConnsRef.current[pairId] = 2.5; // highlight for 2.5 seconds
    }
  };

  // 5. Create Floating Text Billboards
  const createQuestionSprite = (text: string): THREE.Sprite => {
    const canvas = document.createElement("canvas");
    canvas.width = 1024;
    canvas.height = 256;
    const ctx = canvas.getContext("2d")!;

    // Background capsule shape
    ctx.fillStyle = "rgba(10, 15, 30, 0.85)";
    ctx.strokeStyle = "rgba(0, 229, 255, 0.4)";
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.roundRect(10, 10, 1004, 236, 118);
    ctx.fill();
    ctx.stroke();

    // Subtle inner cyan drop shadow glow
    ctx.shadowColor = "rgba(0, 229, 255, 0.5)";
    ctx.shadowBlur = 15;

    // Draw text
    ctx.font = "bold 44px Outfit, Inter, sans-serif";
    ctx.fillStyle = "#FFFFFF";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, 512, 128);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      opacity: 0.0, // starts invisible, fades in
      depthWrite: false
    });

    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(38, 9.5, 1);
    return sprite;
  };

  // 6. Spawn Question Sprites & Highlight Path triggers
  useEffect(() => {
    if (!active || !config.exampleQuestions || config.exampleQuestions.length === 0) return;

    const questions = config.exampleQuestions;
    const nodesData = config.networkNodes || [];
    const highConfNodes = nodesData.filter((n) => n.confidenceScore > 0.85);

    if (highConfNodes.length === 0) return;

    // Distribute question positions around high-confidence nodes
    const activeList: typeof activeQuestionsRef.current = [];
    questions.forEach((q, idx) => {
      const targetNode = highConfNodes[idx % highConfNodes.length];
      const sprite = createQuestionSprite(q);

      // Offset position around node
      const angle = (idx / questions.length) * Math.PI * 2;
      const offsetRadius = 24.0;
      sprite.position.set(
        targetNode.position[0] + Math.cos(angle) * offsetRadius,
        targetNode.position[1] + randomRange(-8, 8),
        targetNode.position[2] + Math.sin(angle) * offsetRadius
      );

      groupRef.current?.add(sprite);
      activeList.push({
        id: `q-${idx}`,
        sprite,
        text: q,
        spawnTime: idx * 2.0 // Staggered spawn timings
      });
    });

    activeQuestionsRef.current = activeList;

    // Pulse Timer to spawn sparks
    const pulseInterval = setInterval(() => {
      if (!shouldAnimate || connections.length === 0) return;

      const numPulses = qualityTier === "low" ? 1 : qualityTier === "medium" ? 2 : 4;
      for (let p = 0; p < numPulses; p++) {
        if (pulsesRef.current.length >= 35) continue; // safety cap

        const randomConn = connections[Math.floor(Math.random() * connections.length)];
        const pulseMesh = new THREE.Mesh(pulseGeometry, pulseMaterial);
        pulseMesh.position.copy(randomConn.fromPos);
        pulsesGroupRef.current?.add(pulseMesh);

        if (p === 0) {
          // Synthesize spatial audio ping at the pulse starting position
          AudioSystem.getInstance().playSpatialPulse(randomConn.fromPos);
        }

        pulsesRef.current.push({
          mesh: pulseMesh,
          fromPos: randomConn.fromPos,
          toPos: randomConn.toPos,
          progress: 0.0,
          speed: (config.flowSpeed ?? 2.0) * (0.8 + Math.random() * 0.4)
        });
      }
    }, 1500 * (config.pulseFrequency ?? 0.6));

    // Pathfinding reasoning trigger (every 4 seconds, highlight reasoning path to random question)
    const pathTimer = setInterval(() => {
      if (activeQuestionsRef.current.length === 0 || highConfNodes.length === 0) return;

      const activeQs = activeQuestionsRef.current.filter(q => q.sprite.material.opacity > 0.5);
      if (activeQs.length === 0) return;

      const randQ = activeQs[Math.floor(Math.random() * activeQs.length)];
      // Find closest node to question position
      const qPos = randQ.sprite.position;
      let closestNode = nodesData[0];
      let minDist = Infinity;
      nodesData.forEach((node) => {
        const nPos = new THREE.Vector3(...node.position);
        const dist = qPos.distanceTo(nPos);
        if (dist < minDist) {
          minDist = dist;
          closestNode = node;
        }
      });

      // Find random answer source (high-confidence node)
      const randAnswer = highConfNodes[Math.floor(Math.random() * highConfNodes.length)];
      const pathNodes = tracePath(closestNode.id, randAnswer.id);
      if (pathNodes && pathNodes.length > 1) {
        highlightPath(pathNodes);
      }
    }, 4000);

    return () => {
      clearInterval(pulseInterval);
      clearInterval(pathTimer);
      // Clean up sprites
      activeList.forEach((q) => {
        groupRef.current?.remove(q.sprite);
        if (q.sprite.material.map) q.sprite.material.map.dispose();
        q.sprite.material.dispose();
      });
      activeQuestionsRef.current = [];

      // Clean up pulses
      pulsesRef.current.forEach((pulse) => {
        pulsesGroupRef.current?.remove(pulse.mesh);
      });
      pulsesRef.current = [];
    };
  }, [active, config.exampleQuestions, connections, qualityTier]);

  // helper random generator
  const randomRange = (min: number, max: number) => Math.random() * (max - min) + min;

  // 7. Render Loop Animations
  useFrame((state, delta) => {
    if (!active) return;

    const time = state.clock.getElapsedTime();

    // A. Animate Connection Line Highlight Fading
    Object.keys(connectionLinesRef.current).forEach((pairId) => {
      const line = connectionLinesRef.current[pairId];
      if (!line) return;

      let targetOpacity = 0.25; // Base subtle connection line opacity
      if (highlightedConnsRef.current[pairId] !== undefined) {
        highlightedConnsRef.current[pairId] -= delta;
        if (highlightedConnsRef.current[pairId] <= 0) {
          delete highlightedConnsRef.current[pairId];
        } else {
          targetOpacity = 0.85; // High visibility reasoning chain opacity
        }
      }

      if (line.material instanceof THREE.LineBasicMaterial) {
        line.material.opacity = THREE.MathUtils.lerp(
          line.material.opacity,
          targetOpacity,
          0.1
        );
      }
    });

    // B. Animate Energy Sparks
    if (shouldAnimate) {
      const remainingPulses: EnergyPulse[] = [];

      pulsesRef.current.forEach((pulse) => {
        pulse.progress += delta * pulse.speed * 0.15;
        if (pulse.progress >= 1.0) {
          pulsesGroupRef.current?.remove(pulse.mesh);
        } else {
          const currentPos = new THREE.Vector3().lerpVectors(
            pulse.fromPos,
            pulse.toPos,
            pulse.progress
          );
          pulse.mesh.position.copy(currentPos);

          // Pulse scale peaks in middle
          const scale = 0.5 + Math.sin(pulse.progress * Math.PI) * 0.7;
          pulse.mesh.scale.setScalar(scale);

          remainingPulses.push(pulse);
        }
      });

      pulsesRef.current = remainingPulses;
    }

    // C. Floating Questions sequential fade & gentle drift
    activeQuestionsRef.current.forEach((q) => {
      // Fade in after their designated spawn delay
      if (time >= q.spawnTime) {
        q.sprite.material.opacity = THREE.MathUtils.lerp(
          q.sprite.material.opacity,
          1.0,
          0.05
        );
      }

      // Gentle floating motion
      if (shouldAnimate) {
        q.sprite.position.y += Math.sin(time * 0.8 + q.sprite.id) * 0.015;
      }
    });

    // D. Billboard scale corrections based on camera distance (LOD readability)
    if (camera) {
      activeQuestionsRef.current.forEach((q) => {
        const dist = camera.position.distanceTo(q.sprite.position);
        // Rescale sprites slightly based on distance to keep text readable
        const targetScale = THREE.MathUtils.clamp(dist * 0.28, 18, 55);
        q.sprite.scale.set(targetScale, targetScale * 0.25, 1);
      });
    }
  });

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
          decay={2}
        />
      ))}

      {/* Render Node connections */}
      {connections.map((conn) => (
        <line
          key={conn.id}
          ref={(el) => {
            if (el) {
              connectionLinesRef.current[conn.id] = el as any;
            }
          }}
          {...{
            geometry: new THREE.BufferGeometry().setFromPoints([conn.fromPos, conn.toPos])
          } as any}
        >
          <lineBasicMaterial
            color={config.pulseColor ?? "#00E5FF"}
            transparent
            opacity={0.25}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
          />
        </line>
      ))}

      {/* Sparks Group */}
      <group ref={pulsesGroupRef} />

      {/* Volumetric Simulated God Rays */}
      {qualityTier !== "low" &&
        config.godRays?.enabled &&
        config.godRays.sources.map((src, i) => (
          <GodRayShaft
            key={`godray-${i}`}
            position={src}
            color={config.pulseColor ?? "#00E5FF"}
            intensity={config.godRays?.intensity ?? 0.8}
          />
        ))}

      {/* Render Evidence Nodes */}
      {config.networkNodes?.map((node, idx) => {
        const colorHex = getNodeColor(node.type);
        const colorObj = new THREE.Color(colorHex);

        return (
          <group key={node.id}>
            {/* Selection Highlight */}
            <SelectionHighlight
              position={node.position}
              radius={node.size}
              hovered={hoveredObjectId === node.id || focusedObjectId === node.id}
              selected={expandedCardId === node.id}
              color={colorHex}
            />

            {/* Standard Mesh Node */}
            <mesh
              position={node.position}
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
              <sphereGeometry args={[node.size, 16, 16]} />
              <meshStandardMaterial
                color={colorObj}
                emissive={colorObj}
                emissiveIntensity={0.35 + node.confidenceScore * 0.65}
                metalness={0.4}
                roughness={0.5}
              />
            </mesh>

            {/* High confidence Outer Aura Glow */}
            {node.confidenceScore > 0.8 && qualityTier !== "low" && (
              <mesh position={node.position}>
                <sphereGeometry args={[node.size * 1.5, 16, 16]} />
                <shaderMaterial
                  uniforms={{
                    c: { value: 0.35 + Math.sin(idx) * 0.05 },
                    p: { value: 3.8 },
                    glowColor: { value: colorObj },
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
      })}
    </group>
  );
}
