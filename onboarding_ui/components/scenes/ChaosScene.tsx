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

  // Smooth gradient background with warm terracotta, ochre, ivory, and slate tones
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, "#2c223a");
  grad.addColorStop(0.16, "#523c4d");
  grad.addColorStop(0.32, "#7f5145");
  grad.addColorStop(0.46, "#b88a68");
  grad.addColorStop(0.52, "#e5cca8");
  grad.addColorStop(0.60, "#cda583");
  grad.addColorStop(0.74, "#8f5e4c");
  grad.addColorStop(0.88, "#422822");
  grad.addColorStop(1, "#181014");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  // Blended screen cloud overlays
  ctx.save();
  ctx.globalCompositeOperation = "screen";
  ctx.globalAlpha = 0.14;
  for (let i = 0; i < 7; i++) {
    const cx = W * (0.15 + i * 0.12);
    const cy = H * (0.25 + Math.sin(i * 1.5) * 0.16);
    const r = 240 + Math.random() * 160;
    const radGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    radGrad.addColorStop(0, "#ffffff");
    radGrad.addColorStop(0.4, "rgba(255, 235, 205, 0.45)");
    radGrad.addColorStop(1, "transparent");
    ctx.fillStyle = radGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // Blended multiply shadow overlays
  ctx.save();
  ctx.globalCompositeOperation = "multiply";
  ctx.globalAlpha = 0.18;
  for (let i = 0; i < 5; i++) {
    const cx = W * (0.35 + i * 0.14);
    const cy = H * (0.65 + Math.cos(i * 1.2) * 0.12);
    const r = 280;
    const radGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    radGrad.addColorStop(0, "#4a2c20");
    radGrad.addColorStop(0.6, "rgba(74, 44, 32, 0.4)");
    radGrad.addColorStop(1, "transparent");
    ctx.fillStyle = radGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // Soft atmospheric storm spots
  const spotX = W * 0.35, spotY = H * 0.48;
  const spotR = 76;
  ctx.save();
  ctx.globalAlpha = 0.60;
  const spotGrad = ctx.createRadialGradient(spotX - 8, spotY - 8, 0, spotX, spotY, spotR);
  spotGrad.addColorStop(0, "#e88c60");
  spotGrad.addColorStop(0.35, "#be4b29");
  spotGrad.addColorStop(1, "transparent");
  ctx.fillStyle = spotGrad;
  ctx.beginPath();
  ctx.arc(spotX, spotY, spotR, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Terminator shadow
  const shadowGrad = ctx.createLinearGradient(W * 0.48, 0, W, 0);
  shadowGrad.addColorStop(0,   "rgba(0,0,0,0)");
  shadowGrad.addColorStop(0.50, "rgba(0,0,0,0.32)");
  shadowGrad.addColorStop(1,   "rgba(0,0,0,0.85)");
  ctx.fillStyle = shadowGrad;
  ctx.fillRect(0, 0, W, H);

  // Specular highlight
  const specGrad = ctx.createRadialGradient(W * 0.22, H * 0.22, 0, W * 0.28, H * 0.30, W * 0.38);
  specGrad.addColorStop(0,   "rgba(255, 235, 200, 0.45)");
  specGrad.addColorStop(0.3, "rgba(255, 210, 160, 0.18)");
  specGrad.addColorStop(1,   "rgba(0,0,0,0)");
  ctx.fillStyle = specGrad;
  ctx.fillRect(0, 0, W, H);

  // ── 7. "YOUR REPO" label overlay ──
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const lx = W * 0.35; // label center x
  const ly = H * 0.50; // label center y

  // Semi-transparent tag backing
  ctx.save();
  ctx.globalAlpha = 0.55;
  ctx.fillStyle = "rgba(10, 5, 25, 0.7)";
  const tagW = 320, tagH = 130;
  if (ctx.roundRect) ctx.roundRect(lx - tagW/2, ly - tagH/2, tagW, tagH, 12);
  else ctx.rect(lx - tagW/2, ly - tagH/2, tagW, tagH);
  ctx.fill();
  ctx.restore();

  // Tag border
  ctx.strokeStyle = "rgba(167, 139, 250, 0.60)";
  ctx.lineWidth = 2;
  if (ctx.roundRect) ctx.roundRect(lx - tagW/2, ly - tagH/2, tagW, tagH, 12);
  else ctx.rect(lx - tagW/2, ly - tagH/2, tagW, tagH);
  ctx.stroke();

  // Small mono caption
  ctx.font = "bold 22px 'Courier New', monospace";
  ctx.fillStyle = "rgba(196, 181, 253, 0.82)";
  ctx.shadowColor = "rgba(168,85,247,0.6)";
  ctx.shadowBlur = 10;
  ctx.fillText("// UNCOMPILED", lx, ly - 44);

  // "YOUR REPO" two-line headline
  ctx.shadowBlur = 22;
  ctx.shadowColor = "rgba(168, 85, 247, 1.0)";

  // "YOUR"
  const tg1 = ctx.createLinearGradient(lx - 110, ly - 14, lx + 110, ly + 6);
  tg1.addColorStop(0, "#e9d5ff");
  tg1.addColorStop(0.5, "#ffffff");
  tg1.addColorStop(1, "#c4b5fd");
  ctx.font = "bold 64px 'Arial Black', 'Arial', sans-serif";
  ctx.fillStyle = tg1;
  ctx.fillText("YOUR", lx, ly - 12);

  // "REPO"
  ctx.shadowBlur = 16;
  const tg2 = ctx.createLinearGradient(lx - 80, ly + 36, lx + 80, ly + 56);
  tg2.addColorStop(0, "#a78bfa");
  tg2.addColorStop(0.5, "#ddd6fe");
  tg2.addColorStop(1, "#818cf8");
  ctx.font = "bold 64px 'Arial Black', 'Arial', sans-serif";
  ctx.fillStyle = tg2;
  ctx.fillText("REPO", lx, ly + 44);

  ctx.shadowBlur = 0;

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.ClampToEdgeWrapping;
  tex.needsUpdate = true;
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

  // Generate textures
  useEffect(() => {
    if (!initialized || typeof window === "undefined") return;
    const pTex = createRealisticPlanetTexture();
    setPlanetTex(pTex);
    return () => { pTex.dispose(); };
  }, [initialized]);

  // Code block count by quality
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

  // Register interactions
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

  // Dispose
  useEffect(() => {
    return () => { codeWindowsData.forEach((win) => win.texture.dispose()); document.body.style.cursor = "auto"; };
  }, [codeWindowsData]);

  // Frame loop
  useFrame((state) => {
    if (!active || !initialized || !shouldAnimate) return;
    const time = state.clock.getElapsedTime();

    // Floating scattered code blocks around the PLANET_POS offset
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

    // Planet slow self-rotation (Y axis = spin)
    if (planetMesh.current) {
      planetMesh.current.rotation.y = time * 0.05;
    }

    // Equatorial ring slow tilt wobble
    if (ringMesh.current) {
      ringMesh.current.rotation.z = Math.sin(time * 0.18) * 0.03;
    }

    // Slow overall group drift
    if (groupRef.current) {
      groupRef.current.rotation.y = time * 0.006;
    }
  });

  return (
    <group ref={groupRef} visible={active}>
      {/* ── Lighting ── */}
      <ambientLight color="#2d1b69" intensity={0.50} />
      <directionalLight color="#ffe8c0" intensity={2.2} position={[-40, 50, 60]} />
      <pointLight color="#06b6d4" intensity={1.8} position={[80, 10, -20]} distance={180} decay={1.6} />
      <pointLight color="#7c3aed" intensity={1.2} position={[-30, -30, -50]} distance={130} decay={2.0} />
      <pointLight color="#f59e0b" intensity={1.5} position={[PLANET_POS.x - 20, PLANET_POS.y + 20, PLANET_POS.z + 30]} distance={80} decay={1.8} />

      {/* ── Planet group ── */}
      <group ref={planetGroup} position={PLANET_POS.toArray() as [number, number, number]}>

        {/* Outer atmosphere halo (back-side glow) */}
        <mesh>
          <sphereGeometry args={[6.2, 32, 32]} />
          <meshStandardMaterial
            color="#ff8822"
            emissive="#cc5500"
            emissiveIntensity={0.30}
            transparent opacity={0.14}
            roughness={1}
            side={THREE.BackSide}
          />
        </mesh>

        {/* Thin bright atmosphere rim */}
        <mesh>
          <sphereGeometry args={[5.38, 32, 32]} />
          <meshStandardMaterial
            color="#ffcc88"
            emissive="#ff9900"
            emissiveIntensity={0.18}
            transparent opacity={0.22}
            roughness={1}
            side={THREE.BackSide}
          />
        </mesh>

        {/* ── Main planet body ── */}
        <mesh ref={planetMesh}>
          <sphereGeometry args={[5.0, 64, 64]} />
          <meshStandardMaterial
            map={planetTex ?? undefined}
            color={planetTex ? "#ffffff" : "#b45309"}
            roughness={0.72}
            metalness={0.04}
            envMapIntensity={0.5}
          />
        </mesh>

        {/* Inner core glow */}
        <mesh>
          <sphereGeometry args={[1.6, 16, 16]} />
          <meshStandardMaterial
            color="#ffddaa"
            emissive="#ff9922"
            emissiveIntensity={2.5}
            transparent opacity={0.55}
          />
        </mesh>
      </group>

      {/* ── Floating Code Editor Windows ── */}
      <group ref={windowsGroup}>
        {active && codeWindowsData.map((win) => (
          <sprite
            key={win.id}
            position={[0, 0, 0]}
            scale={[13, 9.75, 1]}
            onPointerOver={(e) => { e.stopPropagation(); setHoveredObject(win.id); document.body.style.cursor = "pointer"; }}
            onPointerOut={(e)  => { e.stopPropagation(); setHoveredObject(null); document.body.style.cursor = "auto"; }}
            onClick={(e)       => { e.stopPropagation(); expandCard(win.id); }}
          >
            <spriteMaterial attach="material" map={win.texture} transparent opacity={0.92} />
          </sprite>
        ))}
      </group>
    </group>
  );
}
