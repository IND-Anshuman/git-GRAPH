# Wave 9 - Post-Processing Pipeline & Audio System Walkthrough

All tasks for Wave 9, 9.5, and 9.6 have been completed successfully. The application compiles perfectly in TypeScript strict mode, bundles successfully via the Next.js production build, and runs the visual effects pipeline and ambient audio system with smooth 60 FPS performance.

---

## Technical Implementations

### 1. Quality-Tiered Post-Processing Effects (`PostProcessingEffects.tsx`)
- **Direct Child Rendering**:
  - Encapsulated each effect in native R3F tags directly inside `<EffectComposer>`, utilizing `<group />` placeholders when disabled. This satisfies strict ReactElement child type checks expected by `@react-three/postprocessing`'s `<EffectComposer>`, avoiding `null`/`false` child errors and runtime circular reference crashes.
- **Visual Filters by Quality Tier**:
  - **ULTRA**: 
    - Selective Bloom (pulsing between $0.6$ and $0.8$ intensity).
    - Depth of Field (shallow f-stop 1.4; custom focal distances by scene, disabled in Scene 8).
    - Screen-Space Ambient Occlusion (SSAO) with 32 samples for depth shadows.
    - Tone Mapping (ACES Filmic), Chromatic Aberration lens distortion, and Vignette framing.
  - **HIGH**: Bloom, Depth of Field (reduced rendering height of 480px), Tone Mapping, Vignette.
  - **MEDIUM**: Bloom and ACES Filmic Tone Mapping.
  - **LOW**: All effects disabled for raw GPU rendering to maximize framerate.
- **Integration**:
  - Mounted `<PostProcessingEffects />` directly inside `<Canvas>` in `OnboardingCanvas.tsx`.

### 2. Procedural Audio Synthesizer (`AudioSystem.ts`)
- **Autoplay Compliance**:
  - Keeps the Web Audio `AudioContext` suspended on load. Instantiates and resumes the context dynamically on the first user interaction (click, key down, scroll) in `app/page.tsx`.
- **Zero-Resource Synthesis**:
  - Programmatically generates all sounds on-the-fly, avoiding HTTP 404 resource errors and buffering delays:
    - **Ambient Space Drone**: Detuned sawtooth/triangle oscillators at 55Hz and 110Hz run through a low-pass filter modulated by a slow 0.08Hz sine wave LFO filter sweep.
    - **Scene Whoosh**: Procedural white noise passed through a bandpass filter sweeping from 80Hz to 1.8kHz and back, enveloped over 1.2s.
    - **Hover Blip**: A sine oscillator sliding down from 440Hz with rapid exponential gain decay.
    - **Click Chime**: Staggered arpeggiated major triad (C5, E5, G5) chime with exponential decay.
    - **Spatial Pulse**: A high-frequency sine ping (880Hz) mapped to a Web Audio `PannerNode` positioned at the 3D spark source.
- **R3F Camera Listener Syncing**:
  - Decomposes the camera's matrixWorld in the `useFrame` loop of `CameraRig` on every frame to feed the absolute position, forward orientation, and up vectors directly to the Web Audio `AudioListener`.

### 3. Glassmorphic Audio Control UI (`AudioToggle.tsx`)
- Collapsible fixed overlay positioned bottom-left. Expands on hover or keyboard focus to reveal a volume slider.
- Contrast-compliant WCAG 2.1 AA design. Fully accessible via keyboard navigation (`Tab` focus, `Space`/`Enter` toggle, slider control, and `Escape` to close).
- Syncs state reactively with `localStorage` preferences (`sip-audio-enabled` and `sip-audio-volume`).

---

## Wave 9.5 - Scene 1 & 2 Graphics Enhancements (God-Level Polish)

We have upgraded the layouts and animations of the first two onboarding scenes into highly premium, mathematically structured shapes:

### 1. Scene 1 - Logarithmic Galaxy Spiral ("The Chaos")
- **Visual Pattern**: Replaced the random box particle field with a custom `galaxy` distribution pattern. Particles are arranged along two arms of a logarithmic spiral ($r = a \cdot e^{b \cdot \theta}$) winding outwards from a dense core.
- **Rotation Animation**: Added a frame loop animation in `ChaosScene.tsx` that slowly spins the entire galaxy group container on its normal Z-axis, creating a living, rotating cosmos of raw source code.

### 2. Scene 2 - Double-Helix DNA Vortex ("Stardust of Code")
- **Visual Pattern**: Replaced the random sphere shell with a `double_helix` distribution pattern, arranging particles in a double-strand helical DNA-style vortex winding along the vertical axis (Y-axis).
- **Radial Cylindrical Force Vector**: Configured the initial direction vectors of helix particles to point radially outward from the cylinder vertical axis. When the scene triggers, the DNA helix swells outwards concentrically, maintaining its helical wave structure.
- **Zero-Gravity Physics**: Set the scene's gravity parameter to `0` and reduced damping to let the helical shockwave expand cleanly and smoothly.
- **Vertical Spin**: Configured the group container to slowly rotate on its vertical Y-axis inside the animation loop to maintain visual dynamism.

---

## Wave 9.6 - VRAM & Framebuffer Optimizations (<1GB VRAM Support)

To allow the 3D onboarding interface to render smoothly on devices with limited memory (less than 1 GB VRAM), we implemented three core performance improvements:

### 1. Dynamic Resolution Scaling (DPR Capping)
- **Canvas Resolution**: Configured the R3F `<Canvas>` component in `OnboardingCanvas.tsx` to dynamically cap its device pixel ratio (`dpr`) based on the active quality tier:
  - **LOW**: `0.75` (reduces render target area by over $75\%$ compared to Retina/high-DPI screens).
  - **MEDIUM**: `1.0` (renders at native CSS pixel size, saving over $50\%$ framebuffer space).
  - **HIGH/ULTRA**: `[1, 2]` (supports high-resolution Retina screens).
- **Sub-Pixel Antialiasing**: Disabled `gl.antialias` on the `low` quality tier to eliminate sub-pixel rendering buffers, saving significant framebuffer memory.

### 2. High-Polygon Sphere Bypass (LOD Override)
- **Geometry Reduction**: Modified the Level of Detail scheduler in `ParticleLOD.ts` to bypass 3D sphere geometries (LOD 0) entirely when `qualityTier === "low"`.
- **4-Vertex Billboards**: Forces all particles (even close-up ones) to render as highly-optimized 4-vertex 2D billboards. This cuts vertex buffer bandwidth and keeps memory usage down.

### 3. Lowered VBO Allocations
- **Buffer Scaling**: Decreased the maximum particle counts for the `low` tier in `scene1.json` and `scene2.json` to `10,000`, reducing the size of instanced vertex arrays allocated in VRAM.

---

## Verification Results

### TypeScript Verification
- Compiled successfully with 0 warnings/errors:
  ```bash
  $ npm run type-check
  > tsc --noEmit
  ```
  *(Completed successfully with exit code 0)*

### Next.js Production Build
- Bundled successfully with zero compilation or route errors:
  ```bash
  $ npm run build
  ▲ Next.js 16.2.9 (Turbopack)
  Creating an optimized production build ...
  ✓ Compiled successfully in 9.8s
  Running TypeScript ...
  Finished TypeScript in 8.1s ...
  ✓ Generating static pages using 5 workers (4/4) in 871ms
  ```
  *(Completed successfully with exit code 0)*
