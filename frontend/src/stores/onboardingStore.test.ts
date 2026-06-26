/**
 * Unit tests for Onboarding Store
 * 
 * Tests all store actions, state transitions, and derived selectors
 * to ensure correct state management for the cinematic onboarding experience.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  useOnboardingStore,
  useSceneLocalProgress,
  useShouldAnimateCamera,
  useParticleCount,
  useShouldUsePostProcessing,
  type QualityTier,
  type SceneNumber,
} from './onboardingStore';

describe('OnboardingStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const { result } = renderHook(() => useOnboardingStore());
    act(() => {
      result.current.resetProgress();
      result.current.setQualityTier('high');
      result.current.setReducedMotion(false);
      result.current.setAudioEnabled(false);
    });
  });

  describe('Scroll Progress', () => {
    it('should initialize with zero scroll progress', () => {
      const { result } = renderHook(() => useOnboardingStore());
      expect(result.current.scrollProgress).toBe(0);
    });

    it('should update scroll progress within valid range', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setScrollProgress(0.5);
      });
      
      expect(result.current.scrollProgress).toBe(0.5);
    });

    it('should clamp scroll progress to [0, 1]', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setScrollProgress(1.5);
      });
      expect(result.current.scrollProgress).toBe(1);
      
      act(() => {
        result.current.setScrollProgress(-0.5);
      });
      expect(result.current.scrollProgress).toBe(0);
    });

    it('should update current scene based on scroll progress', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      // Scene 1 (0-0.17)
      act(() => {
        result.current.setScrollProgress(0.1);
      });
      expect(result.current.currentScene).toBe(1);
      
      // Scene 2 (0.17-0.33)
      act(() => {
        result.current.setScrollProgress(0.25);
      });
      expect(result.current.currentScene).toBe(2);
      
      // Scene 3 (0.33-0.50)
      act(() => {
        result.current.setScrollProgress(0.4);
      });
      expect(result.current.currentScene).toBe(3);
      
      // Scene 4 (0.50-0.67)
      act(() => {
        result.current.setScrollProgress(0.6);
      });
      expect(result.current.currentScene).toBe(4);
      
      // Scene 5 (0.67-0.83)
      act(() => {
        result.current.setScrollProgress(0.75);
      });
      expect(result.current.currentScene).toBe(5);
      
      // Scene 6 (0.83-1.00)
      act(() => {
        result.current.setScrollProgress(0.9);
      });
      expect(result.current.currentScene).toBe(6);
      
      // Scene 8 (1.00)
      act(() => {
        result.current.setScrollProgress(1.0);
      });
      expect(result.current.currentScene).toBe(8);
    });
  });

  describe('Scene Management', () => {
    it('should set current scene directly', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setCurrentScene(5);
      });
      
      expect(result.current.currentScene).toBe(5);
    });

    it('should get scene boundaries correctly', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      expect(result.current.getSceneBoundaries(1)).toEqual({ start: 0.00, end: 0.17 });
      expect(result.current.getSceneBoundaries(2)).toEqual({ start: 0.17, end: 0.33 });
      expect(result.current.getSceneBoundaries(3)).toEqual({ start: 0.33, end: 0.50 });
      expect(result.current.getSceneBoundaries(4)).toEqual({ start: 0.50, end: 0.67 });
      expect(result.current.getSceneBoundaries(5)).toEqual({ start: 0.67, end: 0.83 });
      expect(result.current.getSceneBoundaries(6)).toEqual({ start: 0.83, end: 1.00 });
    });

    it('should update scene loading status', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setSceneStatus(1, 'loading');
      });
      expect(result.current.sceneStatuses[1]).toBe('loading');
      
      act(() => {
        result.current.setSceneStatus(1, 'ready');
      });
      expect(result.current.sceneStatuses[1]).toBe('ready');
      
      act(() => {
        result.current.setSceneStatus(1, 'active');
      });
      expect(result.current.sceneStatuses[1]).toBe('active');
    });

    it('should check if scene is ready', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setSceneStatus(1, 'unloaded');
      });
      expect(result.current.isSceneReady(1)).toBe(false);
      
      act(() => {
        result.current.setSceneStatus(1, 'loading');
      });
      expect(result.current.isSceneReady(1)).toBe(false);
      
      act(() => {
        result.current.setSceneStatus(1, 'ready');
      });
      expect(result.current.isSceneReady(1)).toBe(true);
      
      act(() => {
        result.current.setSceneStatus(1, 'active');
      });
      expect(result.current.isSceneReady(1)).toBe(true);
    });

    it('should detect scene transitions', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      // Not in transition
      act(() => {
        result.current.setScrollProgress(0.1);
      });
      expect(result.current.isInTransition()).toBe(false);
      
      // In transition (near 0.17 boundary)
      act(() => {
        result.current.setScrollProgress(0.18);
      });
      expect(result.current.isInTransition()).toBe(true);
      
      // In transition (near 0.33 boundary)
      act(() => {
        result.current.setScrollProgress(0.32);
      });
      expect(result.current.isInTransition()).toBe(true);
    });
  });

  describe('Quality Tier', () => {
    it('should set quality tier', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      const tiers: QualityTier[] = ['ultra', 'high', 'medium', 'low'];
      
      tiers.forEach(tier => {
        act(() => {
          result.current.setQualityTier(tier);
        });
        expect(result.current.qualityTier).toBe(tier);
      });
    });
  });

  describe('Interaction State', () => {
    it('should set hovered object', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setHoveredObject('particle-123');
      });
      expect(result.current.hoveredObjectId).toBe('particle-123');
      
      act(() => {
        result.current.setHoveredObject(null);
      });
      expect(result.current.hoveredObjectId).toBe(null);
    });

    it('should expand and close info card', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      // Initially no card expanded
      expect(result.current.expandedCardId).toBe(null);
      expect(result.current.cameraPaused).toBe(false);
      
      // Expand card
      act(() => {
        result.current.expandCard('planet-auth');
      });
      expect(result.current.expandedCardId).toBe('planet-auth');
      expect(result.current.cameraPaused).toBe(true);
      
      // Close card
      act(() => {
        result.current.closeCard();
      });
      expect(result.current.expandedCardId).toBe(null);
      expect(result.current.cameraPaused).toBe(false);
    });
  });

  describe('Camera Control', () => {
    it('should pause and resume camera', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      expect(result.current.cameraPaused).toBe(false);
      
      act(() => {
        result.current.pauseCamera();
      });
      expect(result.current.cameraPaused).toBe(true);
      
      act(() => {
        result.current.resumeCamera();
      });
      expect(result.current.cameraPaused).toBe(false);
    });

    it('should pause camera when expanding card', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.expandCard('planet-123');
      });
      
      expect(result.current.cameraPaused).toBe(true);
    });

    it('should resume camera when closing card', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.expandCard('planet-123');
        result.current.closeCard();
      });
      
      expect(result.current.cameraPaused).toBe(false);
    });
  });

  describe('Audio State', () => {
    it('should initialize with audio disabled', () => {
      const { result } = renderHook(() => useOnboardingStore());
      expect(result.current.audioEnabled).toBe(false);
    });

    it('should toggle audio', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.toggleAudio();
      });
      expect(result.current.audioEnabled).toBe(true);
      
      act(() => {
        result.current.toggleAudio();
      });
      expect(result.current.audioEnabled).toBe(false);
    });

    it('should set audio enabled', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setAudioEnabled(true);
      });
      expect(result.current.audioEnabled).toBe(true);
      
      act(() => {
        result.current.setAudioEnabled(false);
      });
      expect(result.current.audioEnabled).toBe(false);
    });
  });

  describe('Accessibility', () => {
    it('should set reduced motion', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.setReducedMotion(true);
      });
      expect(result.current.reducedMotion).toBe(true);
      
      act(() => {
        result.current.setReducedMotion(false);
      });
      expect(result.current.reducedMotion).toBe(false);
    });

    it('should skip animation and jump to final scene', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.skipAnimation();
      });
      
      expect(result.current.animationSkipped).toBe(true);
      expect(result.current.scrollProgress).toBe(1.0);
      expect(result.current.currentScene).toBe(8);
    });
  });

  describe('Progress Persistence', () => {
    it('should track last completed scene', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.completeScene(3);
      });
      expect(result.current.lastCompletedScene).toBe(3);
      
      act(() => {
        result.current.completeScene(5);
      });
      expect(result.current.lastCompletedScene).toBe(5);
    });

    it('should not regress last completed scene', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      act(() => {
        result.current.completeScene(5);
      });
      expect(result.current.lastCompletedScene).toBe(5);
      
      act(() => {
        result.current.completeScene(3);
      });
      expect(result.current.lastCompletedScene).toBe(5);
    });

    it('should mark journey as completed', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      expect(result.current.journeyCompleted).toBe(false);
      
      act(() => {
        result.current.completeJourney();
      });
      
      expect(result.current.journeyCompleted).toBe(true);
      expect(result.current.lastCompletedScene).toBe(8);
    });

    it('should reset progress', () => {
      const { result } = renderHook(() => useOnboardingStore());
      
      // Set some state
      act(() => {
        result.current.setScrollProgress(0.5);
        result.current.completeScene(3);
        result.current.expandCard('planet-123');
        result.current.setHoveredObject('particle-456');
        result.current.completeJourney();
      });
      
      // Reset
      act(() => {
        result.current.resetProgress();
      });
      
      expect(result.current.scrollProgress).toBe(0);
      expect(result.current.currentScene).toBe(1);
      expect(result.current.lastCompletedScene).toBe(null);
      expect(result.current.journeyCompleted).toBe(false);
      expect(result.current.animationSkipped).toBe(false);
      expect(result.current.expandedCardId).toBe(null);
      expect(result.current.hoveredObjectId).toBe(null);
      expect(result.current.cameraPaused).toBe(false);
    });
  });

  describe('Derived Selectors', () => {
    describe('useSceneLocalProgress', () => {
      it('should calculate scene-local progress', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useSceneLocalProgress());
        
        // Scene 2 starts at 0.17, ends at 0.33 (range = 0.16)
        // At 0.25, local progress = (0.25 - 0.17) / 0.16 = 0.5
        act(() => {
          storeResult.current.setScrollProgress(0.25);
        });
        
        expect(selectorResult.current).toBeCloseTo(0.5, 2);
      });

      it('should return 1.0 for zero-range scenes', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useSceneLocalProgress());
        
        // Scene 8 has zero range
        act(() => {
          storeResult.current.setScrollProgress(1.0);
        });
        
        expect(selectorResult.current).toBe(1.0);
      });
    });

    describe('useShouldAnimateCamera', () => {
      it('should return true when camera is active', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useShouldAnimateCamera());
        
        expect(selectorResult.current).toBe(true);
      });

      it('should return false when camera is paused', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useShouldAnimateCamera());
        
        act(() => {
          storeResult.current.pauseCamera();
        });
        
        expect(selectorResult.current).toBe(false);
      });

      it('should return false when reduced motion is enabled', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useShouldAnimateCamera());
        
        act(() => {
          storeResult.current.setReducedMotion(true);
        });
        
        expect(selectorResult.current).toBe(false);
      });

      it('should return false when animation is skipped', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useShouldAnimateCamera());
        
        act(() => {
          storeResult.current.skipAnimation();
        });
        
        expect(selectorResult.current).toBe(false);
      });
    });

    describe('useParticleCount', () => {
      it('should return particle count for current quality tier', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        
        const baseCounts = {
          ultra: 100000,
          high: 50000,
          medium: 25000,
          low: 10000,
        };
        
        const { result: countResult } = renderHook(() => useParticleCount(baseCounts));
        
        // Default is high
        expect(countResult.current).toBe(50000);
        
        act(() => {
          storeResult.current.setQualityTier('ultra');
        });
        expect(countResult.current).toBe(100000);
        
        act(() => {
          storeResult.current.setQualityTier('low');
        });
        expect(countResult.current).toBe(10000);
      });
    });

    describe('useShouldUsePostProcessing', () => {
      it('should return true for high quality tiers', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useShouldUsePostProcessing());
        
        act(() => {
          storeResult.current.setQualityTier('ultra');
        });
        expect(selectorResult.current).toBe(true);
        
        act(() => {
          storeResult.current.setQualityTier('high');
        });
        expect(selectorResult.current).toBe(true);
        
        act(() => {
          storeResult.current.setQualityTier('medium');
        });
        expect(selectorResult.current).toBe(true);
      });

      it('should return false for low quality tier', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useShouldUsePostProcessing());
        
        act(() => {
          storeResult.current.setQualityTier('low');
        });
        
        expect(selectorResult.current).toBe(false);
      });

      it('should return false when reduced motion is enabled', () => {
        const { result: storeResult } = renderHook(() => useOnboardingStore());
        const { result: selectorResult } = renderHook(() => useShouldUsePostProcessing());
        
        act(() => {
          storeResult.current.setQualityTier('ultra');
          storeResult.current.setReducedMotion(true);
        });
        
        expect(selectorResult.current).toBe(false);
      });
    });
  });
});
