// Task 3.1: Particle System Engine - Foundational GPU-accelerated particle renderer using THREE.InstancedMesh

import * as THREE from "three";
import { ParticleConfig, QualityTier } from "@/types";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { particleShaders } from "../shaders/particleShaders";

export interface ParticleGroup {
  id: string;
  count: number;
  config: ParticleConfig;
  animationState: "idle" | "playing" | "paused";
  lodMeshes: {
    sphere: THREE.InstancedMesh;
    quad: THREE.InstancedMesh;
    point: THREE.InstancedMesh;
  };
  container: THREE.Group;
  material: THREE.ShaderMaterial;
}

export type ParticleUpdateFn = (
  index: number,
  matrix: THREE.Matrix4,
  color: THREE.Color
) => void;

/**
 * ParticleSystemEngine class orchestrates particle rendering,
 * generating random shapes, mapping quality tiers, and binding GPU shaders.
 */
export class ParticleSystemEngine {
  private static instance: ParticleSystemEngine | null = null;
  private groups: Map<string, ParticleGroup> = new Map();
  private dummy: THREE.Object3D = new THREE.Object3D();

  private constructor() {}

  /**
   * Returns the singleton instance of ParticleSystemEngine.
   */
  static getInstance(): ParticleSystemEngine {
    if (!ParticleSystemEngine.instance) {
      ParticleSystemEngine.instance = new ParticleSystemEngine();
    }
    return ParticleSystemEngine.instance;
  }

  /**
   * Creates a GPU-accelerated particle group with LOD meshes and customized shaders.
   */
  createParticles(id: string, config: ParticleConfig): ParticleGroup {
    if (this.groups.has(id)) {
      console.warn(`[ParticleSystemEngine] Group ${id} already exists. Returning existing.`);
      return this.groups.get(id)!;
    }

    const store = useOnboardingStore.getState();
    const qualityTier = store.qualityTier;
    const count = config.count[qualityTier];

    // 1. Setup custom shader material
    const animType = config.behavior.animation;
    const shaderKey = animType === "static" ? "drift" : animType;
    const shader = particleShaders[shaderKey] || particleShaders.drift;

    const uniforms = {
      uTime: { value: 0 },
      uTurbulence: { value: config.behavior.drift?.turbulence ?? 1.5 },
      uWindDirection: { value: new THREE.Vector3(0.5, 0.2, 0.1) },
      uCenter: { value: new THREE.Vector3(0, 0, 0) },
      uRadius: { value: 10.0 },
      uSpeed: { value: 0.5 },
      uOrigin: { value: new THREE.Vector3(0, 0, 0) },
      uForce: { value: 2.0 },
      uGravity: { value: new THREE.Vector3(0, -1.0, 0) },
      uDamping: { value: 0.1 },
      uClusterCenters: { 
        value: Array.from({ length: 10 }, () => new THREE.Vector3(
          (Math.random() - 0.5) * 15,
          (Math.random() - 0.5) * 15,
          (Math.random() - 0.5) * 15
        ))
      },
      uAttractionStrength: { value: 0.5 },
      uFlowSpeed: { value: 0.8 },
      uSize: { value: config.geometry.size ?? 0.8 },
    };

    const material = new THREE.ShaderMaterial({
      vertexShader: shader.vertex,
      fragmentShader: shader.fragment,
      uniforms: uniforms,
      transparent: config.material.transparent ?? true,
      opacity: config.material.opacity ?? 0.8,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      vertexColors: true,
    });

    // 2. Build LOD geometries
    const size = (config.geometry.size ?? 0.5) * 6.0;
    
    // LOD 0: Sphere Geometry
    const sphereGeom = new THREE.IcosahedronGeometry(size, 1);
    const sphereBillboard = new Float32Array(sphereGeom.attributes.position.count).fill(0.0);
    sphereGeom.setAttribute("aIsBillboard", new THREE.BufferAttribute(sphereBillboard, 1));
    
    // LOD 1: Billboard Plane Geometry
    const quadGeom = new THREE.PlaneGeometry(size * 1.5, size * 1.5);
    const quadBillboard = new Float32Array(quadGeom.attributes.position.count).fill(1.0);
    quadGeom.setAttribute("aIsBillboard", new THREE.BufferAttribute(quadBillboard, 1));
    
    // LOD 2: Minimal Point Representation (using tiny plane to stay compatible)
    const pointGeom = new THREE.PlaneGeometry(size * 0.5, size * 0.5);
    const pointBillboard = new Float32Array(pointGeom.attributes.position.count).fill(1.0);
    pointGeom.setAttribute("aIsBillboard", new THREE.BufferAttribute(pointBillboard, 1));

    // 3. Create attribute structures
    const initialPositions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const phases = new Float32Array(count);
    const orbitPhases = new Float32Array(count);
    const directions = new Float32Array(count * 3);
    const speeds = new Float32Array(count);
    const clusterIndices = new Float32Array(count);
    const startPositions = new Float32Array(count * 3);
    const endPositions = new Float32Array(count * 3);
    const flowOffsets = new Float32Array(count);

    const distConfig = config.initialDistribution || { type: config.geometry.type, size: 50.0 };
    const positions = this.generatePositions(distConfig, count);
    
    for (let i = 0; i < count; i++) {
      const p = positions[i];
      initialPositions[i * 3] = p.x;
      initialPositions[i * 3 + 1] = p.y;
      initialPositions[i * 3 + 2] = p.z;

      // Random drift velocity
      velocities[i * 3] = (Math.random() - 0.5) * 1.5;
      velocities[i * 3 + 1] = (Math.random() - 0.5) * 1.5;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * 1.5;

      // Noise phase offset
      phases[i] = Math.random() * 200.0;

      // Orbit phase angle
      orbitPhases[i] = Math.random() * Math.PI * 2.0;

      // Explosion outward vectors
      let dir = new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize();
      if (distConfig.type === "double_helix") {
        // Cylindrical radial outward vector (pushing out from Y axis)
        dir.set(p.x, 0.0, p.z).normalize();
        // Add a slight vertical drift dispersion
        dir.y = (Math.random() - 0.5) * 0.35;
        dir.normalize();
      }
      directions[i * 3] = dir.x;
      directions[i * 3 + 1] = dir.y;
      directions[i * 3 + 2] = dir.z;
      speeds[i] = Math.random() * 4.0 + 1.5;

      // Cluster allocation index
      clusterIndices[i] = Math.floor(Math.random() * 10);

      // Network connection nodes
      startPositions[i * 3] = p.x;
      startPositions[i * 3 + 1] = p.y;
      startPositions[i * 3 + 2] = p.z;

      const offsetP = p.clone().add(new THREE.Vector3(
        (Math.random() - 0.5) * 12.0,
        (Math.random() - 0.5) * 12.0,
        (Math.random() - 0.5) * 12.0
      ));
      endPositions[i * 3] = offsetP.x;
      endPositions[i * 3 + 1] = offsetP.y;
      endPositions[i * 3 + 2] = offsetP.z;

      flowOffsets[i] = Math.random();
    }

    // Attach attributes to geometries
    const geometries = [sphereGeom, quadGeom, pointGeom];
    geometries.forEach((geom) => {
      geom.setAttribute("aInitialPosition", new THREE.InstancedBufferAttribute(initialPositions, 3));
      geom.setAttribute("aVelocity", new THREE.InstancedBufferAttribute(velocities, 3));
      geom.setAttribute("aPhase", new THREE.InstancedBufferAttribute(phases, 1));
      geom.setAttribute("aOrbitPhase", new THREE.InstancedBufferAttribute(orbitPhases, 1));
      geom.setAttribute("aDirection", new THREE.InstancedBufferAttribute(directions, 3));
      geom.setAttribute("aSpeed", new THREE.InstancedBufferAttribute(speeds, 1));
      geom.setAttribute("aClusterIndex", new THREE.InstancedBufferAttribute(clusterIndices, 1));
      geom.setAttribute("aStartPos", new THREE.InstancedBufferAttribute(startPositions, 3));
      geom.setAttribute("aEndPos", new THREE.InstancedBufferAttribute(endPositions, 3));
      geom.setAttribute("aFlowOffset", new THREE.InstancedBufferAttribute(flowOffsets, 1));
    });

    // 4. Instantiate sub-meshes
    const sphereMesh = new THREE.InstancedMesh(sphereGeom, material, count);
    const quadMesh = new THREE.InstancedMesh(quadGeom, material, count);
    const pointMesh = new THREE.InstancedMesh(pointGeom, material, count);

    // Disable frustum culling to let manual culling take over
    sphereMesh.frustumCulled = false;
    quadMesh.frustumCulled = false;
    pointMesh.frustumCulled = false;

    // Initialize all matrices and colorings
    const color = new THREE.Color(config.material.color ?? "#ffffff");
    for (let i = 0; i < count; i++) {
      this.dummy.position.copy(positions[i]);
      this.dummy.scale.setScalar(1.0);
      this.dummy.updateMatrix();

      // LOD 0 starts active, others start off-screen
      sphereMesh.setMatrixAt(i, this.dummy.matrix);
      sphereMesh.setColorAt(i, color);

      this.dummy.position.set(9999, 9999, 9999);
      this.dummy.updateMatrix();
      quadMesh.setMatrixAt(i, this.dummy.matrix);
      quadMesh.setColorAt(i, color);
      pointMesh.setMatrixAt(i, this.dummy.matrix);
      pointMesh.setColorAt(i, color);
    }

    // Force upload
    [sphereMesh, quadMesh, pointMesh].forEach((mesh) => {
      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    });

    const container = new THREE.Group();
    container.add(sphereMesh);
    container.add(quadMesh);
    container.add(pointMesh);

    const group: ParticleGroup = {
      id,
      count,
      config,
      animationState: "idle",
      lodMeshes: {
        sphere: sphereMesh,
        quad: quadMesh,
        point: pointMesh,
      },
      container,
      material,
    };

    this.groups.set(id, group);
    return group;
  }

  /**
   * Directly updates particle matrices and colors.
   */
  updateParticles(id: string, updateFn: ParticleUpdateFn): void {
    const group = this.groups.get(id);
    if (!group) return;

    const count = group.count;
    const tempMatrix = new THREE.Matrix4();
    const tempColor = new THREE.Color();

    for (let i = 0; i < count; i++) {
      // Pull matrix from the sphere (LOD 0) representation
      group.lodMeshes.sphere.getMatrixAt(i, tempMatrix);
      
      const instanceColor = group.lodMeshes.sphere.instanceColor;
      if (instanceColor) {
        tempColor.fromArray(instanceColor.array, i * 3);
      }

      updateFn(i, tempMatrix, tempColor);

      // Copy updates back to the LOD meshes
      group.lodMeshes.sphere.setMatrixAt(i, tempMatrix);
      group.lodMeshes.quad.setMatrixAt(i, tempMatrix);
      group.lodMeshes.point.setMatrixAt(i, tempMatrix);

      if (instanceColor) {
        group.lodMeshes.sphere.setColorAt(i, tempColor);
        group.lodMeshes.quad.setColorAt(i, tempColor);
        group.lodMeshes.point.setColorAt(i, tempColor);
      }
    }

    // Flag GPU updates
    Object.values(group.lodMeshes).forEach((mesh) => {
      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    });
  }

  /**
   * Adjusts particle limits dynamically when the quality tier is updated.
   */
  adjustQuality(tier: QualityTier): void {
    this.groups.forEach((group) => {
      const newCount = group.config.count[tier];
      group.count = newCount;
      
      // Setting InstancedMesh.count restricts WebGL draw limits instantly
      group.lodMeshes.sphere.count = newCount;
      group.lodMeshes.quad.count = newCount;
      group.lodMeshes.point.count = newCount;

      Object.values(group.lodMeshes).forEach((mesh) => {
        mesh.instanceMatrix.needsUpdate = true;
      });
      console.log(`[ParticleSystemEngine] Re-scaled group ${group.id} rendering to ${newCount} particles`);
    });
  }

  /**
   * Animates a particle group.
   */
  animateParticles(_id: string, _animation: any): void {
    // Handled by ParticleAnimator
  }

  /**
   * Destroys particle group and cleans up buffers to prevent leaks.
   */
  destroyParticles(id: string): void {
    const group = this.groups.get(id);
    if (!group) return;

    // Dispose geometries
    group.lodMeshes.sphere.geometry.dispose();
    group.lodMeshes.quad.geometry.dispose();
    group.lodMeshes.point.geometry.dispose();

    // Dispose materials
    group.material.dispose();

    // Remove from container
    group.container.clear();

    this.groups.delete(id);
  }

  /**
   * Gets a registered particle group.
   */
  getGroup(id: string): ParticleGroup | undefined {
    return this.groups.get(id);
  }

  private generatePositions(distConfig: any, count: number): THREE.Vector3[] {
    const positions: THREE.Vector3[] = [];
    const type = distConfig.type;
    const size = distConfig.size ?? 50.0; // Default distribution spread size
    const bounds = distConfig.bounds;

    for (let i = 0; i < count; i++) {
      const vec = new THREE.Vector3();

      if (bounds && Array.isArray(bounds) && bounds.length === 2) {
        // Uniform distribution inside bounds box
        const minB = bounds[0];
        const maxB = bounds[1];
        vec.x = minB[0] + Math.random() * (maxB[0] - minB[0]);
        vec.y = minB[1] + Math.random() * (maxB[1] - minB[1]);
        vec.z = minB[2] + Math.random() * (maxB[2] - minB[2]);
      } else if (type === "galaxy") {
        // Logarithmic spiral galaxy distribution
        const arms = distConfig.arms ?? 2;
        const tightness = distConfig.tightness ?? 0.12;
        const coreRadius = distConfig.coreRadius ?? 8.0;

        const armIndex = i % arms;
        const armAngle = (armIndex * Math.PI * 2.0) / arms;

        // Exponential distribution for high center density
        const r = coreRadius + (Math.pow(Math.random(), 2.0) * size);
        const angle = armAngle + r * tightness;

        // Bounded arm thickness dispersion
        const dispersion = size * 0.08 * (r / size + 0.1);
        const dx = (Math.random() - 0.5) * dispersion;
        const dy = (Math.random() - 0.5) * dispersion;
        const dz = (Math.random() - 0.5) * dispersion;

        // Galaxy disk lies in the X-Y plane, Z is the thickness axis (camera flies along Z)
        vec.x = r * Math.cos(angle) + dx;
        vec.y = r * Math.sin(angle) + dy;
        vec.z = dz;
      } else if (type === "double_helix") {
        // Double strand helical DNA vortex winding along Y axis
        const radius = distConfig.radius ?? 12.0;
        const pitch = distConfig.pitch ?? 0.65;
        const jitter = distConfig.jitter ?? 0.8;

        const strand = (i % 2 === 0) ? 0.0 : Math.PI;
        // Map progression along the length (-4PI to +4PI)
        const t = (i / count) * Math.PI * 8.0;

        vec.x = radius * Math.cos(t + strand);
        vec.y = (t - Math.PI * 4.0) * pitch * 5.0; // centered vertically around Y=0
        vec.z = radius * Math.sin(t + strand);

        // Add small structural jitter noise
        vec.x += (Math.random() - 0.5) * jitter;
        vec.y += (Math.random() - 0.5) * jitter;
        vec.z += (Math.random() - 0.5) * jitter;
      } else if (type === "sphere") {
        // Uniform spherical surface distribution
        const u = Math.random();
        const v = Math.random();
        const theta = Math.acos(2.0 * u - 1.0);
        const phi = Math.PI * 2.0 * v;

        vec.x = size * Math.sin(theta) * Math.cos(phi);
        vec.y = size * Math.sin(theta) * Math.sin(phi);
        vec.z = size * Math.cos(theta);
      } else if (type === "box") {
        // Box bounds
        vec.x = (Math.random() - 0.5) * size;
        vec.y = (Math.random() - 0.5) * size;
        vec.z = (Math.random() - 0.5) * size;
      } else if (type === "grid") {
        // Structured spatial grid coordinates
        const side = Math.ceil(Math.pow(count, 1.0 / 3.0));
        const spacing = size / side;
        const ix = i % side;
        const iy = Math.floor((i / side) % side);
        const iz = Math.floor(i / (side * side));

        // Add jitter to make it look organic
        const jitter = spacing * 0.35;
        vec.x = (ix - side / 2) * spacing + (Math.random() - 0.5) * jitter;
        vec.y = (iy - side / 2) * spacing + (Math.random() - 0.5) * jitter;
        vec.z = (iz - side / 2) * spacing + (Math.random() - 0.5) * jitter;
      } else {
        // Default random cluster
        vec.x = (Math.random() - 0.5) * size * 2;
        vec.y = (Math.random() - 0.5) * size * 2;
        vec.z = (Math.random() - 0.5) * size * 2;
      }

      positions.push(vec);
    }

    return positions;
  }
}
