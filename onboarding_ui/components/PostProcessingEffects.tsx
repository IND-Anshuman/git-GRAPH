"use client";

import { useRef } from "react";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import {
  EffectComposer,
  Bloom,
  DepthOfField,
  SSAO,
  ToneMapping,
  Vignette,
  ChromaticAberration,
} from "@react-three/postprocessing";
import { ToneMappingMode } from "postprocessing";
import { useOnboardingStore } from "@/stores/onboardingStore";

export function PostProcessingEffects() {
  const qualityTier = useOnboardingStore((s) => s.qualityTier);
  const currentScene = useOnboardingStore((s) => s.currentScene);
  const bloomRef = useRef<any>(null);

  // Scene-specific focal distances and lengths for Depth of Field
  const focalSettings: Record<number, { focusDistance: number; focalLength: number }> = {
    1: { focusDistance: 30, focalLength: 35 },
    2: { focusDistance: 40, focalLength: 40 },
    3: { focusDistance: 100, focalLength: 45 },
    4: { focusDistance: 80, focalLength: 50 },
    5: { focusDistance: 150, focalLength: 55 },
    6: { focusDistance: 60, focalLength: 45 },
    7: { focusDistance: 50, focalLength: 40 },
    8: { focusDistance: 200, focalLength: 200 }, // Scene 8 has DoF disabled, but we put fallback
  };

  const settings = focalSettings[currentScene] || { focusDistance: 50, focalLength: 45 };

  // Performance degradation rules
  const shouldRenderSSAO = qualityTier === "ultra";
  const shouldRenderDOF = (qualityTier === "ultra" || (qualityTier === "high" && currentScene !== 1)) && currentScene !== 8;
  const shouldRenderBloom = qualityTier !== "low";
  const shouldRenderColorGrading = qualityTier !== "low";

  // Dynamic pulsing bloom intensity on ULTRA settings to create "living" gas elements
  useFrame((state) => {
    if (bloomRef.current) {
      if (currentScene === 1) {
        bloomRef.current.intensity = qualityTier === "ultra" ? 0.95 : qualityTier === "high" ? 0.8 : 0.55;
      } else if (qualityTier === "ultra") {
        const time = state.clock.getElapsedTime();
        bloomRef.current.intensity = 0.7 + Math.sin(time * 1.5) * 0.1;
      }
    }
  });

  if (qualityTier === "low") {
    // Zero post-processing overhead on low-end machines
    return null;
  }

  // Define shadow color for SSAO
  const ssaoColor = new THREE.Color("black");

  const bloomIntensity = currentScene === 1
    ? (qualityTier === "ultra" ? 0.95 : qualityTier === "high" ? 0.8 : 0.55)
    : (qualityTier === "ultra" ? 0.7 : qualityTier === "high" ? 0.6 : 0.5);

  const bloomThreshold = currentScene === 1
    ? (qualityTier === "ultra" ? 0.25 : qualityTier === "high" ? 0.35 : 0.45)
    : (qualityTier === "ultra" ? 0.3 : qualityTier === "high" ? 0.4 : 0.5);

  return (
    <EffectComposer enableNormalPass={qualityTier === "ultra"}>
      {shouldRenderBloom ? (
        <Bloom
          ref={bloomRef}
          intensity={bloomIntensity}
          luminanceThreshold={bloomThreshold}
          luminanceSmoothing={0.9}
          mipmapBlur={true}
        />
      ) : (
        <group name="bloom-placeholder" />
      )}

      {shouldRenderDOF ? (
        <DepthOfField
          focusDistance={settings.focusDistance}
          focalLength={settings.focalLength}
          bokehScale={2.0}
          height={qualityTier === "ultra" ? 720 : 480}
        />
      ) : (
        <group name="dof-placeholder" />
      )}

      {shouldRenderSSAO ? (
        <SSAO
          samples={32}
          radius={0.5}
          intensity={0.3}
          luminanceInfluence={0.5}
          color={ssaoColor}
        />
      ) : (
        <group name="ssao-placeholder" />
      )}

      {shouldRenderColorGrading ? (
        <ToneMapping
          adaptive={false}
          mode={ToneMappingMode.ACES_FILMIC}
          middleGrey={0.6}
          maxLuminance={16.0}
          averageLuminance={1.0}
        />
      ) : (
        <group name="tone-mapping-placeholder" />
      )}

      {shouldRenderColorGrading ? (
        <ChromaticAberration
          offset={[0.0005, 0.0005]}
          radialModulation={false}
        />
      ) : (
        <group name="chromatic-aberration-placeholder" />
      )}

      {shouldRenderColorGrading ? (
        <Vignette
          offset={0.3}
          darkness={0.5}
          eskil={false}
        />
      ) : (
        <group name="vignette-placeholder" />
      )}
    </EffectComposer>
  );
}
