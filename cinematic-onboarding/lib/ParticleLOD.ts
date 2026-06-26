// Task 3.3: Level of Detail - Reduces geometry complexity for distant particles

import * as THREE from "three";
import { ParticleGroup } from "./ParticleSystemEngine";
import { FrustumCuller } from "./FrustumCuller";

/**
 * ParticleLODManager class handles dynamic level-of-detail mapping for particle groups.
 * It swaps instance matrices between sphere, quad, and point representations based
 * on camera distance, running every 5 frames to prevent CPU overhead.
 */
export class ParticleLODManager {
  private static instance: ParticleLODManager | null = null;
  private frameCounter: number = 0;
  private dummy = new THREE.Object3D();
  private boundingSphere = new THREE.Sphere(undefined, 1.0);

  private constructor() {}

  /**
   * Returns the singleton instance of ParticleLODManager.
   */
  static getInstance(): ParticleLODManager {
    if (!ParticleLODManager.instance) {
      ParticleLODManager.instance = new ParticleLODManager();
    }
    return ParticleLODManager.instance;
  }

  /**
   * Updates Level of Detail (LOD) and frustum culling for all instances in a group.
   * Swaps instance matrices between LOD meshes based on camera distance,
   * or hides them off-screen if they are out of the camera's view frustum.
   * Runs every 5 frames to conserve CPU.
   * 
   * @param group The particle group to update.
   * @param camera The active camera.
   */
  updateLOD(group: ParticleGroup, camera: THREE.Camera): void {
    this.frameCounter++;
    // Throttle calculation: run once every 5 ticks
    if (this.frameCounter % 5 !== 0) {
      return;
    }

    const count = group.count;
    const positionAttr = group.lodMeshes.sphere.geometry.getAttribute("aInitialPosition") as THREE.BufferAttribute;
    if (!positionAttr) return;

    const culler = FrustumCuller.getInstance();
    culler.setupFrustum(camera);

    const cameraPos = new THREE.Vector3();
    camera.getWorldPosition(cameraPos);

    const p = new THREE.Vector3();
    
    for (let i = 0; i < count; i++) {
      // Get particle's coordinate position
      p.set(positionAttr.getX(i), positionAttr.getY(i), positionAttr.getZ(i));

      // Frustum culling check
      this.boundingSphere.center.copy(p);
      this.boundingSphere.radius = 12.0; // Bounding margin to cover GPU-side drift/turbulence

      if (!culler.intersectsSphere(this.boundingSphere)) {
        // Cull: Move off-screen in all LOD representations
        this.dummy.position.set(9999, 9999, 9999);
        this.dummy.scale.setScalar(0.0);
        this.dummy.updateMatrix();
        
        group.lodMeshes.sphere.setMatrixAt(i, this.dummy.matrix);
        group.lodMeshes.quad.setMatrixAt(i, this.dummy.matrix);
        group.lodMeshes.point.setMatrixAt(i, this.dummy.matrix);
        continue;
      }
      
      const d = p.distanceTo(cameraPos);

      let activeMesh: THREE.InstancedMesh;
      let inactiveMesh1: THREE.InstancedMesh;
      let inactiveMesh2: THREE.InstancedMesh;
      let scaleMultiplier = 1.0;

      // Swap geometries based on distance thresholds (20m and 50m)
      if (d < 20.0) {
        activeMesh = group.lodMeshes.sphere;
        inactiveMesh1 = group.lodMeshes.quad;
        inactiveMesh2 = group.lodMeshes.point;
        scaleMultiplier = 1.0;
      } else if (d < 50.0) {
        activeMesh = group.lodMeshes.quad;
        inactiveMesh1 = group.lodMeshes.sphere;
        inactiveMesh2 = group.lodMeshes.point;
        scaleMultiplier = 0.8;
      } else {
        activeMesh = group.lodMeshes.point;
        inactiveMesh1 = group.lodMeshes.sphere;
        inactiveMesh2 = group.lodMeshes.quad;
        scaleMultiplier = 0.5;
      }

      // Build active transformation matrix
      this.dummy.position.copy(p);
      this.dummy.scale.setScalar(scaleMultiplier);
      this.dummy.updateMatrix();
      activeMesh.setMatrixAt(i, this.dummy.matrix);

      // Hide inactive meshes off-screen
      this.dummy.position.set(9999, 9999, 9999);
      this.dummy.scale.setScalar(0.0);
      this.dummy.updateMatrix();
      inactiveMesh1.setMatrixAt(i, this.dummy.matrix);
      inactiveMesh2.setMatrixAt(i, this.dummy.matrix);
    }

    // Flag GPU updates
    Object.values(group.lodMeshes).forEach((mesh) => {
      mesh.instanceMatrix.needsUpdate = true;
    });
  }
}
