// Task 1.9: Config Parser - Parses, validates, and serializes scene configurations

import { z } from "zod";
import * as THREE from "three";
import { SceneConfig, SceneNumber } from "@/types";

// Zod schema for JSON validation (with raw coordinate tuples)
const CameraKeyframeJSONSchema = z.object({
  progress: z.number(),
  position: z.tuple([z.number(), z.number(), z.number()]),
  rotation: z.tuple([z.number(), z.number(), z.number()]).optional(),
  fov: z.number().optional(),
  easing: z.enum(["linear", "easeInOut", "easeIn", "easeOut"]).optional(),
});

const CameraConfigJSONSchema = z.object({
  keyframes: z.array(CameraKeyframeJSONSchema),
  lookAtTarget: z.union([
    z.literal("origin"),
    z.tuple([z.number(), z.number(), z.number()]),
  ]).optional(),
  fov: z.number().optional(),
});

const ParticleCountJSONSchema = z.object({
  ultra: z.number(),
  high: z.number(),
  medium: z.number(),
  low: z.number(),
});

const ParticleGeometryJSONSchema = z.object({
  type: z.enum(["sphere", "box", "plane", "custom"]),
  size: z.number().optional(),
  segments: z.number().optional(),
});

const ParticleMaterialJSONSchema = z.object({
  color: z.string().optional(),
  opacity: z.number().optional(),
  transparent: z.boolean().optional(),
  emissive: z.string().optional(),
  emissiveIntensity: z.number().optional(),
});

const NetworkNodeJSONSchema = z.object({
  id: z.string(),
  position: z.tuple([z.number(), z.number(), z.number()]),
  connections: z.array(z.string()),
});

const ParticleBehaviorJSONSchema = z.object({
  animation: z.enum(["static", "drift", "orbit", "explosion", "cluster", "network"]),
  drift: z.object({
    velocity: z.tuple([
      z.tuple([z.number(), z.number(), z.number()]),
      z.tuple([z.number(), z.number(), z.number()]),
    ]),
    turbulence: z.number(),
  }).optional(),
  orbit: z.object({
    center: z.tuple([z.number(), z.number(), z.number()]),
    radius: z.tuple([z.number(), z.number()]),
    speed: z.tuple([z.number(), z.number()]),
  }).optional(),
  explosion: z.object({
    origin: z.tuple([z.number(), z.number(), z.number()]),
    force: z.tuple([z.number(), z.number()]),
    gravity: z.tuple([z.number(), z.number(), z.number()]),
    damping: z.number(),
  }).optional(),
  cluster: z.object({
    centers: z.array(z.tuple([z.number(), z.number(), z.number()])),
    attractionStrength: z.number(),
    clusterRadius: z.number(),
  }).optional(),
  network: z.object({
    nodes: z.array(NetworkNodeJSONSchema),
    connectionThreshold: z.number(),
    flowSpeed: z.number(),
  }).optional(),
});

const InteractionMetadataJSONSchema = z.object({
  type: z.enum(["particle", "planet", "constellation", "decision", "node"]),
  title: z.string(),
  description: z.string(),
  details: z.record(z.string(), z.union([z.string(), z.number()])).optional(),
  actions: z.array(z.object({
    label: z.string(),
    href: z.string().optional(),
    onClick: z.string().optional(),
  })).optional(),
});

const InteractionHotspotJSONSchema = z.object({
  id: z.string(),
  position: z.tuple([z.number(), z.number(), z.number()]),
  radius: z.number(),
  type: z.enum(["particle", "planet", "constellation", "decision", "node"]),
  metadata: InteractionMetadataJSONSchema,
});

const DirectionalLightJSONSchema = z.object({
  color: z.string(),
  intensity: z.number(),
  position: z.tuple([z.number(), z.number(), z.number()]),
});

const PointLightJSONSchema = z.object({
  color: z.string(),
  intensity: z.number(),
  position: z.tuple([z.number(), z.number(), z.number()]),
  distance: z.number().optional(),
});

const LightingJSONSchema = z.object({
  ambient: z.object({
    color: z.string(),
    intensity: z.number(),
  }),
  directional: z.array(DirectionalLightJSONSchema).optional(),
  point: z.array(PointLightJSONSchema).optional(),
});

const BloomJSONSchema = z.object({
  strength: z.number(),
  radius: z.number(),
  threshold: z.number(),
});

const DofJSONSchema = z.object({
  focusDistance: z.number(),
  focalLength: z.number(),
  bokehScale: z.number(),
});

const SSAOJSONSchema = z.object({
  samples: z.number(),
  radius: z.number(),
  intensity: z.number(),
});

const PostProcessingJSONSchema = z.object({
  bloom: BloomJSONSchema.optional(),
  depthOfField: DofJSONSchema.optional(),
  ssao: SSAOJSONSchema.optional(),
});

const ConstellationJSONSchema = z.object({
  name: z.string(),
  center: z.tuple([z.number(), z.number(), z.number()]),
  entityCount: z.number(),
  color: z.string(),
});

const PlanetJSONSchema = z.object({
  id: z.string(),
  name: z.string(),
  position: z.tuple([z.number(), z.number(), z.number()]),
  size: z.number().positive(),
  health: z.number().min(0).max(1),
  importance: z.number().min(0).max(1),
  entityCount: z.number(),
  linesOfCode: z.number(),
  color: z.string(),
});

const AudioEffectJSONSchema = z.object({
  type: z.string(),
  url: z.string(),
  trigger: z.string(),
});

const AudioJSONSchema = z.object({
  ambient: z.string().optional(),
  effects: z.array(AudioEffectJSONSchema).optional(),
});

const DomainJSONSchema = z.object({
  name: z.string(),
  sunPosition: z.tuple([z.number(), z.number(), z.number()]),
  sunSize: z.number().positive(),
  color: z.string(),
  planets: z.array(z.string()),
  orbitalRadius: z.number().positive(),
  orbitalSpeed: z.number(),
});

const EnergyBeamJSONSchema = z.object({
  fromPlanetId: z.string(),
  toPlanetId: z.string(),
  intensity: z.number().min(0).max(1),
  flowSpeed: z.number(),
});

const DecisionNodeJSONSchema = z.object({
  id: z.string(),
  anglePosition: z.number(),
  distanceFromCenter: z.number().positive(),
  status: z.enum(['accepted', 'superseded', 'deprecated']),
  metadata: InteractionMetadataJSONSchema,
});

const DecisionRingJSONSchema = z.object({
  planetId: z.string(),
  innerRadius: z.number().positive(),
  outerRadius: z.number().positive(),
  rotationSpeed: z.number(),
  rotationAxis: z.tuple([z.number(), z.number(), z.number()]),
  decisionNodes: z.array(DecisionNodeJSONSchema),
});

const DecisionConnectionJSONSchema = z.object({
  fromDecisionId: z.string(),
  toPlanetIds: z.array(z.string()),
  lineStyle: z.enum(['solid', 'dashed', 'dotted']),
});

const NetworkNodeDataJSONSchema = z.object({
  id: z.string(),
  position: z.tuple([z.number(), z.number(), z.number()]),
  type: z.enum(['code_reference', 'test_result', 'metric', 'documentation', 'decision_record']),
  confidenceScore: z.number().min(0).max(1),
  size: z.number().positive(),
  metadata: InteractionMetadataJSONSchema,
});

const NetworkConnectionRulesJSONSchema = z.object({
  connectionThreshold: z.number().positive(),
  minimumConfidence: z.number().min(0).max(1),
  maxConnectionsPerNode: z.number().int().positive(),
});

const GodRaysConfigJSONSchema = z.object({
  enabled: z.boolean(),
  sources: z.array(z.tuple([z.number(), z.number(), z.number()])),
  intensity: z.number(),
  decay: z.number(),
  density: z.number(),
  weight: z.number(),
});

const UniverseLayerConfigJSONSchema = z.object({
  source: z.string(),
  particleCount: ParticleCountJSONSchema.optional(),
  scale: z.number().optional(),
  opacity: z.number().optional(),
  animation: z.string().optional(),
  showConnectionLines: z.boolean().optional(),
  lineOpacity: z.number().optional(),
  showLabels: z.boolean().optional(),
  renderPlanets: z.boolean().optional(),
  glowIntensity: z.number().optional(),
  renderDomainSuns: z.boolean().optional(),
  sunScale: z.number().optional(),
  renderEnergyBeams: z.boolean().optional(),
  beamOpacity: z.number().optional(),
  renderOrbitalPaths: z.boolean().optional(),
  renderRings: z.boolean().optional(),
  ringOpacity: z.number().optional(),
  renderDecisionNodes: z.boolean().optional(),
  nodeScale: z.number().optional(),
  renderConnections: z.boolean().optional(),
  connectionOpacity: z.number().optional(),
  nodeCount: ParticleCountJSONSchema.optional(),
  energyFlowEnabled: z.boolean().optional(),
});

const OverlayUIConfigJSONSchema = z.object({
  centerText: z.string().optional(),
  callToAction: z.object({
    label: z.string(),
    href: z.string(),
  }).optional(),
  navigationOptions: z.array(z.object({
    label: z.string(),
    href: z.string(),
  })).optional(),
});

const SceneConfigJSONSchema = z.object({
  sceneNumber: z.union([
    z.literal(1), z.literal(2), z.literal(3), z.literal(4),
    z.literal(5), z.literal(6), z.literal(7), z.literal(8)
  ]),
  name: z.string(),
  progressRange: z.tuple([z.number(), z.number()]),
  camera: CameraConfigJSONSchema,
  particles: z.object({
    enabled: z.boolean(),
    count: ParticleCountJSONSchema,
    geometry: ParticleGeometryJSONSchema,
    material: ParticleMaterialJSONSchema,
    behavior: ParticleBehaviorJSONSchema,
    entityTypes: z.record(
      z.string(),
      z.object({
        color: z.string(),
        size: z.number(),
        ratio: z.number(),
      })
    ).optional(),
    initialDistribution: z.object({
      type: z.string(),
      bounds: z.tuple([
        z.tuple([z.number(), z.number(), z.number()]),
        z.tuple([z.number(), z.number(), z.number()]),
      ]).optional(),
    }).optional(),
  }),
  interactions: z.array(InteractionHotspotJSONSchema),
  lighting: LightingJSONSchema,
  postProcessing: PostProcessingJSONSchema.optional(),
  audio: AudioJSONSchema.optional(),
  text: z.object({
    title: z.string(),
    subtitle: z.string(),
    description: z.string(),
  }).optional(),
  constellations: z.array(ConstellationJSONSchema).optional(),
  planets: z.array(PlanetJSONSchema).optional(),
  domains: z.array(DomainJSONSchema).optional(),
  energyBeams: z.array(EnergyBeamJSONSchema).optional(),
  rings: z.array(DecisionRingJSONSchema).optional(),
  decisionConnections: z.array(DecisionConnectionJSONSchema).optional(),
  networkNodes: z.array(NetworkNodeDataJSONSchema).optional(),
  connectionRules: NetworkConnectionRulesJSONSchema.optional(),
  flowSpeed: z.number().optional(),
  pulseFrequency: z.number().optional(),
  pulseColor: z.string().optional(),
  exampleQuestions: z.array(z.string()).optional(),
  godRays: GodRaysConfigJSONSchema.optional(),
  isCompletionScene: z.boolean().optional(),
  layers: z.array(UniverseLayerConfigJSONSchema).optional(),
  overlayUI: OverlayUIConfigJSONSchema.optional(),
});

/**
 * Parses and validates a JSON string into a SceneConfig object.
 * Maps raw JSON arrays to THREE.Vector3 objects where necessary to
 * comply with strict type definitions.
 * 
 * @param json The JSON string to parse.
 * @returns The parsed and validated SceneConfig.
 * @throws Error if JSON is invalid or does not match the schema.
 */
export function parseSceneConfig(json: string): SceneConfig {
  let parsed: any;
  try {
    parsed = JSON.parse(json);
  } catch (e: any) {
    throw new Error(`Invalid JSON format: ${e.message}`);
  }

  const result = SceneConfigJSONSchema.safeParse(parsed);
  if (!result.success) {
    const errorDetails = result.error.issues
      .map((issue) => {
        const pathStr = issue.path.length > 0 ? issue.path.join(".") : "root";
        return `[${pathStr}]: ${issue.message}`;
      })
      .join("\n");
    throw new Error(`Config validation failed:\n${errorDetails}`);
  }

  const data = result.data;

  // Map the JSON structure to the strict TypeScript interface which expects THREE.Vector3
  const sceneConfig: SceneConfig = {
    sceneNumber: data.sceneNumber as SceneNumber,
    name: data.name,
    progressRange: data.progressRange,
    camera: {
      keyframes: data.camera.keyframes.map((kf) => ({
        progress: kf.progress,
        position: kf.position,
        rotation: kf.rotation,
        fov: kf.fov,
        easing: kf.easing,
      })),
      lookAtTarget: data.camera.lookAtTarget,
      fov: data.camera.fov,
    },
    particles: {
      enabled: data.particles.enabled,
      count: data.particles.count,
      geometry: data.particles.geometry,
      material: data.particles.material,
      behavior: {
        animation: data.particles.behavior.animation,
        drift: data.particles.behavior.drift
          ? {
              velocity: [
                new THREE.Vector3().fromArray(data.particles.behavior.drift.velocity[0]),
                new THREE.Vector3().fromArray(data.particles.behavior.drift.velocity[1]),
              ],
              turbulence: data.particles.behavior.drift.turbulence,
            }
          : undefined,
        orbit: data.particles.behavior.orbit,
        explosion: data.particles.behavior.explosion,
        cluster: data.particles.behavior.cluster,
        network: data.particles.behavior.network,
      },
      entityTypes: data.particles.entityTypes,
      initialDistribution: data.particles.initialDistribution,
    },
    interactions: data.interactions,
    lighting: data.lighting,
    postProcessing: data.postProcessing,
    audio: data.audio,
    text: data.text,
    constellations: data.constellations,
    planets: data.planets,
    domains: data.domains,
    energyBeams: data.energyBeams,
    rings: data.rings,
    decisionConnections: data.decisionConnections,
    networkNodes: data.networkNodes,
    connectionRules: data.connectionRules,
    flowSpeed: data.flowSpeed,
    pulseFrequency: data.pulseFrequency,
    pulseColor: data.pulseColor,
    exampleQuestions: data.exampleQuestions,
    godRays: data.godRays,
    isCompletionScene: data.isCompletionScene,
    layers: data.layers,
    overlayUI: data.overlayUI,
  };

  return sceneConfig;
}

/**
 * Serializes a SceneConfig back to a pretty-printed JSON string,
 * preserving precision and converting THREE.Vector3 back to raw arrays.
 * 
 * @param config The SceneConfig to serialize.
 * @returns The pretty-printed JSON string.
 */
export function prettyPrintConfig(config: SceneConfig): string {
  // Convert THREE.Vector3 back to array representation for serialization
  const jsonObject = {
    ...config,
    particles: {
      ...config.particles,
      behavior: {
        ...config.particles.behavior,
        drift: config.particles.behavior.drift
          ? {
              velocity: [
                config.particles.behavior.drift.velocity[0].toArray(),
                config.particles.behavior.drift.velocity[1].toArray(),
              ],
              turbulence: config.particles.behavior.drift.turbulence,
            }
          : undefined,
      },
    },
  };

  return JSON.stringify(jsonObject, null, 2);
}
