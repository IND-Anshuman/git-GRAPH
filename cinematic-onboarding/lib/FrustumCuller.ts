// Task 3.4: Frustum Culling - Manually cull particles outside camera view to save GPU cycles

import * as THREE from "three";
import { ParticleGroup } from "./ParticleSystemEngine";

/**
 * FrustumCuller class handles camera frustum intersection checks for instanced meshes.
 * If an instance is outside the camera view, it is moved off-screen to prevent rendering.
 */
export class FrustumCuller {
  private static instance: FrustumCuller | null = null;
  private frustum = new THREE.Frustum();
  private projScreenMatrix = new THREE.Matrix4();
  private dummy = new THREE.Object3D();
  private boundingSphere = new THREE.Sphere(undefined, 1.0);

  private constructor() {}

  /**
   * Returns the singleton instance of FrustumCuller.
   */
  static getInstance(): FrustumCuller {
    if (!FrustumCuller.instance) {
      FrustumCuller.instance = new FrustumCuller();
    }
    return FrustumCuller.instance;
  }

  /**
   * Sets up the frustum check against the active camera.
   */
  setupFrustum(camera: THREE.Camera): void {
    this.projScreenMatrix.multiplyMatrices(
      camera.projectionMatrix,
      camera.matrixWorldInverse
    );
    this.frustum.setFromProjectionMatrix(this.projScreenMatrix);
  }

  /**
   * Checks if a bounding sphere intersects the frustum.
   */
  intersectsSphere(sphere: THREE.Sphere): boolean {
    return this.frustum.intersectsSphere(sphere);
  }

  /**
   * Culls out-of-frustum instances in a particle group.
   * Modifies instance matrices of lodMeshes directly, restoring position using LOD values.
   * 
   * @param camera The active camera.
   * @param group The particle group to cull.
   * @returns Number of visible instances.
   */
  cullGroup(camera: THREE.Camera, group: ParticleGroup): number {
    this.setupFrustum(camera);

    let visibleCount = 0;
    const count = group.count;

    // Retrieve the initial coordinates attribute to read permanent positions
    const positionAttr = group.lodMeshes.sphere.geometry.getAttribute("aInitialPosition") as THREE.BufferAttribute;
    if (!positionAttr) return count;

    const cameraPos = new THREE.Vector3();
    camera.getWorldPosition(cameraPos);

    for (let i = 0; i < count; i++) {
      const px = positionAttr.getX(i);
      const py = positionAttr.getY(i);
      const pz = positionAttr.getZ(i);

      // Create a bounding sphere centered at the particle coordinates
      this.boundingSphere.center.set(px, py, pz);
      this.boundingSphere.radius = 12.0; // Bounding margin to cover GPU-side drift/turbulence

      if (this.intersectsSphere(this.boundingSphere)) {
        visibleCount++;
        
        // Restore correct LOD matrix representation
        const d = this.boundingSphere.center.distanceTo(cameraPos);
        let activeMesh: THREE.InstancedMesh;
        let inactiveMesh1: THREE.InstancedMesh;
        let inactiveMesh2: THREE.InstancedMesh;
        let scaleMultiplier = 1.0;

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

        this.dummy.position.set(px, py, pz);
        this.dummy.scale.setScalar(scaleMultiplier);
        this.dummy.updateMatrix();
        activeMesh.setMatrixAt(i, this.dummy.matrix);

        // Hide inactive
        this.dummy.position.set(9999, 9999, 9999);
        this.dummy.scale.setScalar(0.0);
        this.dummy.updateMatrix();
        inactiveMesh1.setMatrixAt(i, this.dummy.matrix);
        inactiveMesh2.setMatrixAt(i, this.dummy.matrix);
      } else {
        // Cull: Move off-screen in all LOD representations
        this.dummy.position.set(9999, 9999, 9999);
        this.dummy.scale.setScalar(0.0);
        this.dummy.updateMatrix();

        group.lodMeshes.sphere.setMatrixAt(i, this.dummy.matrix);
        group.lodMeshes.quad.setMatrixAt(i, this.dummy.matrix);
        group.lodMeshes.point.setMatrixAt(i, this.dummy.matrix);
      }
    }

    // Mark matrix updates
    Object.values(group.lodMeshes).forEach((mesh) => {
      mesh.instanceMatrix.needsUpdate = true;
    });

    return visibleCount;
  }
}
