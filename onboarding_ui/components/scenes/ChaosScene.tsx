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
  { filename: "index.html",      lang: "html",       code: ["<!DOCTYPE html>", "<html>", "<head>", "  <title>App</title>", "</head>", "<body>"] },
  { filename: "order.java",      lang: "java",       code: ["@RestController", "public class OrderController {", "  @PostMapping(\"/orders\")", "  public Order create(@RequestBody Cart cart) {", "    return orderService.place(cart);", "  }", "}"] },
  { filename: "payment.rb",      lang: "ruby",       code: ["class PaymentProcessor", "  def self.charge(amount, token)", "    Stripe::Charge.create(", "      amount: amount,", "      currency: 'usd',", "      source: token", "    )", "  end", "end"] },
  { filename: "db.sql",          lang: "sql",        code: ["CREATE TABLE users (", "  id SERIAL PRIMARY KEY,", "  email VARCHAR(255) UNIQUE,", "  password_hash TEXT,", "  created_at TIMESTAMP DEFAULT NOW()", ");"] },
  { filename: "styles.css",      lang: "css",        code: [".nebula-particle {", "  mix-blend-mode: screen;", "  filter: blur(4px);", "  animation: drift 10s ease infinite;", "  opacity: 0.85;", "}"] },
  { filename: "config.tf",       lang: "tf",         code: ["resource \"aws_instance\" \"web\" {", "  ami           = data.aws_ami.ubuntu.id", "  instance_type = \"t3.micro\"", "  tags = {", "    Name = \"git-graph-node\"", "  }", "}"] },
  { filename: "redis.cache.ts",  lang: "typescript", code: ["export class RedisCache {", "  async get(key: string): Promise<string | null> {", "    return this.client.get(key);", "  }", "  async set(key: string, val: string): Promise<void> {", "    await this.client.setEx(key, 3600, val);", "  }", "}"] },
  { filename: "api.routes.ts",   lang: "typescript", code: ["import { Router } from 'express';", "const router = Router();", "router.get('/health', (req, res) => {", "  res.status(200).json({ status: 'UP' });", "});", "export default router;"] },
  { filename: "docker-compose.yml", lang: "yml",    code: ["version: '3.8'", "services:", "  db:", "    image: postgres:15-alpine", "    environment:", "      POSTGRES_DB: git_graph", "    ports:", "      - \"5432:5432\""] },
  { filename: "package.json",    lang: "json",       code: ["{", "  \"name\": \"git-graph\",", "  \"dependencies\": {", "    \"three\": \"^0.185.0\",", "    \"react\": \"^19.2.0\"", "  }", "}"] },
  { filename: "auth.middleware.go", lang: "go",     code: ["func AuthMiddleware() gin.HandlerFunc {", "  return func(c *git.Context) {", "    token := c.GetHeader(\"Authorization\")", "    if token == \"\" {", "      c.AbortWithStatus(401)", "      return", "    }", "    c.Next()", "  }", "}"] },
  { filename: "README.md",       lang: "md",         code: ["# Software Intelligence Platform", "This experience visualizes:", "Source Code -> SEEE -> Semantic Compiler", "## Architecture Layers", "- Domain layer", "- Capability layer"] },
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

  // Simple band gradients for initial commit
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, "#2c223a");
  grad.addColorStop(0.32, "#7f5145");
  grad.addColorStop(0.52, "#e5cca8");
  grad.addColorStop(0.74, "#8f5e4c");
  grad.addColorStop(1, "#181014");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  // Write "YOUR REPO" on the planet initially
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  const lx = W * 0.35, ly = H * 0.50;
  ctx.font = "bold 64px sans-serif";
  ctx.fillStyle = "#ffffff";
  ctx.fillText("YOUR REPO", lx, ly);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.ClampToEdgeWrapping;
  tex.needsUpdate = true;
  return tex;
}

function createRingTexture(): THREE.CanvasTexture {
  const size = 512;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, size, size);

  const cx = size / 2, cy = size / 2;
  const maxR = size / 2 - 4;
  const minR = maxR * (6.2 / 9.8);

  ctx.fillStyle = "rgba(165, 135, 95, 0.4)";
  ctx.beginPath();
  ctx.arc(cx, cy, maxR, 0, Math.PI * 2);
  ctx.arc(cx, cy, minR, 0, Math.PI * 2, true);
  ctx.fill();

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
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
  const [ringTex,     setRingTex]     = useState<THREE.CanvasTexture | null>(null);

  const shouldAnimate    = useShouldAnimateCamera();
  const qualityTier      = useOnboardingStore((s) => s.qualityTier);
  const hoveredObject    = useOnboardingStore((s) => s.hoveredObjectId);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard       = useOnboardingStore((s) => s.expandCard);

  useEffect(() => { if (active && !initialized) setInitialized(true); }, [active, initialized]);

  useEffect(() => {
    if (!initialized || typeof window === "undefined") return;
    const pTex = createRealisticPlanetTexture();
    const rTex = createRingTexture();
    setPlanetTex(pTex);
    setRingTex(rTex);
    return () => {
      pTex.dispose();
      rTex.dispose();
    };
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
        description: `A raw source code fragment.`,
        details: { Language: languages[win.lang] || win.lang }
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

        const isHovered   = hoveredObject === win.id;
        const targetScale = isHovered ? 1.22 : 1.0;
        child.scale.lerp(new THREE.Vector3(13 * targetScale, 9.75 * targetScale, 1.0), 0.14);
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

      <group ref={planetGroup} position={PLANET_POS.toArray() as [number, number, number]}>
        <mesh ref={planetMesh}>
          <sphereGeometry args={[5.0, 64, 64]} />
          <meshStandardMaterial map={planetTex ?? undefined} roughness={0.72} />
        </mesh>

        <mesh ref={ringMesh} rotation={[Math.PI / 2 - 0.38, 0.12, 0]}>
          <ringGeometry args={[6.2, 9.8, 128]} />
          <meshBasicMaterial map={ringTex ?? undefined} transparent opacity={0.88} side={THREE.DoubleSide} />
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
