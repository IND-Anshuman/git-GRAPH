"use client";

import { useRef, useEffect, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { ParticleSystemEngine, ParticleGroup } from "@/lib/ParticleSystemEngine";
import { ParticleAnimator } from "@/lib/ParticleAnimator";
import { ParticleLODManager } from "@/lib/ParticleLOD";
import { CodeSnippetRenderer } from "@/lib/CodeSnippetRenderer";
import { SceneConfig } from "@/types";
import * as THREE from "three";

interface ChaosSceneProps {
  active: boolean;
  config: SceneConfig;
}

export function ChaosScene({ active, config }: ChaosSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [initialized, setInitialized] = useState(false);
  const shouldAnimate = useShouldAnimateCamera();
  const qualityTier = useOnboardingStore((s) => s.qualityTier);

  // States for particle systems
  const [nebulaSystem, setNebulaSystem] = useState<ParticleGroup | null>(null);
  const [explosionCore, setExplosionCore] = useState<ParticleGroup | null>(null);
  const [codeSprites, setCodeSprites] = useState<THREE.Sprite[]>([]);

  // Lazy Initialization
  useEffect(() => {
    if (active && !initialized) {
      setInitialized(true);
    }
  }, [active, initialized]);

  useEffect(() => {
    if (!initialized) return;

    const engine = ParticleSystemEngine.getInstance();
    const animator = ParticleAnimator.getInstance();

    // 1. Create Consolidated Nebula System
    const nebula = engine.createParticles("scene-1-nebula-unified", {
      enabled: true,
      count: { ultra: 25000, high: 16000, medium: 9000, low: 4500 },
      geometry: { type: "plane", size: 1.0 },
      material: { color: "#8b5cf6", opacity: 0.8, transparent: true },
      behavior: {
        animation: "nebula" as any, // binds to new custom nebula shader
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
        sizes[i] = Math.random() * 18.0 + 12.0;
      } else if (typeRand < 0.60) {
        cloudTypes[i] = 1.0; // Mid orange/pink gas
        sizes[i] = Math.random() * 9.0 + 5.0;
      } else {
        cloudTypes[i] = 2.0; // Sharp twinkling stars
        sizes[i] = Math.random() * 1.5 + 0.6;
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

    setExplosionCore(core);

    // Play animator sequences
    animator.play("scene-1-nebula-unified", { type: "nebula" as any, loop: true });
    animator.play("scene-1-explosion-core", { type: "explosion", loop: false });

    // 3. Create Code Snippet Windows & Filename Badges
    const renderer = new CodeSnippetRenderer();
    const sprites: THREE.Sprite[] = [];

    const snippets = [
      { filename: "auth.service.ts", lang: "typescript", code: ["export class AuthService {", "  async login(cred) {", "    const t = await validate(cred);", "    return this.session(t);", "  }", "}"] },
      { filename: "user.py", lang: "python", code: ["class User(Model):", "    email = EmailField(unique=True)", "    name = CharField(max_length=100)", "    def check(self, pw):", "        return hash(pw)", "    "] },
      { filename: "checkout.js", lang: "javascript", code: ["function process(cart) {", "  const tot = cart.items.reduce(", "    (s, i) => s + i.price, 0", "  );", "  return stripe.charge(tot);", "}"] },
      { filename: "app.go", lang: "go", code: ["func main() {", "\tr := gin.Default()", "\tr.GET(\"/ping\", func(c *gin.Context) {", "\t\tc.JSON(200, gin.H{\"msg\": \"pong\"})", "\t})", "\tr.Run()", "}"] },
      { filename: "index.html", lang: "html", code: ["<!DOCTYPE html>", "<html>", "<head>", "  <title>App</title>", "</head>", "<body>"] }
    ];

    // Build 8 Code Windows
    for (let i = 0; i < 8; i++) {
      const snip = snippets[i % snippets.length];
      const tex = renderer.renderCodeSnippet(snip.filename, snip.code, snip.lang);
      const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.85 });
      const sprite = new THREE.Sprite(mat);

      sprite.position.set((Math.random() - 0.5) * 110, (Math.random() - 0.5) * 70, (Math.random() - 0.5) * 110);
      sprite.scale.set(16, 12, 1); // 4:3 aspect ratio
      sprites.push(sprite);
      groupRef.current?.add(sprite);
    }

    // Build 15 Filename Badges
    const filenames = ["redis.ts", "order.java", "payment.rb", "api.ts", "styles.css", "main.go", "config.yml", "db.sql", "routes.ts", "index.js", "setup.py", "test.py", "dockerfile", "package.json", "next.config.js"];
    for (let i = 0; i < 15; i++) {
      const fn = filenames[i % filenames.length];
      const tex = renderer.renderFilenameBadge(fn);
      const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.75 });
      const sprite = new THREE.Sprite(mat);

      sprite.position.set((Math.random() - 0.5) * 150, (Math.random() - 0.5) * 90, (Math.random() - 0.5) * 150);
      sprite.scale.set(8, 2.0, 1); // 4:1 aspect ratio
      sprites.push(sprite);
      groupRef.current?.add(sprite);
    }

    setCodeSprites(sprites);

    return () => {
      animator.stop("scene-1-nebula-unified");
      animator.stop("scene-1-explosion-core");
      engine.destroyParticles("scene-1-nebula-unified");
      engine.destroyParticles("scene-1-explosion-core");

      // Dispose of Canvas Textures and Materials
      sprites.forEach((sp) => {
        if (sp.material.map) sp.material.map.dispose();
        sp.material.dispose();
      });
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

    // 3. Animate float code windows and filename badges
    codeSprites.forEach((sp, idx) => {
      sp.position.y += Math.sin(state.clock.getElapsedTime() + idx) * 0.005;
      sp.material.rotation += delta * 0.025;
    });
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
    </group>
  );
}
