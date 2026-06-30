"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { useOnboardingStore, useShouldAnimateCamera } from "@/stores/onboardingStore";
import { CodeSnippetRenderer } from "@/lib/CodeSnippetRenderer";
import { SceneConfig } from "@/types";
import * as THREE from "three";
import { Html } from "@react-three/drei";

interface StardustSceneProps {
  active: boolean;
  config: SceneConfig;
}

// Procedural glow texture generator
function createGlowingParticleTexture(): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  
  ctx.clearRect(0, 0, 128, 128);
  const grad = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  grad.addColorStop(0, "rgba(255, 255, 255, 1.0)");
  grad.addColorStop(0.15, "rgba(255, 255, 255, 0.95)");
  grad.addColorStop(0.4, "rgba(255, 255, 255, 0.25)");
  grad.addColorStop(1.0, "rgba(255, 255, 255, 0.0)");
  
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 128, 128);
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

// Math for Bezier curve with scattered start that decays into a unified thick core
function getPointOnCurve(
  pStart: THREE.Vector3,
  pEnd: THREE.Vector3,
  clusterIdx: number,
  t: number,
  time: number,
  curveIdx: number
): THREE.Vector3 {
  // Center-left point for parallel scattering
  const pCenterLeft = new THREE.Vector3(-26, pEnd.y * 0.45, pEnd.z * 0.45);
  
  // Mid point bottleneck spaced out to remain distinct
  const pMid = new THREE.Vector3(
    -4,
    pEnd.y * 0.30 + (clusterIdx - 2.5) * 1.1,
    pEnd.z * 0.30
  );

  // Bezier curve coordinates for scattered and central paths
  const oneMinusT = 1.0 - t;
  const posScatter = new THREE.Vector3()
    .addScaledVector(pStart, oneMinusT * oneMinusT)
    .addScaledVector(pMid, 2.0 * oneMinusT * t)
    .addScaledVector(pEnd, t * t);

  const posCentral = new THREE.Vector3()
    .addScaledVector(pCenterLeft, oneMinusT * oneMinusT)
    .addScaledVector(pMid, 2.0 * oneMinusT * t)
    .addScaledVector(pEnd, t * t);

  // Exponential decay: forces all lines to merge perfectly into one core by t = 0.35
  const decay = Math.pow(Math.max(0, 1.0 - t * 2.85), 3.5);
  
  // Blend between the scattered path and the central path
  const pos = new THREE.Vector3().lerpVectors(posCentral, posScatter, decay);

  // High-frequency waving plasma/electrical noise to make the core cable look bumpy, irregular, and alive
  const waveFreq = 24.0;
  const noiseSpeed = 14.0;
  const amplitude = 0.22 * (1.0 - decay); // Only waves when lines are merged in the core
  
  pos.y += Math.sin(t * waveFreq - time * noiseSpeed + curveIdx) * amplitude;
  pos.z += Math.cos(t * waveFreq * 0.8 - time * (noiseSpeed - 2.0) + curveIdx) * amplitude;

  return pos;
}

// Icon mapper for HTML badges
const getClusterIcon = (type: string, color: string) => {
  const iconClass = "w-3 h-3";
  switch (type) {
    case "CLASSES":
      return (
        <span className="p-1 bg-slate-950/80 rounded border border-white/5 flex items-center justify-center" style={{ color }}>
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
          </svg>
        </span>
      );
    case "FUNCTIONS":
      return (
        <span className="px-1.5 py-0.5 bg-slate-950/80 rounded border border-white/5 text-[9px] font-black italic tracking-tighter flex items-center justify-center leading-none" style={{ color }}>
          fx
        </span>
      );
    case "APIs":
      return (
        <span className="p-1 bg-slate-950/80 rounded border border-white/5 flex items-center justify-center" style={{ color }}>
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25z" />
          </svg>
        </span>
      );
    case "DATABASES":
      return (
        <span className="p-1 bg-slate-950/80 rounded border border-white/5 flex items-center justify-center" style={{ color }}>
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0v3.75m-16.5-3.75v3.75" />
          </svg>
        </span>
      );
    case "QUEUES":
      return (
        <span className="p-1 bg-slate-950/80 rounded border border-white/5 flex items-center justify-center" style={{ color }}>
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 0 1 0 3.75H5.625a1.875 1.875 0 0 1 0-3.75Z" />
          </svg>
        </span>
      );
    case "DEPENDENCIES":
      return (
        <span className="p-1 bg-slate-950/80 rounded border border-white/5 flex items-center justify-center" style={{ color }}>
          <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
          </svg>
        </span>
      );
    default:
      return null;
  }
};

export function StardustScene({ active, config: _config }: StardustSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const snippetGroupsRef = useRef<(THREE.Group | null)[]>([]);
  const spritesRef = useRef<(THREE.Sprite | null)[]>([]);
  const clusterGroupsRef = useRef<(THREE.Group | null)[]>([]);
  
  // References for structured nodes and dynamic lines
  const nodeMeshesRef = useRef<Record<string, THREE.InstancedMesh | null>>({});
  const latticeLinesRef = useRef<(THREE.LineSegments | null)[]>([]);
  const energyLinesGeomRef = useRef<THREE.BufferGeometry>(null);

  const shouldAnimate = useShouldAnimateCamera();
  const scrollProgress = useOnboardingStore((s) => s.scrollProgress);

  // Map Scene 2 scroll boundaries [0.17, 0.33] to local progress [0.0, 1.0]
  const localProgress = useMemo(() => {
    return Math.max(0, Math.min(1, (scrollProgress - 0.17) / 0.16));
  }, [scrollProgress]);

  // Interpolate timeline values
  const phase2Val = useMemo(() => Math.max(0, Math.min(1, (localProgress - 0.25) / 0.20)), [localProgress]);
  const phase4Val = useMemo(() => Math.max(0, Math.min(1, (localProgress - 0.65) / 0.20)), [localProgress]);
  const phase5Val = useMemo(() => Math.max(0, Math.min(1, (localProgress - 0.85) / 0.15)), [localProgress]);

  const glowTexture = useMemo(() => {
    if (typeof window === "undefined") return null;
    return createGlowingParticleTexture();
  }, []);

  useEffect(() => {
    return () => {
      glowTexture?.dispose();
    };
  }, [glowTexture]);

  // ── 20 Small Code Blocks (High Quantity, Small snippets, static position) ──
  const codeSnippets = useMemo(() => [
    { filename: "user.go", xStart: -28, yStart: 14, zStart: 1, lang: "go", code: ["type User struct {", "  ID   string", "  Name string", "}"] },
    { filename: "auth.ts", xStart: -23, yStart: 9, zStart: -4, lang: "typescript", code: ["export const verify = (tok) => {", "  return jwt.verify(tok, secret);", "}"] },
    { filename: "db.py", xStart: -30, yStart: 4, zStart: 3, lang: "python", code: ["def connect_db():", "  return psycopg2.connect(url)", ""] },
    { filename: "routes.rs", xStart: -22, yStart: -1, zStart: -2, lang: "rust", code: ["#[get(\"/health\")]", "pub fn health() -> impl Responder {", "  HttpResponse::Ok()", "}"] },
    { filename: "index.js", xStart: -29, yStart: -6, zStart: 2, lang: "javascript", code: ["const app = express();", "app.use(cors());", ""] },
    { filename: "cache.redis", xStart: -26, yStart: -11, zStart: -3, lang: "typescript", code: ["SET user:101 \"active\"", "EXPIRE user:101 3600", ""] },
    { filename: "config.yaml", xStart: -32, yStart: -15, zStart: 1, lang: "yml", code: ["server:", "  port: 8080", "  host: 0.0.0.0"] },
    { filename: "query.sql", xStart: -20, yStart: 15, zStart: -3, lang: "sql", code: ["SELECT * FROM users", "WHERE active = true;", ""] },
    { filename: "utils.ts", xStart: -27, yStart: 6, zStart: -5, lang: "typescript", code: ["export const delay = (ms) =>", "  new Promise(r => setTimeout(r, ms))"] },
    { filename: "main.cpp", xStart: -24, yStart: -4, zStart: 4, lang: "cpp", code: ["int main() {", "  std::cout << \"Starting...\";", "}"] },
    { filename: "styles.css", xStart: -28, yStart: -10, zStart: 4, lang: "css", code: [".container {", "  display: flex;", "}"] },
    { filename: "service.java", xStart: -25, yStart: 0, zStart: 5, lang: "java", code: ["@Service", "public class BillingService {", "}"] },
    { filename: "logger.go", xStart: -31, yStart: 11, zStart: -2, lang: "go", code: ["log.Printf(\"Starting session...\")", ""] },
    { filename: "helper.py", xStart: -26, yStart: 12, zStart: 3, lang: "python", code: ["def parse_json(payload):", "  return json.loads(payload)"] },
    { filename: "main.rs", xStart: -29, yStart: -13, zStart: -2, lang: "rust", code: ["fn main() {", "  println!(\"Thread active\");", "}"] },
    { filename: "schema.prisma", xStart: -22, yStart: -8, zStart: 5, lang: "typescript", code: ["model Account {", "  id        String   @id", "  createdAt DateTime @default(now)"] },
    { filename: "queue.go", xStart: -34, yStart: 7, zStart: 2, lang: "go", code: ["ch := make(chan Message, 100)", ""] },
    { filename: "worker.ts", xStart: -21, yStart: 4, zStart: 4, lang: "typescript", code: ["class WorkerPool {", "  async runTask(t) {", "    await t.execute();", "  }", "}"] },
    { filename: "test.js", xStart: -30, yStart: -2, zStart: -4, lang: "javascript", code: ["describe('auth', () => {", "  it('signs token', () => {})", "})"] },
    { filename: "api.go", xStart: -27, yStart: -7, zStart: -5, lang: "go", code: ["r.POST(\"/v1/api\", func(c *gin.Context) {", "  c.JSON(200, gin.H{\"id\": 1})", "})"] }
  ], []);

  // Pre-render code block editor textures
  const [snippetTextures, setSnippetTextures] = useState<THREE.CanvasTexture[]>([]);
  useEffect(() => {
    if (typeof window === "undefined") return;
    const renderer = new CodeSnippetRenderer();
    const textures = codeSnippets.map((snip) =>
      renderer.renderCodeSnippet(snip.filename, snip.code, snip.lang)
    );
    setSnippetTextures(textures);
    return () => {
      textures.forEach((t) => t.dispose());
    };
  }, [codeSnippets]);

  // ── Right-Side Structured Clusters (Spread further apart so they are clear) ──
  const clusters = useMemo(() => ({
    classes: { type: "CLASSES", position: new THREE.Vector3(2.5, 23, 2), color: "#3B82F6", count: 56782, nodesCount: 18, geomType: "octahedron" },
    functions: { type: "FUNCTIONS", position: new THREE.Vector3(8.0, 13, 4), color: "#A855F7", count: 128430, nodesCount: 24, geomType: "sphere" },
    apis: { type: "APIs", position: new THREE.Vector3(9.0, -13, -4), color: "#F97316", count: 3247, nodesCount: 20, geomType: "box" },
    databases: { type: "DATABASES", position: new THREE.Vector3(12.5, 3.5, 5), color: "#3B82F6", count: 1342, nodesCount: 20, geomType: "cylinder" },
    queues: { type: "QUEUES", position: new THREE.Vector3(4.0, -23, 2), color: "#EC4899", count: 764, nodesCount: 16, geomType: "torus" },
    dependencies: { type: "DEPENDENCIES", position: new THREE.Vector3(1.0, -3.5, -5), color: "#06B6D4", count: 342891, nodesCount: 16, geomType: "tetrahedron" }
  }), []);

  // Initialize Cluster Node structures with strict 3D Geometric lattices
  const clusterData = useMemo(() => {
    return Object.values(clusters).map((cluster) => {
      const nodes: THREE.Vector3[] = [];
      const linePoints: THREE.Vector3[] = [];

      if (cluster.geomType === "octahedron") {
        const size = 3.0;
        const vertices = [
          new THREE.Vector3(size, 0, 0), new THREE.Vector3(-size, 0, 0),
          new THREE.Vector3(0, size, 0), new THREE.Vector3(0, -size, 0),
          new THREE.Vector3(0, 0, size), new THREE.Vector3(0, 0, -size)
        ];
        nodes.push(...vertices);
        for (let i = 0; i < vertices.length; i++) {
          for (let j = i + 1; j < vertices.length; j++) {
            if (vertices[i].dot(vertices[j]) === 0) {
              const mid = new THREE.Vector3().addVectors(vertices[i], vertices[j]).multiplyScalar(0.5);
              if (nodes.length < cluster.nodesCount) nodes.push(mid);
            }
          }
        }
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            if (nodes[i].distanceTo(nodes[j]) < size * 1.5) {
              linePoints.push(nodes[i], nodes[j]);
            }
          }
        }
      } else if (cluster.geomType === "sphere") {
        const core = new THREE.Vector3(0, 0, 0);
        nodes.push(core);
        for (let i = 1; i < cluster.nodesCount; i++) {
          const u = Math.random();
          const v = Math.random();
          const theta = Math.acos(2.0 * u - 1.0);
          const phi = Math.PI * 2.0 * v;
          const r = 2.5 + Math.random() * 1.2;
          nodes.push(new THREE.Vector3(r * Math.sin(theta) * Math.cos(phi), r * Math.sin(theta) * Math.sin(phi), r * Math.cos(theta)));
        }
        for (let i = 1; i < nodes.length; i++) {
          linePoints.push(core, nodes[i]);
          for (let j = i + 1; j < nodes.length; j++) {
            if (nodes[i].distanceTo(nodes[j]) < 2.2) linePoints.push(nodes[i], nodes[j]);
          }
        }
      } else if (cluster.geomType === "box") {
        const radius = 3.2;
        for (let i = 0; i < cluster.nodesCount; i++) {
          const offset = i + 0.5;
          const phi = Math.acos(-1 + (2 * offset) / cluster.nodesCount);
          const theta = Math.sqrt(cluster.nodesCount * Math.PI) * phi;
          nodes.push(new THREE.Vector3(radius * Math.sin(phi) * Math.cos(theta), radius * Math.sin(phi) * Math.sin(theta), radius * Math.cos(phi)));
        }
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            if (nodes[i].distanceTo(nodes[j]) < 3.5) linePoints.push(nodes[i], nodes[j]);
          }
        }
      } else if (cluster.geomType === "cylinder") {
        const radius = 2.5;
        const height = 3.2;
        const halfCount = Math.floor(cluster.nodesCount / 2);
        for (let i = 0; i < halfCount; i++) {
          const angle = (i / halfCount) * Math.PI * 2;
          nodes.push(new THREE.Vector3(radius * Math.cos(angle), height / 2, radius * Math.sin(angle)));
          nodes.push(new THREE.Vector3(radius * Math.cos(angle), -height / 2, radius * Math.sin(angle)));
        }
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const dist = nodes[i].distanceTo(nodes[j]);
            if (dist < radius * 1.3 || (Math.abs(nodes[i].y - nodes[j].y) === height && dist < height * 1.1)) {
              linePoints.push(nodes[i], nodes[j]);
            }
          }
        }
      } else if (cluster.geomType === "torus") {
        const length = 6.5;
        for (let i = 0; i < cluster.nodesCount; i++) {
          const t = i / (cluster.nodesCount - 1);
          const px = -length / 2 + t * length;
          const py = Math.sin(t * Math.PI * 2.0) * 1.2;
          const pz = Math.cos(t * Math.PI * 1.5) * 0.8;
          nodes.push(new THREE.Vector3(px, py, pz));
        }
        for (let i = 0; i < nodes.length - 1; i++) {
          linePoints.push(nodes[i], nodes[i + 1]);
        }
      } else {
        const size = 3.0;
        const v0 = new THREE.Vector3(0, size, 0);
        const v1 = new THREE.Vector3(-size, -size / 2, size);
        const v2 = new THREE.Vector3(size, -size / 2, size);
        const v3 = new THREE.Vector3(0, -size / 2, -size);
        nodes.push(v0, v1, v2, v3);
        const edges = [[v0, v1], [v0, v2], [v0, v3], [v1, v2], [v2, v3], [v3, v1]];
        edges.forEach(([pA, pB]) => {
          if (nodes.length < cluster.nodesCount) nodes.push(new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5));
        });
        while (nodes.length < cluster.nodesCount) {
          const r1 = Math.random();
          const r2 = Math.random();
          if (r1 + r2 <= 1.0) {
            nodes.push(new THREE.Vector3().addScaledVector(v1, r1).addScaledVector(v2, r2).addScaledVector(v3, 1 - r1 - r2));
          }
        }
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            if (nodes[i].distanceTo(nodes[j]) < size * 1.6) linePoints.push(nodes[i], nodes[j]);
          }
        }
      }

      return { ...cluster, nodes, linePoints };
    });
  }, [clusters]);

  // ── Allocate Vertex Colors for the LineSegments ──
  const lineColorsAttribute = useMemo(() => {
    // 6 clusters, 12 curves per cluster, 24 segments per curve, 2 points per segment, 3 floats (r, g, b)
    const arr = new Float32Array(6 * 12 * 24 * 2 * 3);
    let ptr = 0;
    Object.values(clusters).forEach((cluster) => {
      const col = new THREE.Color(cluster.color);
      for (let k = 0; k < 12; k++) {
        for (let s = 0; s < 24; s++) {
          // Point 1
          arr[ptr++] = col.r;
          arr[ptr++] = col.g;
          arr[ptr++] = col.b;
          // Point 2
          arr[ptr++] = col.r;
          arr[ptr++] = col.g;
          arr[ptr++] = col.b;
        }
      }
    });
    return arr;
  }, [clusters]);

  // Frame Loop
  useFrame((state) => {
    if (!active || !shouldAnimate) return;
    const time = state.clock.getElapsedTime();

    // ── 1. Animate Code Blocks (Minimize to 30% scale and retain that state) ──
    const animatedSnippetPositions = codeSnippets.map((snip, idx) => {
      const p = new THREE.Vector3(snip.xStart, snip.yStart, snip.zStart);

      // Continuous float and rotation on the left
      const floatY = Math.sin(time * 0.8 + idx) * 0.6;
      const floatX = Math.cos(time * 0.6 + idx) * 0.4;
      p.x += floatX;
      p.y += floatY;

      const group = snippetGroupsRef.current[idx];
      const sprite = spritesRef.current[idx];
      if (group && sprite) {
        const scaleMult = 1.0 - 0.7 * phase2Val; // Shrinks to 30% scale and retains it
        let opacity = 0.85 - 0.3 * phase2Val;   // Dims to 55% opacity and retains it

        // Glitchy opacity flicker in Phase 1
        if (localProgress <= 0.25) {
          const glitch = Math.sin(time * 30 + idx) > 0.82 ? 0.35 : 1.0;
          opacity *= glitch;
        }

        group.position.copy(p);
        group.scale.set(scaleMult, scaleMult, scaleMult);
        sprite.material.opacity = opacity;
      }
      return p;
    });

    // ── 2. Re-compute scattered-to-merged Bezier lines dynamically ──
    const geom = energyLinesGeomRef.current;
    if (geom) {
      const posAttr = geom.getAttribute("position") as THREE.BufferAttribute;
      const array = posAttr.array as Float32Array;
      let ptr = 0;

      // Tube progress timeline spans localProgress [0.20, 0.70]
      const lineProgress = Math.max(0, Math.min(1, (localProgress - 0.20) / 0.50));

      Object.values(clusters).forEach((cluster, clusterIdx) => {
        const pEnd = cluster.position;

        for (let k = 0; k < 12; k++) {
          // Select a start snippet card center dynamically
          const snippetIdx = (k + clusterIdx * 2) % codeSnippets.length;
          const pStart = animatedSnippetPositions[snippetIdx];

          for (let s = 0; s < 24; s++) {
            const t0 = (s / 24) * lineProgress;
            const t1 = ((s + 1) / 24) * lineProgress;

            const pos0 = getPointOnCurve(pStart, pEnd, clusterIdx, t0, time, k);
            const pos1 = getPointOnCurve(pStart, pEnd, clusterIdx, t1, time, k);

            array[ptr++] = pos0.x;
            array[ptr++] = pos0.y;
            array[ptr++] = pos0.z;

            array[ptr++] = pos1.x;
            array[ptr++] = pos1.y;
            array[ptr++] = pos1.z;
          }
        }
      });
      posAttr.needsUpdate = true;
    }

    // ── 3. Animate Right-Side Structured Lattices (Enlarged to 2.6 scale) ──
    clusterData.forEach((cluster, clusterIdx) => {
      const group = clusterGroupsRef.current[clusterIdx];
      if (!group) return;

      // Slow self-spin
      group.rotation.y = time * 0.06 + clusterIdx;
      group.rotation.z = Math.sin(time * 0.2 + clusterIdx) * 0.03;

      // Enlarge final scale to 2
      let baseScale = 0.0;
      if (phase4Val > 0.0) {
        const ease = 1.0 - Math.pow(1.0 - phase4Val, 3.5);
        baseScale = ease * 2;
      }
      if (phase5Val > 0.0) {
        const pulse = 1.9 + 0.04 * Math.sin(time * 1.5 + clusterIdx);
        baseScale = pulse;
      }
      group.scale.set(baseScale, baseScale, baseScale);

      // Animate lattice connection lines segment draw-in
      const lineMesh = latticeLinesRef.current[clusterIdx];
      if (lineMesh && lineMesh.geometry) {
        const totalPoints = cluster.linePoints.length;
        const drawLimit = phase4Val > 0.0 ? Math.floor(totalPoints * phase4Val) : 0;
        lineMesh.geometry.setDrawRange(0, phase5Val > 0.0 ? totalPoints : drawLimit);
      }

      // Update 3D Nodes scaling in InstancedMesh
      const nodeMesh = nodeMeshesRef.current[cluster.type];
      if (nodeMesh) {
        const tempMat = new THREE.Matrix4();
        const nodeQ = new THREE.Quaternion();
        const nodeS = new THREE.Vector3(1, 1, 1);

        cluster.nodes.forEach((pos, idx) => {
          const stagger = (idx / cluster.nodesCount) * 0.3;
          const nodeT = Math.max(0, Math.min(1, (phase4Val - stagger) / 0.4));
          const easeNodeT = 1.0 - Math.pow(1.0 - nodeT, 4.0);
          
          nodeS.setScalar(easeNodeT);
          tempMat.compose(pos, nodeQ, nodeS);
          nodeMesh.setMatrixAt(idx, tempMat);
        });
        nodeMesh.instanceMatrix.needsUpdate = true;
      }
    });
  });

  return (
    <group ref={groupRef} visible={active}>
      {/* ── Lighting ── */}
      <ambientLight color="#0c0724" intensity={0.5} />
      <directionalLight color="#b96bf6" intensity={1.4} position={[15, 25, 15]} />
      <pointLight color="#0284c7" intensity={2.0} position={[-25, 5, -20]} distance={90} />
      <pointLight color="#c084fc" intensity={1.8} position={[25, -5, 20]} distance={90} />

      {/* ── Floor Portal Glow ── */}
      {glowTexture && (
        <mesh position={[4, -18, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[75, 75]} />
          <meshBasicMaterial
            map={glowTexture}
            color="#a78bfa"
            transparent
            opacity={0.12}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
          />
        </mesh>
      )}

      {/* ── Floating Small VSCode Code Blocks (Do NOT disappear - scale down & retain) ── */}
      {snippetTextures.map((tex, idx) => {
        const snip = codeSnippets[idx];

        return (
          <group
            key={snip.filename}
            ref={(el) => { snippetGroupsRef.current[idx] = el; }}
            position={[snip.xStart, snip.yStart, snip.zStart]}
          >
            <sprite
              ref={(el) => { spritesRef.current[idx] = el; }}
              scale={[11, 8.25, 1]}
            >
              <spriteMaterial attach="material" map={tex} transparent opacity={0.85} />
            </sprite>

            {/* Floating Filename Badges (Follows scaled group position) */}
            <Html
              position={[0, 4.8, 0]}
              center
              distanceFactor={45}
              style={{
                pointerEvents: "none",
                transition: "opacity 0.2s ease-out"
              }}
            >
              <div className="bg-[#05040a]/95 border border-white/10 px-2 py-0.5 rounded text-[8px] font-bold text-slate-300 tracking-wider font-mono shadow-xl backdrop-blur select-none whitespace-nowrap">
                {snip.filename}
              </div>
            </Html>
          </group>
        );
      })}

      {/* ── 6 Scattered-to-Merged Line Bundles (Do NOT disappear) ── */}
      <lineSegments>
        <bufferGeometry ref={energyLinesGeomRef}>
          <bufferAttribute
            attach="attributes-position"
            args={[new Float32Array(6 * 12 * 24 * 2 * 3), 3]}
          />
          <bufferAttribute
            attach="attributes-color"
            args={[lineColorsAttribute, 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial
          vertexColors
          transparent
          opacity={0.94}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>

      {/* ── Right-side Structured Clusters ── */}
      {clusterData.map((cluster, clusterIdx) => {
        let geom: THREE.BufferGeometry;
        switch (cluster.geomType) {
          case "octahedron":
            geom = new THREE.OctahedronGeometry(0.48, 0);
            break;
          case "sphere":
            geom = new THREE.IcosahedronGeometry(0.38, 1);
            break;
          case "box":
            geom = new THREE.BoxGeometry(0.55, 0.55, 0.55);
            break;
          case "cylinder":
            geom = new THREE.CylinderGeometry(0.3, 0.3, 0.7, 6);
            break;
          case "torus":
            geom = new THREE.TorusGeometry(0.32, 0.1, 6, 12);
            break;
          default:
            geom = new THREE.TetrahedronGeometry(0.5, 0);
        }

        return (
          <group
            key={cluster.type}
            position={cluster.position.toArray() as [number, number, number]}
            ref={(el) => { clusterGroupsRef.current[clusterIdx] = el; }}
          >
            {/* Volumetric Localized Nebula Glow (Halos centered at each cluster) */}
            {glowTexture && (
              <sprite scale={[18, 18, 1]}>
                <spriteMaterial
                  attach="material"
                  map={glowTexture}
                  color={cluster.color}
                  transparent
                  opacity={0.36 * Math.min(1.0, phase4Val)} // Fades in with final structure
                  blending={THREE.AdditiveBlending}
                  depthWrite={false}
                />
              </sprite>
            )}

            {/* 3D Node Mesh Instances */}
            <instancedMesh
              ref={(el) => { nodeMeshesRef.current[cluster.type] = el; }}
              args={[geom, null as any, cluster.nodesCount]}
            >
              <meshStandardMaterial
                color={cluster.color}
                emissive={cluster.color}
                emissiveIntensity={0.88}
                roughness={0.2}
                metalness={0.1}
              />
            </instancedMesh>

            {/* Lattice Connections */}
            <lineSegments ref={(el) => { latticeLinesRef.current[clusterIdx] = el; }}>
              <bufferGeometry attach="geometry">
                <bufferAttribute
                  attach="attributes-position"
                  args={[new Float32Array(cluster.linePoints.flatMap(p => [p.x, p.y, p.z])), 3]}
                />
              </bufferGeometry>
              <lineBasicMaterial
                color={cluster.color}
                transparent
                opacity={0.35}
                blending={THREE.AdditiveBlending}
              />
            </lineSegments>

            {/* Custom Interactive HUD badges overlay */}
            <Html center distanceFactor={45} style={{ pointerEvents: "none" }}>
              <div 
                className="flex items-center gap-2 bg-[#05040a]/95 backdrop-blur px-3 py-1.5 rounded-lg border shadow-xl shadow-black/60 whitespace-nowrap select-none"
                style={{ borderColor: `${cluster.color}35` }}
              >
                {getClusterIcon(cluster.type, cluster.color)}
                <div>
                  <div className="text-[9px] font-black uppercase tracking-wider text-white font-sans leading-none">
                    {cluster.type}
                  </div>
                  <div className="text-[8px] font-bold text-slate-400 font-mono mt-0.5 leading-none">
                    {cluster.count.toLocaleString()}
                  </div>
                </div>
              </div>
            </Html>
          </group>
        );
      })}
    </group>
  );
}
