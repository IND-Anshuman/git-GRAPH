import { describe, it, expect } from 'vitest';
import { progressToScene, applyEasing, getParticleCount } from './three-utils';

describe('three-utils', () => {
  describe('progressToScene', () => {
    it('should return scene 1 for progress 0 to 0.17', () => {
      expect(progressToScene(0)).toBe(1);
      expect(progressToScene(0.1)).toBe(1);
      expect(progressToScene(0.16)).toBe(1);
    });

    it('should return scene 2 for progress 0.17 to 0.33', () => {
      expect(progressToScene(0.17)).toBe(2);
      expect(progressToScene(0.25)).toBe(2);
      expect(progressToScene(0.32)).toBe(2);
    });

    it('should return scene 3 for progress 0.33 to 0.5', () => {
      expect(progressToScene(0.33)).toBe(3);
      expect(progressToScene(0.4)).toBe(3);
      expect(progressToScene(0.49)).toBe(3);
    });

    it('should return scene 4 for progress 0.5 to 0.67', () => {
      expect(progressToScene(0.5)).toBe(4);
      expect(progressToScene(0.6)).toBe(4);
      expect(progressToScene(0.66)).toBe(4);
    });

    it('should return scene 5 for progress 0.67 to 0.83', () => {
      expect(progressToScene(0.67)).toBe(5);
      expect(progressToScene(0.75)).toBe(5);
      expect(progressToScene(0.82)).toBe(5);
    });

    it('should return scene 6 for progress 0.83 to 1.0', () => {
      expect(progressToScene(0.83)).toBe(6);
      expect(progressToScene(0.9)).toBe(6);
      expect(progressToScene(0.99)).toBe(6);
    });

    it('should return scene 7 for progress 1.0', () => {
      expect(progressToScene(1.0)).toBe(7);
    });

    it('should clamp negative progress to scene 1', () => {
      expect(progressToScene(-0.5)).toBe(1);
    });

    it('should clamp progress > 1 to scene 7', () => {
      expect(progressToScene(1.5)).toBe(7);
    });
  });

  describe('applyEasing', () => {
    it('should return input for linear easing', () => {
      expect(applyEasing(0, 'linear')).toBe(0);
      expect(applyEasing(0.5, 'linear')).toBe(0.5);
      expect(applyEasing(1, 'linear')).toBe(1);
    });

    it('should apply easeInOut curve', () => {
      expect(applyEasing(0, 'easeInOut')).toBe(0);
      expect(applyEasing(1, 'easeInOut')).toBe(1);
      const mid = applyEasing(0.5, 'easeInOut');
      expect(mid).toBeGreaterThan(0.4);
      expect(mid).toBeLessThan(0.6);
    });

    it('should apply easeIn curve', () => {
      expect(applyEasing(0, 'easeIn')).toBe(0);
      expect(applyEasing(1, 'easeIn')).toBe(1);
      const mid = applyEasing(0.5, 'easeIn');
      expect(mid).toBeLessThan(0.5);
    });

    it('should apply easeOut curve', () => {
      expect(applyEasing(0, 'easeOut')).toBe(0);
      expect(applyEasing(1, 'easeOut')).toBe(1);
      const mid = applyEasing(0.5, 'easeOut');
      expect(mid).toBeGreaterThan(0.5);
    });

    it('should clamp values outside [0, 1]', () => {
      expect(applyEasing(-0.5)).toBe(0);
      expect(applyEasing(1.5)).toBe(1);
    });
  });

  describe('getParticleCount', () => {
    const counts = {
      ultra: 100000,
      high: 80000,
      medium: 50000,
      low: 30000,
    };

    it('should return ultra count for ultra tier', () => {
      expect(getParticleCount(counts, 'ultra')).toBe(100000);
    });

    it('should return high count for high tier', () => {
      expect(getParticleCount(counts, 'high')).toBe(80000);
    });

    it('should return medium count for medium tier', () => {
      expect(getParticleCount(counts, 'medium')).toBe(50000);
    });

    it('should return low count for low tier', () => {
      expect(getParticleCount(counts, 'low')).toBe(30000);
    });
  });
});
