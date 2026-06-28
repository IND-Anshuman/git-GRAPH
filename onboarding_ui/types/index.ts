import { Vector3, Euler } from 'three';

// Scene Types
export type SceneNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

export enum SceneStatus {
  UNLOADED = 'unloaded',
  LOADING = 'loading',
  READY = 'ready',
  ACTIVE = 'active',
}

export enum QualityTier {
  ULTRA = 'ultra',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

// Camera Types
export interface CameraState {
  position: Vector3;
  rotation: Euler;
  fov: number;
  target: Vector3;
}

export interface CameraKeyframe {
  progress: number;
  position: [number, number, number];
  rotation?: [number, number, number];
  fov?: number;
  easing?: 'linear' | 'easeInOut' | 'easeIn' | 'easeOut';
}

export interface CameraRailDefinition {
  sceneNumber: SceneNumber;
  splineType: 'catmullRom' | 'bezier' | 'linear';
  tension?: number;
  keyframes: CameraKeyframe[];
}

// Particle Types
export interface ParticleConfig {
  enabled: boolean;
  count: {
    ultra: number;
    high: number;
    medium: number;
    low: number;
  };
  geometry: ParticleGeometryConfig;
  material: ParticleMaterialConfig;
  behavior: ParticleBehaviorConfig;
  entityTypes?: Record<string, { color: string; size: number; ratio: number }>;
  initialDistribution?: {
    type: string;
    bounds?: [[number, number, number], [number, number, number]];
  };
}

export interface ParticleGeometryConfig {
  type: 'sphere' | 'box' | 'plane' | 'custom';
  size?: number;
  segments?: number;
}

export interface ParticleMaterialConfig {
  color?: string;
  opacity?: number;
  transparent?: boolean;
  emissive?: string;
  emissiveIntensity?: number;
}

export interface ParticleBehaviorConfig {
  animation: 'static' | 'drift' | 'orbit' | 'explosion' | 'cluster' | 'network';
  drift?: {
    velocity: [Vector3, Vector3];
    turbulence: number;
  };
  orbit?: {
    center: [number, number, number];
    radius: [number, number];
    speed: [number, number];
  };
  explosion?: {
    origin: [number, number, number];
    force: [number, number];
    gravity: [number, number, number];
    damping: number;
  };
  cluster?: {
    centers: [number, number, number][];
    attractionStrength: number;
    clusterRadius: number;
  };
  network?: {
    nodes: NetworkNode[];
    connectionThreshold: number;
    flowSpeed: number;
  };
}

export interface NetworkNode {
  id: string;
  position: [number, number, number];
  connections: string[];
}

// Interaction Types
export interface InteractionMetadata {
  type: 'particle' | 'planet' | 'constellation' | 'decision' | 'node';
  title: string;
  description: string;
  details?: Record<string, string | number>;
  actions?: {
    label: string;
    href?: string;
    onClick?: string;
  }[];
}

export interface InteractionHotspot {
  id: string;
  position: [number, number, number];
  radius: number;
  type: 'particle' | 'planet' | 'constellation' | 'decision' | 'node';
  metadata: InteractionMetadata;
}

export interface NetworkNodeData {
  id: string;
  position: [number, number, number];
  type: 'code_reference' | 'test_result' | 'metric' | 'documentation' | 'decision_record';
  confidenceScore: number; // 0.0-1.0
  size: number;
  metadata: InteractionMetadata;
}

export interface NetworkConnectionRules {
  connectionThreshold: number;
  minimumConfidence: number;
  maxConnectionsPerNode: number;
}

export interface GodRaysConfig {
  enabled: boolean;
  sources: [number, number, number][];
  intensity: number;
  decay: number;
  density: number;
  weight: number;
}

export interface UniverseLayerConfig {
  source: string; // Scene ID (e.g., "scene1", "scene2")
  particleCount?: {
    ultra: number;
    high: number;
    medium: number;
    low: number;
  };
  scale?: number;
  opacity?: number;
  animation?: string;
  // Layer-specific flags
  showConnectionLines?: boolean;
  lineOpacity?: number;
  showLabels?: boolean;
  renderPlanets?: boolean;
  glowIntensity?: number;
  renderDomainSuns?: boolean;
  sunScale?: number;
  renderEnergyBeams?: boolean;
  beamOpacity?: number;
  renderOrbitalPaths?: boolean;
  renderRings?: boolean;
  ringOpacity?: number;
  renderDecisionNodes?: boolean;
  nodeScale?: number;
  renderConnections?: boolean;
  connectionOpacity?: number;
  nodeCount?: {
    ultra: number;
    high: number;
    medium: number;
    low: number;
  };
  energyFlowEnabled?: boolean;
}

export interface OverlayUIConfig {
  centerText?: string;
  callToAction?: {
    label: string;
    href: string;
  };
  navigationOptions?: Array<{
    label: string;
    href: string;
  }>;
}

// Scene Configuration Types
export interface SceneConfig {
  sceneNumber: SceneNumber;
  name: string;
  progressRange: [number, number];
  camera: {
    keyframes: CameraKeyframe[];
    lookAtTarget?: 'origin' | [number, number, number];
    fov?: number;
  };
  particles: ParticleConfig;
  interactions: InteractionHotspot[];
  lighting: {
    ambient: { color: string; intensity: number };
    directional?: DirectionalLightConfig[];
    point?: PointLightConfig[];
  };
  postProcessing?: {
    bloom?: BloomConfig;
    depthOfField?: DofConfig;
    ssao?: SSAOConfig;
  };
  audio?: {
    ambient?: string;
    effects?: AudioEffectConfig[];
  };
  text?: {
    title: string;
    subtitle: string;
    description: string;
  };
  constellations?: ConstellationData[];
  planets?: PlanetData[];
  domains?: DomainData[];
  energyBeams?: EnergyBeamData[];
  rings?: DecisionRingData[];
  decisionConnections?: DecisionConnectionData[];
  networkNodes?: NetworkNodeData[];
  connectionRules?: NetworkConnectionRules;
  flowSpeed?: number;
  pulseFrequency?: number;
  pulseColor?: string;
  exampleQuestions?: string[];
  godRays?: GodRaysConfig;
  isCompletionScene?: boolean;
  layers?: UniverseLayerConfig[];
  overlayUI?: OverlayUIConfig;
}

export interface ConstellationData {
  name: string;
  center: [number, number, number];
  entityCount: number;
  color: string;
}

export interface PlanetData {
  id: string;
  name: string;
  position: [number, number, number];
  size: number;
  health: number;
  importance: number;
  entityCount: number;
  linesOfCode: number;
  color: string;
}

export interface DomainData {
  name: string;
  sunPosition: [number, number, number];
  sunSize: number;
  color: string;
  planets: string[]; // Planet IDs
  orbitalRadius: number;
  orbitalSpeed: number;
}

export interface EnergyBeamData {
  fromPlanetId: string;
  toPlanetId: string;
  intensity: number;
  flowSpeed: number;
}

export interface DecisionNodeData {
  id: string;
  anglePosition: number; // radians
  distanceFromCenter: number;
  status: 'accepted' | 'superseded' | 'deprecated';
  metadata: InteractionMetadata;
}

export interface DecisionRingData {
  planetId: string;
  innerRadius: number;
  outerRadius: number;
  rotationSpeed: number;
  rotationAxis: [number, number, number];
  decisionNodes: DecisionNodeData[];
}

export interface DecisionConnectionData {
  fromDecisionId: string;
  toPlanetIds: string[];
  lineStyle: 'solid' | 'dashed' | 'dotted';
}

export interface DirectionalLightConfig {
  color: string;
  intensity: number;
  position: [number, number, number];
}

export interface PointLightConfig {
  color: string;
  intensity: number;
  position: [number, number, number];
  distance?: number;
}

export interface BloomConfig {
  strength: number;
  radius: number;
  threshold: number;
}

export interface DofConfig {
  focusDistance: number;
  focalLength: number;
  bokehScale: number;
}

export interface SSAOConfig {
  samples: number;
  radius: number;
  intensity: number;
}

export interface AudioEffectConfig {
  type: string;
  url: string;
  trigger: string;
}

// Store Types
export interface OnboardingState {
  currentScene: SceneNumber;
  scrollProgress: number;
  qualityTier: QualityTier;
  isAudioEnabled: boolean;
  isReducedMotion: boolean;
  hoveredObject: string | null;
  selectedObject: string | null;
  sceneStatuses: Record<SceneNumber, SceneStatus>;
}

export interface OnboardingActions {
  setCurrentScene: (scene: SceneNumber) => void;
  setScrollProgress: (progress: number) => void;
  setQualityTier: (tier: QualityTier) => void;
  toggleAudio: () => void;
  setReducedMotion: (enabled: boolean) => void;
  setHoveredObject: (id: string | null) => void;
  setSelectedObject: (id: string | null) => void;
  setSceneStatus: (scene: SceneNumber, status: SceneStatus) => void;
}
