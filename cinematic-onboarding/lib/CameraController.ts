// Task 1.5: Camera Controller - Manages camera position and rotation along spline rails

import * as THREE from "three";
import { CameraState, CameraRailDefinition } from "@/types";
import { applyEasing } from "./three-utils";

/**
 * CameraController class manages the camera position, rotation, fov,
 * and target along spline rails defined by keyframes, with support for
 * look-at targets and additive parallax offsets.
 */
export class CameraController {
  private rail: CameraRailDefinition | null = null;
  private additiveOffset: THREE.Vector3 = new THREE.Vector3();
  private lookAtTarget: THREE.Vector3 | null = null;

  constructor(rail?: CameraRailDefinition) {
    if (rail) {
      this.setRail(rail);
    }
  }

  /**
   * Sets the camera rail definition and sorts keyframes by progress.
   */
  setRail(rail: CameraRailDefinition): void {
    this.rail = {
      ...rail,
      keyframes: [...rail.keyframes].sort((a, b) => a.progress - b.progress),
    };
  }

  /**
   * Sets the look-at target for the camera.
   */
  setLookAtTarget(target: "origin" | [number, number, number] | null): void {
    if (!target) {
      this.lookAtTarget = null;
    } else if (target === "origin") {
      this.lookAtTarget = new THREE.Vector3(0, 0, 0);
    } else {
      this.lookAtTarget = new THREE.Vector3(target[0], target[1], target[2]);
    }
  }

  /**
   * Adds an additive offset for parallax or other visual adjustments.
   */
  addOffset(offset: THREE.Vector3): void {
    this.additiveOffset.copy(offset);
  }

  /**
   * Updates camera state based on the progress within the active rail.
   * @param progress normalized progress [0, 1] between keyframes.
   * @returns The calculated CameraState.
   */
  updateCamera(progress: number): CameraState {
    if (!this.rail || this.rail.keyframes.length === 0) {
      return {
        position: new THREE.Vector3(0, 0, -50).add(this.additiveOffset),
        rotation: new THREE.Euler(0, 0, 0),
        fov: 75,
        target: this.lookAtTarget || new THREE.Vector3(0, 0, 0),
      };
    }

    const keyframes = this.rail.keyframes;

    // Clamp progress
    const clampedProgress = Math.max(0, Math.min(1, progress));

    // Handle single keyframe boundary cases
    if (keyframes.length === 1) {
      const kf = keyframes[0];
      const pos = new THREE.Vector3().fromArray(kf.position).add(this.additiveOffset);
      const rot = new THREE.Euler();
      if (kf.rotation) {
        rot.fromArray(kf.rotation);
      }
      return {
        position: pos,
        rotation: rot,
        fov: kf.fov ?? 75,
        target: this.lookAtTarget || new THREE.Vector3(0, 0, 0),
      };
    }

    // Find surrounding keyframes
    let prevIndex = 0;
    let nextIndex = 0;

    if (clampedProgress <= keyframes[0].progress) {
      prevIndex = 0;
      nextIndex = 1;
    } else if (clampedProgress >= keyframes[keyframes.length - 1].progress) {
      prevIndex = keyframes.length - 2;
      nextIndex = keyframes.length - 1;
    } else {
      for (let i = 0; i < keyframes.length - 1; i++) {
        if (clampedProgress >= keyframes[i].progress && clampedProgress < keyframes[i + 1].progress) {
          prevIndex = i;
          nextIndex = i + 1;
          break;
        }
      }
    }

    const prev = keyframes[prevIndex];
    const next = keyframes[nextIndex];

    // Calculate transition progress between these two keyframes
    let t = 0;
    const progressRange = next.progress - prev.progress;
    if (progressRange > 0) {
      t = (clampedProgress - prev.progress) / progressRange;
    }
    t = Math.max(0, Math.min(1, t));

    // Apply easing
    const easing = next.easing || "linear";
    const easedT = applyEasing(t, easing);

    // Interpolate position
    const position = new THREE.Vector3();
    const p1 = new THREE.Vector3().fromArray(prev.position);
    const p2 = new THREE.Vector3().fromArray(next.position);

    if (this.rail.splineType === "catmullRom") {
      const p0Keyframe = keyframes[Math.max(0, prevIndex - 1)];
      const p3Keyframe = keyframes[Math.min(keyframes.length - 1, nextIndex + 1)];

      const p0 = new THREE.Vector3().fromArray(p0Keyframe.position);
      const p3 = new THREE.Vector3().fromArray(p3Keyframe.position);

      position.copy(this.catmullRomInterpolate(p0, p1, p2, p3, easedT));
    } else {
      // Linear lerp as default / linear spline type
      position.lerpVectors(p1, p2, easedT);
    }

    // Apply additive offset
    position.add(this.additiveOffset);

    // Interpolate rotation
    const rotation = new THREE.Euler();
    if (prev.rotation && next.rotation) {
      const q1 = new THREE.Quaternion().setFromEuler(new THREE.Euler().fromArray(prev.rotation));
      const q2 = new THREE.Quaternion().setFromEuler(new THREE.Euler().fromArray(next.rotation));
      const q = new THREE.Quaternion().slerpQuaternions(q1, q2, easedT);
      rotation.setFromQuaternion(q);
    } else if (prev.rotation) {
      rotation.fromArray(prev.rotation);
    }

    // Interpolate FOV
    const prevFov = prev.fov ?? 75;
    const nextFov = next.fov ?? 75;
    const fov = prevFov + (nextFov - prevFov) * easedT;

    // Calculate target and adjust rotation if lookAtTarget is specified
    const target = new THREE.Vector3(0, 0, 0);
    if (this.lookAtTarget) {
      target.copy(this.lookAtTarget);
      
      const m = new THREE.Matrix4();
      m.lookAt(position, target, new THREE.Vector3(0, 1, 0));
      rotation.setFromRotationMatrix(m);
    }

    return {
      position,
      rotation,
      fov,
      target,
    };
  }

  private catmullRomInterpolate(
    p0: THREE.Vector3,
    p1: THREE.Vector3,
    p2: THREE.Vector3,
    p3: THREE.Vector3,
    t: number
  ): THREE.Vector3 {
    const t2 = t * t;
    const t3 = t2 * t;

    return new THREE.Vector3(
      0.5 * (
        (2 * p1.x) +
        (-p0.x + p2.x) * t +
        (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 +
        (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3
      ),
      0.5 * (
        (2 * p1.y) +
        (-p0.y + p2.y) * t +
        (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 +
        (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3
      ),
      0.5 * (
        (2 * p1.z) +
        (-p0.z + p2.z) * t +
        (2 * p0.z - 5 * p1.z + 4 * p2.z - p3.z) * t2 +
        (-p0.z + 3 * p1.z - 3 * p2.z + p3.z) * t3
      )
    );
  }
}
