"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { CodeSnippetRenderer } from "@/lib/CodeSnippetRenderer";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { SceneConfig } from "@/types";

interface ChaosSceneProps {
  active: boolean;
  config: SceneConfig;
}

const languages: Record<string, string> = {
  typescript: "TypeScript", python: "Python", javascript: "JavaScript",
  go: "Go", html: "HTML", java: "Java", ruby: "Ruby", sql: "SQL",
  css: "CSS", tf: "Terraform", yml: "YAML", json: "JSON", md: "Markdown"
};

const snippets = [
  { filename: "auth.service.ts", lang: "typescript", code: ["export class AuthService {", "  async login(cred) {", "    const t = await validate(cred);", "    return this.session(t);", "  }", "}"] },
  { filename: "user.py",         lang: "python",     code: ["class User(Model):", "    email = EmailField(unique=True)", "    name = CharField(max_length=100)", "    def check(self, pw):", "        return hash(pw)", "    "] },
  { filename: "checkout.js",     lang: "javascript", code: ["function process(cart) {", "  const tot = cart.items.reduce(", "    (s, i) => s + i.price, 0", "  );", "  return stripe.charge(tot);", "}"] },
  { filename: "app.go",          lang: "go",         code: ["func main() {", "\tr := gin.Default()", "\tr.GET(\"/ping\", func(c *gin.Context) {", "\t\tc.JSON(200, gin.H{\"msg\": \"pong\"})", "\t})", "\tr.Run()", "}"] },
];

const PLANET_POS = new THREE.Vector3(0, 0, 0);

interface ScatteredSlot {
  radius: number;
  theta: number;
  phi: number;
  speed: number;
  driftOffset: THREE.Vector3;
  driftSpeed: number;
  phase: number;
}

function buildScatteredSlots(count: number): ScatteredSlot[] {
  const slots: ScatteredSlot[] = [];
  for (let i = 0; i < count; i++) {
    const radius = 18 + (i / count) * 26 + (Math.random() - 0.5) * 3;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos((Math.random() * 2) - 1);
    slots.push({
      radius,
      theta,
      phi,
      speed: (Math.random() * 0.04 + 0.015) * (Math.random() > 0.5 ? 1 : -1),
      driftOffset: new THREE.Vector3(
        (Math.random() - 0.5) * 6,
        (Math.random() - 0.5) * 6,
        (Math.random() - 0.5) * 6
      ),
      driftSpeed: Math.random() * 0.15 + 0.08,
      phase: Math.random() * Math.PI * 2
    });
  }
  return slots;
}

export function ChaosScene({ active, config: _config }: ChaosSceneProps) {
  const groupRef     = useRef<THREE.Group>(null);
  const windowsGroup = useRef<THREE.Group>(null);

  const [initialized, setInitialized] = useState(false);

  const shouldAnimate    = useShouldAnimateCamera();
  const qualityTier      = useOnboardingStore((s) => s.qualityTier);
  const hoveredObject    = useOnboardingStore((s) => s.hoveredObjectId);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard       = useOnboardingStore((s) => s.expandCard);

  useEffect(() => { if (active && !initialized) setInitialized(true); }, [active, initialized]);

  const windowCount = useMemo(() => {
    switch (qualityTier) {
      case "low":    return 12;
      case "medium": return 20;
      case "high":   return 28;
      default:       return 32;
    }
  }, [qualityTier]);

  const scatteredSlots = useMemo(() => buildScatteredSlots(windowCount), [windowCount]);

  const codeWindowsData = useMemo(() => {
    if (!initialized || typeof window === "undefined") return [];
    const renderer = new CodeSnippetRenderer();
    return Array.from({ length: windowCount }, (_, i) => {
      const snip = snippets[i % snippets.length];
      const tex  = renderer.renderCodeSnippet(snip.filename, snip.code, snip.lang);
      return { id: `scene-1-window-${i}`, filename: snip.filename, lang: snip.lang, codeLength: snip.code.length, texture: tex, slot: scatteredSlots[i] };
    });
  }, [initialized, windowCount, scatteredSlots]);

  useFrame((state) => {
    if (!active || !initialized || !shouldAnimate) return;
    const time = state.clock.getElapsedTime();

    if (windowsGroup.current) {
      windowsGroup.current.children.forEach((child, idx) => {
        const win = codeWindowsData[idx];
        if (!win?.slot) return;
        const { radius, theta, phi, speed, driftOffset, driftSpeed, phase } = win.slot;

        const angle = time * speed + phase;
        const lx = Math.sin(phi) * Math.cos(theta + angle) * radius;
        const lz = Math.sin(phi) * Math.sin(theta + angle) * radius;
        const ly = Math.cos(phi) * radius;

        const dx = Math.sin(time * driftSpeed + phase) * driftOffset.x;
        const dy = Math.cos(time * driftSpeed * 1.1 + phase) * driftOffset.y;
        const dz = Math.sin(time * driftSpeed * 0.9 + phase) * driftOffset.z;

        const wx = PLANET_POS.x + lx + dx;
        const wy = PLANET_POS.y + ly + dy;
        const wz = PLANET_POS.z + lz + dz;

        child.position.set(wx, wy, wz);

        const distToCam = state.camera.position.distanceTo(new THREE.Vector3(wx, wy, wz));
        const fadeStart = 26;
        const fadeEnd = 14;
        let opacityMult = 1.0;
        if (distToCam < fadeStart) {
          opacityMult = Math.max(0.0, (distToCam - fadeEnd) / (fadeStart - fadeEnd));
        }

        const isHovered   = hoveredObject === win.id;
        const targetScale = isHovered ? 1.22 : 1.0;
        child.scale.lerp(new THREE.Vector3(13 * targetScale * Math.max(0.1, opacityMult), 9.75 * targetScale * Math.max(0.1, opacityMult), 1.0), 0.14);

        if (child instanceof THREE.Sprite && child.material instanceof THREE.SpriteMaterial) {
          const baseOpacity = isHovered ? 1.0 : 0.90;
          child.material.opacity += ((baseOpacity * opacityMult) - child.material.opacity) * 0.1;
        }
      });
    }
  });

  return (
    <group ref={groupRef} visible={active}>
      <group ref={windowsGroup}>
        {active && codeWindowsData.map((win) => (
          <sprite
            key={win.id}
            position={[0, 0, 0]}
            scale={[13, 9.75, 1]}
            onPointerOver={(e) => { e.stopPropagation(); setHoveredObject(win.id); }}
            onPointerOut={(e)  => { e.stopPropagation(); setHoveredObject(null); }}
            onClick={(e)       => { e.stopPropagation(); expandCard(win.id); }}
          >
            <spriteMaterial attach="material" map={win.texture} transparent opacity={0.92} />
          </sprite>
        ))}
      </group>
    </group>
  );
}
