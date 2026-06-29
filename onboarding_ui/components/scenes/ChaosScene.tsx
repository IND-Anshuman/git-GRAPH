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

function createRealisticPlanetTexture(): THREE.CanvasTexture {
  const W = 1024, H = 1024;
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, W, H);

  // Placeholder flat background
  ctx.fillStyle = "#b45309";
  ctx.fillRect(0, 0, W, H);

  // Write "YOUR REPO" on the planet
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.font = "bold 48px sans-serif";
  ctx.fillStyle = "#ffffff";
  ctx.fillText("YOUR REPO", W / 2, H / 2);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function ChaosScene({ active, config: _config }: ChaosSceneProps) {
  const groupRef     = useRef<THREE.Group>(null);
  const planetGroup  = useRef<THREE.Group>(null);
  const windowsGroup = useRef<THREE.Group>(null);
  const planetMesh   = useRef<THREE.Mesh>(null);
  const ringMesh     = useRef<THREE.Mesh>(null);

  const [initialized, setInitialized] = useState(false);
  const [planetTex,   setPlanetTex]   = useState<THREE.CanvasTexture | null>(null);

  const shouldAnimate    = useShouldAnimateCamera();
  const qualityTier      = useOnboardingStore((s) => s.qualityTier);
  const hoveredObject    = useOnboardingStore((s) => s.hoveredObjectId);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard       = useOnboardingStore((s) => s.expandCard);

  useEffect(() => { if (active && !initialized) setInitialized(true); }, [active, initialized]);

  useEffect(() => {
    if (!initialized || typeof window === "undefined") return;
    const pTex = createRealisticPlanetTexture();
    setPlanetTex(pTex);
    return () => { pTex.dispose(); };
  }, [initialized]);

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

  useEffect(() => {
    if (!initialized) return;
    const handler = InteractionHandler.getInstance();
    codeWindowsData.forEach((win, i) => {
      handler.registerObject(win.id, PLANET_POS.clone(), 16.0, {
        type: "Code Fragment", title: win.filename,
        description: `A raw source code fragment containing ${win.codeLength} lines, floating in the chaos before semantic compilation.`,
        details: {
          Language: languages[win.lang] || win.lang,
          Complexity: i % 3 === 0 ? "High" : i % 3 === 1 ? "Medium" : "Critical",
          Status: "Orbiting / Untracked",
          Size: `${(win.codeLength * 0.15 + 0.5).toFixed(2)} KB`
        }
      });
    });
    return () => { codeWindowsData.forEach((win) => handler.unregisterObject(win.id)); };
  }, [initialized, codeWindowsData]);

  useEffect(() => {
    return () => { codeWindowsData.forEach((win) => win.texture.dispose()); };
  }, [codeWindowsData]);

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
        InteractionHandler.getInstance().updateObjectPosition(win.id, new THREE.Vector3(wx, wy, wz));

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

    if (planetMesh.current) planetMesh.current.rotation.y = time * 0.05;
    if (ringMesh.current) ringMesh.current.rotation.z = Math.sin(time * 0.18) * 0.03;
    if (groupRef.current) groupRef.current.rotation.y = time * 0.006;
  });

  return (
    <group ref={groupRef} visible={active}>
      <ambientLight color="#2d1b69" intensity={0.50} />
      <directionalLight color="#ffe8c0" intensity={2.2} position={[-40, 50, 60]} />
      <pointLight color="#06b6d4" intensity={1.8} position={[80, 10, -20]} distance={180} decay={1.6} />
      <pointLight color="#7c3aed" intensity={1.2} position={[-30, -30, -50]} distance={130} decay={2.0} />

      <group ref={planetGroup} position={PLANET_POS.toArray() as [number, number, number]}>
        <mesh>
          <sphereGeometry args={[6.2, 32, 32]} />
          <meshStandardMaterial color="#ff8822" transparent opacity={0.14} side={THREE.BackSide} />
        </mesh>

        <mesh ref={planetMesh}>
          <sphereGeometry args={[5.0, 64, 64]} />
          <meshStandardMaterial map={planetTex ?? undefined} roughness={0.72} />
        </mesh>
      </group>

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
