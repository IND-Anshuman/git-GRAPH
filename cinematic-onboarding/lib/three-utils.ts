import * as THREE from 'three';

/**
 * Check if WebGL is supported in the current browser
 */
export function isWebGLSupported(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch (e) {
    return false;
  }
}

/**
 * Get WebGL capabilities and limitations
 */
export function getWebGLCapabilities(
  renderer: THREE.WebGLRenderer
): {
  maxTextureSize: number;
  maxCubemapSize: number;
  maxAnisotropy: number;
  supportsFloatTextures: boolean;
} {
  const gl = renderer.getContext();
  const capabilities = renderer.capabilities;

  return {
    maxTextureSize: capabilities.maxTextureSize,
    maxCubemapSize: capabilities.maxCubemapSize,
    maxAnisotropy: capabilities.getMaxAnisotropy(),
    supportsFloatTextures: gl.getExtension('OES_texture_float') !== null,
  };
}

/**
 * Convert progress (0-1) to scene number (1-8)
 */
export function progressToScene(progress: number): number {
  const clampedProgress = Math.max(0, Math.min(1, progress));

  if (clampedProgress < 0.17) return 1;
  if (clampedProgress < 0.33) return 2;
  if (clampedProgress < 0.5) return 3;
  if (clampedProgress < 0.67) return 4;
  if (clampedProgress < 0.83) return 5;
  if (clampedProgress < 1.0) return 6;
  return 7;
}

/**
 * Apply easing function to interpolation value
 */
export function applyEasing(
  t: number,
  easing: 'linear' | 'easeInOut' | 'easeIn' | 'easeOut' = 'linear'
): number {
  const clamped = Math.max(0, Math.min(1, t));

  switch (easing) {
    case 'linear':
      return clamped;
    case 'easeInOut':
      return clamped < 0.5
        ? 2 * clamped * clamped
        : 1 - Math.pow(-2 * clamped + 2, 2) / 2;
    case 'easeIn':
      return clamped * clamped * clamped;
    case 'easeOut':
      return 1 - Math.pow(1 - clamped, 3);
    default:
      return clamped;
  }
}

/**
 * Interpolate between two Vector3 values with easing
 */
export function lerpVector3(
  a: THREE.Vector3,
  b: THREE.Vector3,
  t: number,
  easing: 'linear' | 'easeInOut' | 'easeIn' | 'easeOut' = 'linear'
): THREE.Vector3 {
  const easedT = applyEasing(t, easing);
  return new THREE.Vector3().lerpVectors(a, b, easedT);
}

/**
 * Calculate optimal particle count based on quality tier
 */
export function getParticleCount(
  baseCount: { ultra: number; high: number; medium: number; low: number },
  qualityTier: 'ultra' | 'high' | 'medium' | 'low'
): number {
  return baseCount[qualityTier];
}

/**
 * Check if a point is within the camera frustum
 */
export function isInFrustum(
  point: THREE.Vector3,
  camera: THREE.Camera,
  frustum?: THREE.Frustum
): boolean {
  if (!frustum) {
    frustum = new THREE.Frustum();
    const projectionMatrix = new THREE.Matrix4();
    projectionMatrix.multiplyMatrices(
      camera.projectionMatrix,
      camera.matrixWorldInverse
    );
    frustum.setFromProjectionMatrix(projectionMatrix);
  }

  return frustum.containsPoint(point);
}
