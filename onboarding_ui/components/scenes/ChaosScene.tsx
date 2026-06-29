"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { ParticleSystemEngine, ParticleGroup } from "@/lib/ParticleSystemEngine";
import { ParticleAnimator } from "@/lib/ParticleAnimator";
import { ParticleLODManager } from "@/lib/ParticleLOD";
import { CodeSnippetRenderer } from "@/lib/CodeSnippetRenderer";
import { InteractionHandler } from "@/lib/InteractionHandler";
import { SceneConfig } from "@/types";
import * as THREE from "three";

interface ChaosSceneProps {
  active: boolean;
  config: SceneConfig;
}

const languages: Record<string, string> = {
  typescript: "TypeScript",
  python: "Python",
  javascript: "JavaScript",
  go: "Go",
  html: "HTML",
  java: "Java",
  ruby: "Ruby",
  sql: "SQL",
  css: "CSS",
  tf: "Terraform",
  yml: "YAML",
  json: "JSON",
  md: "Markdown"
};

const snippets = [
  { filename: "auth.service.ts", lang: "typescript", code: ["export class AuthService {", "  async login(cred) {", "    const t = await validate(cred);", "    return this.session(t);", "  }", "}"] },
  { filename: "user.py", lang: "python", code: ["class User(Model):", "    email = EmailField(unique=True)", "    name = CharField(max_length=100)", "    def check(self, pw):", "        return hash(pw)", "    "] },
  { filename: "checkout.js", lang: "javascript", code: ["function process(cart) {", "  const tot = cart.items.reduce(", "    (s, i) => s + i.price, 0", "  );", "  return stripe.charge(tot);", "}"] },
  { filename: "app.go", lang: "go", code: ["func main() {", "\tr := gin.Default()", "\tr.GET(\"/ping\", func(c *gin.Context) {", "\t\tc.JSON(200, gin.H{\"msg\": \"pong\"})", "\t})", "\tr.Run()", "}"] },
  { filename: "index.html", lang: "html", code: ["<!DOCTYPE html>", "<html>", "<head>", "  <title>App</title>", "</head>", "<body>"] },
  { filename: "order.java", lang: "java", code: ["@RestController", "public class OrderController {", "  @PostMapping(\"/orders\")", "  public Order create(@RequestBody Cart cart) {", "    return orderService.place(cart);", "  }", "}"] },
  { filename: "payment.rb", lang: "ruby", code: ["class PaymentProcessor", "  def self.charge(amount, token)", "    Stripe::Charge.create(", "      amount: amount,", "      currency: 'usd',", "      source: token", "    )", "  end", "end"] },
  { filename: "db.sql", lang: "sql", code: ["CREATE TABLE users (", "  id SERIAL PRIMARY KEY,", "  email VARCHAR(255) UNIQUE,", "  password_hash TEXT,", "  created_at TIMESTAMP DEFAULT NOW()", ");"] },
  { filename: "styles.css", lang: "css", code: [".nebula-particle {", "  mix-blend-mode: screen;", "  filter: blur(4px);", "  animation: drift 10s ease infinite;", "  opacity: 0.85;", "}"] },
  { filename: "config.tf", lang: "tf", code: ["resource \"aws_instance\" \"web\" {", "  ami           = data.aws_ami.ubuntu.id", "  instance_type = \"t3.micro\"", "  tags = {", "    Name = \"git-graph-node\"", "  }", "}"] },
  { filename: "redis.cache.ts", lang: "typescript", code: ["export class RedisCache {", "  async get(key: string): Promise<string | null> {", "    return this.client.get(key);", "  }", "  async set(key: string, val: string): Promise<void> {", "    await this.client.setEx(key, 3600, val);", "  }", "}"] },
  { filename: "api.routes.ts", lang: "typescript", code: ["import { Router } from 'express';", "const router = Router();", "router.get('/health', (req, res) => {", "  res.status(200).json({ status: 'UP' });", "});", "export default router;"] },
  { filename: "docker-compose.yml", lang: "yml", code: ["version: '3.8'", "services:", "  db:", "    image: postgres:15-alpine", "    environment:", "      POSTGRES_DB: git_graph", "    ports:", "      - \"5432:5432\""] },
  { filename: "package.json", lang: "json", code: ["{", "  \"name\": \"git-graph\",", "  \"dependencies\": {", "    \"three\": \"^0.185.0\",", "    \"react\": \"^19.2.0\"", "  }", "}"] },
  { filename: "auth.middleware.go", lang: "go", code: ["func AuthMiddleware() gin.HandlerFunc {", "  return func(c *gin.Context) {", "    token := c.GetHeader(\"Authorization\")", "    if token == \"\" {", "      c.AbortWithStatus(401)", "      return", "    }", "    c.Next()", "  }", "}"] },
  { filename: "README.md", lang: "md", code: ["# Software Intelligence Platform", "This experience visualizes the platform pipeline:", "Source Code -> SEEE -> Semantic Compiler", "## Architecture Layers", "- Domain layer", "- Capability layer"] }
];

const filenames = [
  "user.py", "auth.service.ts", "checkout.js", "config.tf",
  "redis.cache.ts", "order.controller.java", "payment.rb",
  "database.sql", "api.routes.ts", "styles.css", "index.html",
  "main.go", "routes.ts", "db.sql", "config.yml", "test.py",
  "middleware.ts", "index.js", "setup.py", "types.ts",
  "package.json", "next.config.js", "dockerfile", "app.css", "utils.js"
];

export function ChaosScene({ active, config }: ChaosSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const windowsGroupRef = useRef<THREE.Group>(null);
  const badgesGroupRef = useRef<THREE.Group>(null);
  
  const [initialized, setInitialized] = useState(false);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);
  const setHoveredObject = useOnboardingStore((s) => s.setHoveredObject);
  const expandCard = useOnboardingStore((s) => s.expandCard);

  // States for particle systems
  const [nebulaSystem, setNebulaSystem] = useState<ParticleGroup | null>(null);
  const [explosionCore, setExplosionCore] = useState<ParticleGroup | null>(null);

  // Lazy Initialization
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
    }
  }, [active, initialized]);

  // Dynamic scaling limits based on active Quality Tier (keeps VRAM and draw calls in check on 1GB GPUs)
  const counts = useMemo(() => {
    switch (qualityTier) {
      case "low":
        return { windows: 4, badges: 8 };
      case "medium":
        return { windows: 6, badges: 12 };
      case "high":
        return { windows: 9, badges: 18 };
      case "ultra":
      default:
        return { windows: 12, badges: 25 };
    }
  }, [qualityTier]);

  // Generate Snippets and Badges data once on initialization and re-evaluate dynamically on quality change
  const codeWindowsData = useMemo(() => {
    if (!initialized || typeof window === "undefined") return [];
    const renderer = new CodeSnippetRenderer();
    const data = [];
    const windowCount = counts.windows;
    for (let i = 0; i < windowCount; i++) {
      const snip = snippets[i % snippets.length];
      const tex = renderer.renderCodeSnippet(snip.filename, snip.code, snip.lang);
      const pos = new THREE.Vector3(
        (Math.random() - 0.5) * 200,
        (Math.random() - 0.5) * 150,
        (Math.random() - 0.5) * 200
      );
      data.push({
        id: `scene-1-window-${i}`,
        filename: snip.filename,
        lang: snip.lang,
        codeLength: snip.code.length,
        texture: tex,
        position: pos
      });
    }
    return data;
  }, [initialized, counts.windows]);

  const filenameBadgesData = useMemo(() => {
    if (!initialized || typeof window === "undefined") return [];
    const renderer = new CodeSnippetRenderer();
    const data = [];
    const badgeCount = counts.badges;
    for (let i = 0; i < badgeCount; i++) {
      const fn = filenames[i % filenames.length];
      const tex = renderer.renderFilenameBadge(fn);
      const pos = new THREE.Vector3(
        (Math.random() - 0.5) * 250,
        (Math.random() - 0.5) * 180,
        (Math.random() - 0.5) * 250
      );
      const ext = fn.split(".").pop() || "";
      data.push({
        id: `scene-1-badge-${i}`,
        filename: fn,
        ext,
        texture: tex,
        position: pos
      });
    }
    return data;
  }, [initialized, counts.badges]);

  // Register interactive items in InteractionHandler for raycast queries
  useEffect(() => {
    if (!initialized) return;
    const handler = InteractionHandler.getInstance();

    codeWindowsData.forEach((win) => {
      handler.registerObject(win.id, win.position, 15.0, {
        type: "Code Fragment",
        title: win.filename,
        description: `A floating, raw source code fragment containing ${win.codeLength} lines of syntax-highlighted syntax, drifting in complexity.`,
        details: {
          Language: languages[win.lang] || win.lang,
          Complexity: win.id.charCodeAt(win.id.length - 1) % 3 === 0 ? "High" : win.id.charCodeAt(win.id.length - 1) % 3 === 1 ? "Medium" : "Critical",
          Status: win.id.charCodeAt(win.id.length - 1) % 2 === 0 ? "Legacy / Untracked" : "Drifting",
          Size: `${(win.codeLength * 0.15 + 0.5).toFixed(2)} KB`
        }
      });
    });

    filenameBadgesData.forEach((badge) => {
      handler.registerObject(badge.id, badge.position, 7.5, {
        type: "File Badge",
        title: badge.filename,
        description: `An untracked source file badge drifting in the workspace. Part of the 10,231 legacy files in this repository.`,
        details: {
          Extension: badge.ext.toUpperCase() || "Unknown",
          Type: badge.ext === "yml" || badge.ext === "json" ? "Configuration" : "Source Code",
          Owner: badge.id.charCodeAt(badge.id.length - 1) % 4 === 0 ? "Git-Graph Agent" : "Legacy Importer"
        }
      });
    });

    return () => {
      codeWindowsData.forEach((win) => handler.unregisterObject(win.id));
      filenameBadgesData.forEach((badge) => handler.unregisterObject(badge.id));
    };
  }, [initialized, codeWindowsData, filenameBadgesData]);

  // Texture and material disposal on unmount
  useEffect(() => {
    return () => {
      codeWindowsData.forEach((win) => win.texture.dispose());
      filenameBadgesData.forEach((badge) => badge.texture.dispose());
      document.body.style.cursor = "auto";
    };
  }, [codeWindowsData, filenameBadgesData]);

  // Initialize Particles (Nebula + Core)
  useEffect(() => {
    if (!initialized) return;

    const engine = ParticleSystemEngine.getInstance();
    const animator = ParticleAnimator.getInstance();

    // 1. Create Consolidated Nebula System
    const nebula = engine.createParticles("scene-1-nebula-unified", {
      enabled: true,
      count: { ultra: 600, high: 400, medium: 250, low: 80 },
      geometry: { type: "plane", size: 1.0 },
      material: { color: "#3b0764", opacity: 0.4, transparent: true },
      behavior: {
        animation: "nebula" as any,
        drift: {
          velocity: [new THREE.Vector3(-0.02, -0.01, -0.02), new THREE.Vector3(0.02, 0.01, 0.02)],
          turbulence: 2.2
        }
      },
      initialDistribution: {
        type: "sphere",
        size: 150.0
      } as any
    });

    // Populate Custom Instance Attributes for size, phase and cloud type
    const count = nebula.count;
    const sizes = new Float32Array(count);
    const cloudTypes = new Float32Array(count);
    const phases = new Float32Array(count);
    const positions = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      phases[i] = Math.random() * 200.0;

      // 0.0 = Background Large, 1.0 = Mid Gas, 2.0 = Twinkling Star
      const typeRand = Math.random();
      if (typeRand < 0.25) {
        cloudTypes[i] = 0.0; // Large background
        sizes[i] = Math.random() * 50.0 + 30.0;
      } else if (typeRand < 0.60) {
        cloudTypes[i] = 1.0; // Mid orange/pink gas
        sizes[i] = Math.random() * 24.0 + 15.0;
      } else {
        cloudTypes[i] = 2.0; // Sharp twinkling stars
        sizes[i] = Math.random() * 2.8 + 0.8;
      }

      // Chaotic sphere distribution biased towards center
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const radiusDecay = Math.pow(Math.random(), 2.5); // Exponential decay
      const radius = radiusDecay * 140.0;

      positions[i * 3 + 0] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);
    }

    // Attach custom float attributes to the LOD meshes
    Object.values(nebula.lodMeshes).forEach((mesh) => {
      mesh.geometry.setAttribute("aCustomSize", new THREE.InstancedBufferAttribute(sizes, 1));
      mesh.geometry.setAttribute("aCloudType", new THREE.InstancedBufferAttribute(cloudTypes, 1));
      mesh.geometry.setAttribute("aInitialPosition", new THREE.InstancedBufferAttribute(positions, 3));
    });

    setNebulaSystem(nebula);

    // 2. Create Explosion Core System
    const core = engine.createParticles("scene-1-explosion-core", {
      enabled: true,
      count: { ultra: 1000, high: 700, medium: 500, low: 250 },
      geometry: { type: "sphere", size: 0.35 },
      material: { color: "#f97316", opacity: 0.9, transparent: true },
      behavior: {
        animation: "explosion",
        explosion: {
          origin: [0, 0, 0],
          force: [8.0, 15.0],
          gravity: [0, 0, 0],
          damping: 0.18
        }
      },
      initialDistribution: {
        type: "sphere",
        size: 8.0 // Tightly bound center core
      } as any
    });

    // Randomize initial scale and apply orange-to-white color gradient to explosion core
    const coreCount = core.count;
    const orange = new THREE.Color("#f97316");
    const white = new THREE.Color("#ffffff");
    const tempCol = new THREE.Color();
    const tempMatrix = new THREE.Matrix4();
    const tempPos = new THREE.Vector3();
    const tempQuat = new THREE.Quaternion();
    const tempScale = new THREE.Vector3();

    Object.values(core.lodMeshes).forEach((mesh) => {
      for (let i = 0; i < coreCount; i++) {
        // Color gradient interpolation
        tempCol.copy(orange).lerp(white, Math.random());
        mesh.setColorAt(i, tempCol);

        // Scale variation (1 to 5 units)
        mesh.getMatrixAt(i, tempMatrix);
        tempMatrix.decompose(tempPos, tempQuat, tempScale);
        const randScale = Math.random() * 4.0 + 1.0;
        tempScale.set(randScale, randScale, randScale);
        tempMatrix.compose(tempPos, tempQuat, tempScale);
        mesh.setMatrixAt(i, tempMatrix);
      }
      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    });

    setExplosionCore(core);

    // Play animator sequences
    animator.play("scene-1-nebula-unified", { type: "nebula" as any, loop: true });
    animator.play("scene-1-explosion-core", { type: "explosion", loop: false });

    return () => {
      animator.stop("scene-1-nebula-unified");
      animator.stop("scene-1-explosion-core");
      engine.destroyParticles("scene-1-nebula-unified");
      engine.destroyParticles("scene-1-explosion-core");
    };
  }, [initialized, config, qualityTier]);

  // Sync Pause/Resume
  useEffect(() => {
    if (!initialized) return;
    const animator = ParticleAnimator.getInstance();
    if (shouldAnimate) {
      animator.resume("scene-1-nebula-unified");
      animator.resume("scene-1-explosion-core");
    } else {
      animator.pause("scene-1-nebula-unified");
      animator.pause("scene-1-explosion-core");
    }
  }, [shouldAnimate, initialized]);

  // Frame loop animations
  useFrame((state, delta) => {
    if (!active || !initialized || !shouldAnimate) return;

    const camera = state.camera;
    const lod = ParticleLODManager.getInstance();

    // 1. Update LOD and culling for custom particle groups
    if (nebulaSystem) lod.updateLOD(nebulaSystem, camera);
    if (explosionCore) lod.updateLOD(explosionCore, camera);

    // 2. Slow spin rotation of the entire galaxy on the Z-axis
    if (groupRef.current) {
      groupRef.current.rotation.z = state.clock.getElapsedTime() * 0.025;
    }

    // 3. Animate float code windows and filename badges (drift-free, frame rate independent)
    const time = state.clock.getElapsedTime();

    if (windowsGroupRef.current) {
      windowsGroupRef.current.children.forEach((child, idx) => {
        const win = codeWindowsData[idx];
        if (win) {
          child.position.y = win.position.y + Math.sin(time * 0.8 + idx) * 1.5;
          if (child instanceof THREE.Sprite && child.material instanceof THREE.SpriteMaterial) {
            child.material.rotation += delta * 0.05;
          }
        }
      });
    }

    if (badgesGroupRef.current) {
      badgesGroupRef.current.children.forEach((child, idx) => {
        const badge = filenameBadgesData[idx];
        if (badge) {
          child.position.y = badge.position.y + Math.sin(time * 0.8 + idx + 10) * 1.0;
          if (child instanceof THREE.Sprite && child.material instanceof THREE.SpriteMaterial) {
            child.material.rotation += delta * 0.05;
          }
        }
      });
    }
  });

  return (
    <group ref={groupRef} visible={active}>
      {/* Dynamic Lighting */}
      <ambientLight color="#8B5CF6" intensity={0.4} />
      <pointLight color="#FF9955" intensity={3.5} position={[0, 0, 0]} distance={150} />
      <directionalLight color="#EC4899" intensity={1.8} position={[40, 40, 40]} />

      {/* Render GPU Instanced Systems */}
      {nebulaSystem && <primitive object={nebulaSystem.container} />}
      {explosionCore && <primitive object={explosionCore.container} />}

      {/* Render Code Editor Windows (Interactive via R3F) */}
      <group ref={windowsGroupRef}>
        {active && codeWindowsData.map((win) => (
          <sprite
            key={win.id}
            position={win.position}
            scale={[30, 22.5, 1]}
            onPointerOver={(e) => {
              e.stopPropagation();
              setHoveredObject(win.id);
              document.body.style.cursor = "pointer";
            }}
            onPointerOut={(e) => {
              e.stopPropagation();
              setHoveredObject(null);
              document.body.style.cursor = "auto";
            }}
            onClick={(e) => {
              e.stopPropagation();
              expandCard(win.id);
            }}
          >
            <spriteMaterial attach="material" map={win.texture} transparent opacity={0.9} />
          </sprite>
        ))}
      </group>

      {/* Render Filename Badges (Interactive via R3F) */}
      <group ref={badgesGroupRef}>
        {active && filenameBadgesData.map((badge) => (
          <sprite
            key={badge.id}
            position={badge.position}
            scale={[15, 3.75, 1]}
            onPointerOver={(e) => {
              e.stopPropagation();
              setHoveredObject(badge.id);
              document.body.style.cursor = "pointer";
            }}
            onPointerOut={(e) => {
              e.stopPropagation();
              setHoveredObject(null);
              document.body.style.cursor = "auto";
            }}
            onClick={(e) => {
              e.stopPropagation();
              expandCard(badge.id);
            }}
          >
            <spriteMaterial attach="material" map={badge.texture} transparent opacity={0.8} />
          </sprite>
        ))}
      </group>
    </group>
  );
}
