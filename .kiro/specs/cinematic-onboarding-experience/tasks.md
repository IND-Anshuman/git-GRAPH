# Implementation Plan: Cinematic Onboarding Experience

## Overview

This implementation plan breaks down the Cinematic Onboarding Experience into discrete, executable coding tasks. The experience is a GPU-accelerated, scroll-driven 3D journey built with React Three Fiber, Three.js, and GSAP that visualizes the transformation of source code into software intelligence through eight interconnected scenes.

**Tech Stack:**
- Next.js 15, React 19, TypeScript
- React Three Fiber, Three.js, Drei
- GSAP ScrollTrigger, Framer Motion
- Zustand for state management
- fast-check for property-based testing
- Vitest for unit testing
- Playwright for integration testing

**Implementation Approach:**
The tasks follow a bottom-up approach: core infrastructure → particle systems → individual scenes → interactions → accessibility → integration → testing. Each task builds incrementally, with checkpoints to validate functionality before proceeding.

## Tasks

### 1. Project Setup and Core Infrastructure

- [x] 1.1 Initialize project structure and dependencies
  - Create Next.js 15 project with TypeScript configuration
  - Install dependencies: react-three-fiber, three, @react-three/drei, gsap, zustand, framer-motion
  - Install dev dependencies: vitest, @testing-library/react, fast-check, playwright
  - Configure TypeScript with strict mode and path aliases
  - Set up ESLint and Prettier for code quality
  - Create directory structure: `/components`, `/lib`, `/hooks`, `/stores`, `/config`, `/shaders`, `/public/assets`
  - _Requirements: 1.1, 1.2_

- [x] 1.2 Create Zustand store for application state
  - Define `OnboardingState` interface with scroll progress, current scene, quality tier, interaction state
  - Implement store actions: `setScrollProgress`, `setCurrentScene`, `setQualityTier`, `setHoveredObject`, `expandCard`, `closeCard`
  - Add derived selectors for scene boundaries and loading status
  - Implement state persistence for progress tracking
  - _Requirements: 1.1, 19.3_

- [-] 1.3 Implement Scroll Controller with GSAP ScrollTrigger
  - Create `ScrollController` class managing scroll-to-progress mapping [0, 1]
  - Integrate GSAP ScrollTrigger with scrub enabled for 1:1 scroll mapping
  - Implement smooth interpolation with 200ms settling time on scroll stop
  - Add scroll position clamping to prevent over-scroll
  - Define scene boundaries at [0, 0.17, 0.33, 0.50, 0.67, 0.83, 1.0]
  - Implement `getCurrentScene()` method mapping progress to scene number
  - Add event subscription pattern for progress changes
  - _Requirements: 2.1, 2.2, 2.4, 2.6_

- [ ]* 1.4 Write property test for scroll position clamping
  - **Property 3: Scroll Position Clamping**
  - **Validates: Requirements 2.6**
  - Generate random scroll inputs including negative and >1 values
  - Verify normalized output is always in [0, 1]
  - Test with extreme values (-1000, 1000, NaN, Infinity)
  - _Requirements: 2.6_

- [x] 1.5 Implement Camera Controller with spline interpolation
  - Create `CameraController` class managing camera position and rotation
  - Implement Catmull-Rom spline interpolation for smooth camera paths
  - Parse camera rail definitions from JSON configuration files
  - Implement keyframe surrounding lookup and interpolation factor calculation
  - Add easing function support (linear, easeInOut, easeIn, easeOut)
  - Implement look-at target calculation for automatic rotation
  - Support additive offsets for mouse parallax effects
  - _Requirements: 2.3, 2.7_

- [ ]* 1.6 Write property test for camera interpolation correctness
  - **Property 2: Camera Interpolation Correctness**
  - **Validates: Requirements 2.3, 2.4**
  - Generate random scene configurations with varying keyframe counts
  - Verify interpolated positions lie within keyframe bounding volumes
  - Verify rotation values are within surrounding keyframe ranges
  - Test edge cases: single keyframe, identical keyframes, extreme positions
  - _Requirements: 2.3, 2.4_

- [-] 1.7 Create Scene Manager for lifecycle orchestration
  - Implement `SceneManager` class with scene loading, activation, and unloading
  - Define `SceneStatus` enum (UNLOADED, LOADING, READY, ACTIVE)
  - Implement lazy loading: current scene + next scene loaded, scenes >2 away unloaded
  - Add 500ms crossfade transitions between scenes
  - Implement scene configuration parser reading JSON files
  - Add schema validation for scene configurations
  - _Requirements: 2.5, 16.2, 16.3, 17.1, 17.2_

- [ ]* 1.8 Write property test for configuration schema validation
  - **Property 8: Configuration Schema Validation**
  - **Validates: Requirements 17.2**
  - Generate valid configurations conforming to schema
  - Generate invalid configurations with specific constraint violations
  - Verify validation returns success for valid configs
  - Verify validation returns failure with specific errors for invalid configs
  - _Requirements: 17.2_

- [-] 1.9 Implement configuration parsing with round-trip preservation
  - Create JSON parser for scene configuration files
  - Create pretty printer formatting configuration objects to JSON
  - Ensure round-trip preservation: parse → pretty print → parse produces equivalent object
  - Preserve numeric precision, array ordering, nested structures
  - Generate descriptive error messages with property paths for invalid configs
  - _Requirements: 17.1, 18.3, 18.4, 18.5, 18.6, 18.7_

- [ ]* 1.10 Write property test for configuration round-trip identity
  - **Property 7: Configuration Round-Trip Identity**
  - **Validates: Requirements 18.3, 18.4, 18.5, 18.6**
  - Generate valid scene configurations with random schema-conforming values
  - Perform round-trip: serialize → parse → serialize
  - Verify all properties preserved (deep equality check)
  - Verify numeric precision preserved (test with floats having many decimal places)
  - Verify array ordering preserved
  - Verify nested structure preservation
  - _Requirements: 18.3, 18.4, 18.5, 18.6_

- [ ]* 1.11 Write property test for configuration error messages
  - **Property 9: Configuration Parse Error Messages**
  - **Validates: Requirements 18.7**
  - Generate invalid JSON configurations with various error types
  - Verify error messages contain property paths identifying invalid locations
  - Test with: missing required fields, type mismatches, constraint violations
  - _Requirements: 18.7_

- [-] 1.12 Implement Performance Monitor with adaptive quality
  - Create `PerformanceMonitor` class tracking FPS and triggering quality adjustments
  - Measure frame rate every 1000ms, average over 3 samples
  - Define quality tiers: ULTRA (>60 FPS), HIGH (50-60), MEDIUM (30-50), LOW (<30)
  - Implement automatic downgrade when FPS drops below threshold for 3 consecutive measurements
  - Implement gradual upgrade when FPS stabilizes above 60 for 10 seconds
  - Emit quality change events for particle system and post-processing adjustments
  - Provide manual quality override
  - _Requirements: 12.1, 12.2, 12.3_

- [ ]* 1.13 Write property test for adaptive quality adjustment
  - **Property 6: Adaptive Quality Adjustment**
  - **Validates: Requirements 12.2**
  - Generate FPS sequences with patterns: gradual decline, sudden drops, oscillations
  - Verify particle count reduced by 20% after 3 consecutive low FPS measurements
  - Verify quality tier downgrades at correct thresholds
  - Test edge cases: exactly 50 FPS, oscillating around threshold
  - _Requirements: 12.2_

- [-] 1.14 Create Asset Loader with caching and retry logic
  - Implement `AssetLoader` class for loading 3D models, textures, and audio
  - Support GLTF/GLB models with Draco compression
  - Support WebP textures with basis universal fallback
  - Implement IndexedDB caching with version-based invalidation
  - Add priority queue: critical assets load first, decorative assets last
  - Implement retry logic with exponential backoff (3 attempts, 2s → 4s → 8s delays)
  - Display granular loading progress updates
  - _Requirements: 1.2, 16.1, 16.6, 16.7, 16.8_

- [ ]* 1.15 Write unit tests for Asset Loader
  - Test retry logic with simulated network failures
  - Test exponential backoff timing
  - Test cache retrieval and invalidation based on version
  - Test loading priority queue ordering
  - _Requirements: 16.6_

- [ ] 1.16 Set up main Canvas and R3F context
  - Create `OnboardingApp` root component
  - Set up R3F Canvas with WebGL2 context, fallback to WebGL1
  - Configure camera with initial position [0, 0, -50], FOV 75
  - Add ambient lighting and scene background color
  - Handle WebGL initialization failures with fallback message
  - Display loading progress indicator during initial asset load
  - _Requirements: 1.1, 1.3, 1.4_

### 2. Checkpoint - Core Infrastructure Complete

- [~] 2. Verify core infrastructure
  - Ensure scroll controller maps scroll to progress correctly
  - Ensure camera controller interpolates positions smoothly
  - Ensure scene manager loads and transitions between scenes
  - Ensure performance monitor adjusts quality based on FPS
  - Ensure asset loader caches and retrieves assets
  - Run all property tests and unit tests - verify they pass
  - Ask the user if questions arise.

### 3. Particle System Engine

- [~] 3.1 Implement base Particle System Engine with instanced meshes
  - Create `ParticleSystemEngine` class managing multiple particle groups
  - Implement `createParticles()` method creating `THREE.InstancedMesh` with configurable count
  - Support quality-based particle counts (ultra, high, medium, low)
  - Initialize instance matrices with position, rotation, scale for each particle
  - Support instance colors via `instanceColor` attribute
  - Implement `updateParticles()` method with per-particle update function
  - Implement `destroyParticles()` method with proper disposal
  - _Requirements: 3.2, 4.2, 4.7_

- [~] 3.2 Create GPU shaders for particle animations
  - Write vertex shader for drift animation using Simplex noise for turbulence
  - Write vertex shader for orbit animation with circular paths around centers
  - Write vertex shader for explosion animation with velocity and gravity physics
  - Write vertex shader for cluster animation with attraction forces to centers
  - Write vertex shader for network animation with connection flow effects
  - Implement shader uniform updates for time, parameters, and animation control
  - _Requirements: 3.4, 4.3, 4.4, 5.2, 5.3_

- [~] 3.3 Implement LOD system for particle rendering
  - Define three LOD levels: high-poly sphere (close), billboard quad (medium), single point (far)
  - Implement distance-based LOD selection at thresholds 20m and 50m
  - Create `updateParticleLOD()` method adjusting scale based on camera distance
  - Apply LOD updates during render loop without triggering layout thrashing
  - _Requirements: 12.4_

- [~] 3.4 Implement frustum culling for particles
  - Create `FrustumCuller` class using `THREE.Frustum` for visibility tests
  - Implement per-instance culling with bounding sphere tests
  - Move off-screen instances to far position (9999, 9999, 9999) to skip rendering
  - Apply culling in render loop before particle updates
  - Track and log visible/culled instance counts for debugging
  - _Requirements: 12.5, 3.7_

- [ ]* 3.5 Write unit tests for Particle System Engine
  - Test instanced mesh creation with correct particle counts per quality tier
  - Test particle update functions modify positions, colors, scales correctly
  - Test LOD selection returns correct geometry for given distances
  - Test frustum culling marks correct instances as visible/hidden
  - _Requirements: 3.2, 12.4, 12.5_

- [~] 3.6 Implement texture atlasing for particle materials
  - Create 2048x2048 texture atlas packing all particle textures
  - Generate UV coordinates for each particle type
  - Assign UV coordinates via instanced attributes
  - Build texture atlas generation script for asset pipeline
  - _Requirements: 12.8_

- [~] 3.7 Implement particle animation system
  - Create `animateParticles()` method with animation type and parameters
  - Support animation types: drift, orbit, explosion, cluster, network
  - Implement animation state management (playing, paused, completed)
  - Add animation blending between types for smooth transitions
  - Integrate with GPU shaders for physics calculations
  - _Requirements: 3.4, 4.3, 5.3_

### 4. Checkpoint - Particle System Complete

- [~] 4. Verify particle system functionality
  - Create test scene with 50,000 particles rendering at 60 FPS
  - Verify LOD system switches geometries at correct distances
  - Verify frustum culling improves performance (check culled count)
  - Verify GPU shaders animate particles correctly
  - Run all unit tests - verify they pass
  - Ask the user if questions arise.

### 5. Scene Implementations - Scenes 1-2

- [~] 5.1 Create scene configuration JSON files
  - Define JSON schemas for camera keyframes, particle configs, lighting, interactions
  - Create `scene1-config.json` for Chaos scene with 50k-100k particles
  - Create `scene2-config.json` for Stardust scene with 10k-50k particles
  - Define camera rail keyframes for each scene with positions, rotations, easing
  - Define particle behavior parameters (drift velocity, turbulence, colors)
  - Define interaction hotspot metadata
  - _Requirements: 17.1_

- [~] 5.2 Implement Scene 1: The Chaos
  - Create `ChaosScene` component loading scene1-config.json
  - Initialize particle system with 50k-100k code fragment particles using instanced meshes
  - Apply drift animation shader with random velocity and turbulence
  - Position camera inside particle cloud as defined in camera rail
  - Add subtle bloom post-processing effect to code fragments
  - Implement frustum culling to render only visible particles
  - Register interaction hotspots for code fragment hover
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [~] 5.3 Implement Scene 2: Stardust of Code
  - Create `StardustScene` component loading scene2-config.json
  - Animate file structure explosion using explosion shader with physics-based velocity and gravity
  - Render 10k-50k semantic entity particles with size/color variations (functions=blue, classes=purple, methods=green)
  - Stabilize particles in distributed cloud after explosion completes
  - Implement 1000ms smooth transition from Scene 1 chaos to Scene 2 explosion
  - Register interaction hotspots for semantic entity particles
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ]* 5.4 Write unit tests for Scene 1 and 2
  - Test scene configuration parsing from JSON
  - Test particle counts match quality tier settings
  - Test animation state transitions
  - Test interaction hotspot registration
  - _Requirements: 3.1, 4.1_

### 6. Scene Implementations - Scenes 3-4

- [~] 6.1 Create scene configuration JSON files for Scenes 3-4
  - Create `scene3-config.json` for Knowledge Constellations with cluster positions
  - Create `scene4-config.json` for Planets with size/health metrics
  - Define constellation clustering parameters and connection line rules
  - Define planet mesh configurations with size scaling and color gradients
  - Define camera rails with orbital movement
  - _Requirements: 17.1_

- [~] 6.2 Implement Scene 3: Knowledge Constellations
  - Create `ConstellationScene` component with cluster animation shader
  - Animate semantic particles clustering into constellation groups using attraction forces
  - Render connecting lines between related particles using `THREE.LineSegments`
  - Position constellation clusters in 3D space with separation
  - Animate constellation rotation and pulsing glow effect (0.5Hz frequency)
  - Render constellation labels floating above each cluster using THREE.Sprite
  - Register interaction hotspots with concept names and entity counts
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [~] 6.3 Implement Scene 4: Planets of Capability
  - Create `PlanetScene` component with 5-30 capability planets based on config
  - Animate constellations collapsing into spherical planet meshes
  - Scale planet size proportionally to capability importance (lines of code, entity count)
  - Apply color gradients representing health metrics (green=healthy, yellow=warning, red=critical)
  - Render atmospheric glow around planets using shader effects with activity-based intensity
  - Implement camera orbital movement around planet cluster
  - Apply depth of field post-processing blurring distant planets
  - Register interaction hotspots with capability metadata (name, size, health, key entities)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [ ]* 6.4 Write unit tests for Scene 3 and 4
  - Test constellation clustering algorithm produces correct groupings
  - Test planet size scaling based on importance metrics
  - Test color gradient application based on health scores
  - Test camera orbital path generation
  - _Requirements: 5.1, 6.1_

### 7. Scene Implementations - Scenes 5-6

- [~] 7.1 Create scene configuration JSON files for Scenes 5-6
  - Create `scene5-config.json` for Solar Systems with domain groupings
  - Create `scene6-config.json` for Decision Rings with ADR data
  - Define solar system layouts with domain suns and planetary orbits
  - Define decision node positions along orbital rings
  - Define color schemes per domain (Frontend=blue, Backend=purple, Data=green, Infrastructure=orange)
  - _Requirements: 17.1_

- [~] 7.2 Implement Scene 5: Solar Systems of Architecture
  - Create `SolarSystemScene` component grouping planets into domains
  - Position central sun mesh for each architecture domain (Frontend, Backend, Data, Infrastructure)
  - Animate orbital paths for capability planets around domain suns
  - Render connecting energy beams between related planets using `THREE.Line` with flowing shader
  - Apply domain-specific color schemes to suns and planets
  - Implement camera pan between solar systems
  - Register interaction hotspots for domain suns (domain name, capability count, entity count)
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [~] 7.3 Implement Scene 6: Rings of Decisions
  - Create `DecisionRingScene` component adding orbital rings around planets
  - Render orbital ring meshes using `THREE.RingGeometry` with rotation animations
  - Position decision nodes along orbital rings representing ADRs
  - Animate rings rotating at varying speeds
  - Apply visual indicators to decision nodes (accepted=green glow, superseded=gray, deprecated=red)
  - Render connecting lines from decision nodes to affected capability planets
  - Register interaction hotspots with decision metadata (title, date, status, tradeoffs, rationale)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ]* 7.4 Write unit tests for Scene 5 and 6
  - Test solar system layout generation with correct domain groupings
  - Test orbital path calculations for planets
  - Test energy beam connection logic between related planets
  - Test decision node positioning along rings
  - Test visual indicator application based on decision status
  - _Requirements: 7.1, 8.1_

### 8. Scene Implementations - Scenes 7-8

- [~] 8.1 Create scene configuration JSON files for Scenes 7-8
  - Create `scene7-config.json` for Reasoning Network with evidence nodes
  - Create `scene8-config.json` for Universe composite view with all layers
  - Define network node positions and connection rules
  - Define god rays effect parameters
  - Define universe layer rendering order and particle count reductions
  - _Requirements: 17.1_

- [~] 8.2 Implement Scene 7: Constellation of Reasoning
  - Create `ReasoningNetworkScene` component with neural network morphing animation
  - Morph solar system view into neural network visualization
  - Render network nodes representing evidence points with glowing effects
  - Render energy beams connecting nodes using shader with flowing pulses
  - Animate energy pulses simulating reasoning flow
  - Display example questions floating in 3D space using THREE.Sprite with illuminated reasoning paths
  - Apply god rays effect emanating from central reasoning nodes
  - Implement camera fly-through providing immersive network perspective
  - Register interaction hotspots with evidence metadata (type, confidence score, source reference)
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [~] 8.3 Implement Scene 8: The Software Universe
  - Create `UniverseScene` component rendering all layers simultaneously
  - Display layered visualization: particles (innermost) → constellations → planets → solar systems → rings → reasoning network (outermost)
  - Reduce particle counts across all layers to maintain 60 FPS (use LOW quality tier counts)
  - Implement slow camera orbital providing 360-degree universe view
  - Display overlay text "Your Repository as a Living Knowledge Universe" using HTML overlay
  - Render call-to-action button "Explore Your Universe" with navigation to main platform
  - Register interaction hotspots for all element types with layer identification
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [ ]* 8.4 Write unit tests for Scene 7 and 8
  - Test network morphing animation transitions smoothly
  - Test energy pulse flow along network connections
  - Test layered rendering order in universe view
  - Test particle count reductions maintain performance
  - _Requirements: 9.1, 10.1_

### 9. Checkpoint - All Scenes Implemented

- [~] 9. Verify all scenes render correctly
  - Scroll through all 8 scenes verifying smooth transitions
  - Verify particle counts appropriate for each scene
  - Verify camera movement follows defined rails
  - Verify visual effects (bloom, DOF, glows) render correctly
  - Measure FPS in each scene - ensure 60 FPS target met
  - Run all unit tests - verify they pass
  - Ask the user if questions arise.

### 10. Interaction System

- [~] 10.1 Implement Interaction Handler with raycasting
  - Create `InteractionHandler` class managing interactive 3D objects
  - Implement `registerInteractive()` and `unregisterInteractive()` methods
  - Use `THREE.Raycaster` updated on mouse move with 60ms throttling
  - Maintain spatial index (octree) for fast intersection tests
  - Emit hover events when raycast intersects registered objects
  - Emit click events when user clicks on interactive objects
  - Support keyboard interactions (tab navigation + enter/space to activate)
  - _Requirements: 11.1, 11.2_

- [ ]* 10.2 Write property test for raycast intersection detection
  - **Property 4: Raycast Intersection Detection**
  - **Validates: Requirements 11.1**
  - Generate random 3D object positions and sizes
  - Generate random ray directions including edge cases (grazing angles, behind camera)
  - Verify intersection detected for rays that geometrically intersect bounding volumes
  - Test with various object shapes: spheres, boxes, complex meshes
  - _Requirements: 11.1_

- [~] 10.3 Implement interaction highlighting
  - Apply outline shader effect to highlighted objects using edge detection post-process
  - Implement highlight state management (none, hover, selected)
  - Remove highlight within 300ms when cursor moves away
  - Apply highlight within one render frame of intersection detection
  - _Requirements: 11.2, 11.5_

- [ ]* 10.4 Write property test for interaction highlighting
  - **Property 5: Interaction Highlighting**
  - **Validates: Requirements 11.2**
  - Verify highlight applied within one render frame of raycast intersection
  - Test with varying object counts and scene complexity
  - _Requirements: 11.2_

- [~] 10.5 Create Info Card component
  - Create `InfoCard` React component displaying interaction metadata
  - Position info card near cursor, clamped within viewport boundaries
  - Display basic metadata: title, description, icon
  - Support expanded mode showing detailed information with actions
  - Implement smooth fade-in/fade-out animations (300ms)
  - Ensure WCAG 2.1 AA contrast ratios for text content
  - Make responsive across screen sizes
  - _Requirements: 11.3, 11.4, 11.6, 14.9_

- [~] 10.6 Implement camera pause on card expansion
  - Pause camera progression when user clicks interactive object and expands info card
  - Resume camera progression when user closes expanded info card
  - Store pause state in Zustand store
  - Integrate with scroll controller to block automatic progression
  - _Requirements: 11.7, 11.8_

- [ ]* 10.7 Write unit tests for Interaction Handler
  - Test raycaster updates on mouse move
  - Test spatial index queries return correct objects
  - Test hover event emission when intersection detected
  - Test click event emission when user clicks object
  - Test keyboard interaction handling
  - _Requirements: 11.1, 11.2_

- [ ]* 10.8 Write integration tests for interaction flow
  - Test hover shows info card with correct metadata
  - Test click expands card and pauses camera
  - Test closing card resumes camera progression
  - Test keyboard navigation through interactive elements
  - _Requirements: 11.1, 11.2, 11.3, 11.6, 11.7, 11.8_

### 11. Post-Processing Pipeline

- [~] 11.1 Implement post-processing effects
  - Add `EffectComposer` from @react-three/postprocessing
  - Implement selective bloom effect (only glowing objects) with intensity 0.4-0.8
  - Implement depth of field effect with f-stop 1.4, scene-specific focal lengths
  - Implement SSAO with radius 0.5, intensity 0.3
  - Implement color grading with slight blue tint for space aesthetic
  - Make effects toggleable based on quality tier
  - _Requirements: 3.5, 6.8, 12.3_

- [~] 11.2 Implement quality-based effect toggling
  - Disable all post-processing at LOW quality tier
  - Disable DOF and SSAO at MEDIUM quality tier, keep bloom only
  - Enable bloom + DOF at HIGH quality tier
  - Enable all effects at ULTRA quality tier
  - Listen to quality change events from Performance Monitor
  - _Requirements: 12.3_

- [ ]* 11.3 Write unit tests for post-processing
  - Test effect composition order
  - Test quality tier toggles correct effects
  - Test effect parameters update correctly
  - _Requirements: 12.3_

### 12. Audio System

- [~] 12.1 Implement Audio System
  - Create `AudioSystem` class managing ambient soundtrack and sound effects
  - Load ambient space soundtrack looping throughout journey
  - Implement spatial audio positioning sounds based on 3D object locations
  - Play transition sound effects on scene changes
  - Play subtle hover sound effects on interaction
  - Adjust volume based on scene intensity
  - Default to audio disabled respecting autoplay policies
  - _Requirements: 13.1, 13.2, 13.3, 13.5, 13.6, 13.7_

- [~] 12.2 Create Audio Toggle UI
  - Create `AudioToggle` component with enable/disable button
  - Display current audio state (enabled/disabled, volume level)
  - Allow volume adjustment via slider
  - Store audio preferences in localStorage
  - _Requirements: 13.4_

- [ ]* 12.3 Write unit tests for Audio System
  - Test audio playback starts/stops correctly
  - Test spatial audio positioning calculations
  - Test volume adjustments apply correctly
  - Test audio state persistence
  - _Requirements: 13.1, 13.4_

### 13. Accessibility Features

- [~] 13.1 Implement Accessibility Controller
  - Create `AccessibilityController` class managing accessibility features
  - Detect user's `prefers-reduced-motion` system setting
  - Provide reduced motion mode disabling particle animations and camera movement
  - Display static scene screenshots with text descriptions in reduced motion mode
  - Support keyboard navigation with arrow keys controlling camera movement
  - Support keyboard shortcuts to jump between scenes (number keys 1-8)
  - Display keyboard hints in info cards when keyboard focus on elements
  - _Requirements: 14.1, 14.2, 14.3, 14.6, 14.7, 14.8_

- [~] 13.2 Create Skip Animation button
  - Create `SkipButton` component visible at all times
  - Navigate to Scene 8 immediately when activated
  - Update scroll position and progress state
  - Provide clear visual feedback on activation
  - _Requirements: 14.4, 14.5_

- [~] 13.3 Implement screen reader support
  - Add ARIA labels to all interactive elements
  - Provide screen reader announcements for scene transitions
  - Announce interactive element focus changes
  - Ensure info card content is screen reader accessible
  - Test with NVDA and JAWS screen readers
  - _Requirements: 14.10_

- [~] 13.4 Create static fallback for reduced motion
  - Create high-quality screenshots of each scene
  - Create text narratives describing each scene transformation
  - Display slideshow with navigation controls
  - Ensure content equivalence with animated version
  - _Requirements: 14.2, 14.3_

- [ ]* 13.5 Write integration tests for accessibility
  - Test prefers-reduced-motion detection triggers static mode
  - Test keyboard navigation controls camera movement
  - Test scene jump shortcuts work correctly
  - Test skip button navigates to final scene
  - Test screen reader announcements fire on scene transitions
  - _Requirements: 14.1, 14.2, 14.4, 14.6, 14.7, 14.10_

### 14. Responsive Design

- [~] 14.1 Implement responsive rendering adjustments
  - Detect viewport width and adjust particle counts accordingly
  - Full quality (max particles) for width >1920px
  - Reduce particles by 30% for width 1280-1920px
  - Reduce particles by 50% and disable DOF for width <1280px
  - Adjust camera FOV based on viewport aspect ratio
  - Reposition and resize info cards responsively
  - Update rendering parameters within 500ms of viewport resize
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [~] 14.2 Add portrait orientation message
  - Detect portrait orientation (aspect ratio <1.0)
  - Display message recommending landscape orientation
  - Allow user to dismiss and continue in portrait mode
  - _Requirements: 15.7_

- [ ]* 14.3 Write unit tests for responsive adjustments
  - Test particle count calculations at various viewport widths
  - Test FOV calculations for different aspect ratios
  - Test info card repositioning logic
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

### 15. Checkpoint - Interactions and UI Complete

- [~] 15. Verify interactions and UI
  - Test hover and click on various interactive elements
  - Verify info cards display with correct metadata
  - Verify camera pauses on card expansion
  - Test audio toggle and volume controls
  - Test accessibility features (keyboard nav, skip button, reduced motion)
  - Test responsive behavior at various screen sizes
  - Run all unit and integration tests - verify they pass
  - Ask the user if questions arise.

### 16. Platform Integration

- [~] 16.1 Implement repository context passing
  - Define `RepositoryContext` interface with repo ID, name, metadata
  - Store context in session storage when user completes onboarding
  - Pass context via URL parameters when navigating to main platform
  - Create `navigateToUniverseView()` function with context transfer
  - _Requirements: 19.2, 19.7_

- [~] 16.2 Implement scene element click handlers
  - Define route mappings for all interactive elements in Scene 8
  - Handle clicks on planets, decisions, reasoning nodes navigating to corresponding features
  - Pass repository context and element ID to target routes
  - _Requirements: 19.6, 19.7_

- [~] 16.3 Implement progress persistence
  - Define `OnboardingProgress` interface with scene, progress, timestamp
  - Save progress to localStorage on scene transitions
  - Load saved progress on app initialization
  - Offer resume or restart options for returning users
  - Mark completion when user reaches Scene 8
  - _Requirements: 19.3, 19.4_

- [~] 16.4 Add completion screen with navigation options
  - Display navigation buttons to Architecture Studio, Decision Intelligence, Reasoning Layer
  - Add "Explore Your Universe" primary CTA button
  - Add "Replay Tour" option
  - Style with Framer Motion animations
  - _Requirements: 10.7, 19.1, 19.5_

- [ ]* 16.5 Write unit tests for platform integration
  - Test repository context serialization/deserialization
  - Test route mapping lookups
  - Test progress persistence save/load
  - Test resume offer logic
  - _Requirements: 19.2, 19.3, 19.4, 19.6_

### 17. Analytics and Monitoring

- [~] 17.1 Implement analytics tracking
  - Create `OnboardingAnalyticsTracker` class implementing analytics interface
  - Track scene entry events with scene number, name, timestamp
  - Track scene exit events with time spent
  - Track user interactions (hover, click, element types)
  - Track performance metrics (FPS, quality adjustments, load times)
  - Track completion events (reached Scene 8 or skipped)
  - Track accessibility feature usage (skip, reduced motion, keyboard nav)
  - Send events to configurable analytics endpoint without blocking rendering
  - Respect user privacy settings and provide opt-out
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8_

- [~] 17.2 Implement error tracking
  - Track WebGL initialization failures with browser details
  - Track asset loading failures with specific URLs
  - Track shader compilation errors
  - Track memory overflow events
  - Track frame rate crashes (FPS drops to 0)
  - Integrate with error reporting service (e.g., Sentry)
  - _Requirements: 1.4_

- [ ]* 17.3 Write unit tests for analytics
  - Test event emission with correct properties
  - Test privacy opt-out prevents event sending
  - Test scene time calculations
  - Test event batching and throttling
  - _Requirements: 20.1, 20.2, 20.8_

### 18. Error Handling and Fallbacks

- [~] 18.1 Implement WebGL initialization error handling
  - Detect WebGL support on page load
  - Check for required extensions (OES_texture_float, WEBGL_depth_texture)
  - Display fallback message with browser upgrade recommendations if unsupported
  - Display limited experience message if extensions missing
  - _Requirements: 1.4_

- [~] 18.2 Implement asset loading error handling
  - Add retry logic with exponential backoff (already in Asset Loader)
  - Display user-friendly notifications for permanent load failures
  - Load placeholder assets when originals fail
  - Allow experience to continue with degraded visuals
  - _Requirements: 16.6_

- [~] 18.3 Implement performance degradation handling
  - Monitor for WebGL context lost events
  - Implement context recovery with quality downgrade
  - Implement crash detection (multiple failures → safe mode)
  - Enter safe mode with static fallback after 3 crashes
  - Display user-friendly error messages
  - _Requirements: 12.2, 12.3_

- [~] 18.4 Implement graceful degradation levels
  - Level 1: Full Experience (WebGL 2.0, all extensions)
  - Level 2: Reduced Quality (WebGL 1.0, lower particle counts, no post-processing)
  - Level 3: Static Slideshow (no WebGL, image-based scenes with text)
  - Level 4: Text-Only (extreme fallback, complete text descriptions)
  - Automatically select appropriate level based on capabilities
  - _Requirements: 1.4_

- [ ]* 18.5 Write unit tests for error handling
  - Test WebGL support detection logic
  - Test fallback mode selection
  - Test error message display
  - Test crash recovery attempts
  - _Requirements: 1.4_

### 19. Checkpoint - Integration and Error Handling Complete

- [~] 19. Verify platform integration and error handling
  - Test navigation to main platform with repository context
  - Test progress persistence and resume functionality
  - Test analytics events fire correctly
  - Test error handling for various failure scenarios
  - Test graceful degradation levels
  - Run all unit and integration tests - verify they pass
  - Ask the user if questions arise.

### 20. UI Components and Overlays

- [~] 20.1 Create Progress Indicator component
  - Create `ProgressIndicator` component showing journey completion percentage
  - Display scene indicators (1-8) with current scene highlighted
  - Show smooth progress bar animation
  - Position fixed at screen edge (top or side)
  - Style with space aesthetic matching overall design
  - _Requirements: 1.3_

- [~] 20.2 Create Navigation Hints component
  - Create `NavigationHints` component displaying scroll instructions
  - Show "Scroll to explore" message on first load
  - Display keyboard shortcut hints for keyboard navigation users
  - Auto-hide after user starts scrolling
  - Style with subtle animations
  - _Requirements: 14.8_

- [~] 20.3 Create Loading Screen component
  - Create `LoadingScreen` component with progress percentage
  - Display asset loading status with granular updates
  - Show animated space-themed loading graphics
  - Fade out smoothly when Scene 1 is ready
  - _Requirements: 1.3_

- [~] 20.4 Style all UI components
  - Apply color palette (Deep Space Black, Nebula Purple, Cosmic Blue, etc.)
  - Use Inter font family with appropriate weights
  - Ensure WCAG 2.1 AA contrast ratios
  - Add responsive styles for all screen sizes
  - Apply Framer Motion animations for smooth transitions
  - _Requirements: 14.9_

- [ ]* 20.5 Write unit tests for UI components
  - Test progress indicator updates correctly with scroll progress
  - Test navigation hints display and hide logic
  - Test loading screen progress updates
  - Test component responsiveness at various screen sizes
  - _Requirements: 1.3_

### 21. Memory Management

- [~] 21.1 Implement Memory Manager
  - Create `MemoryManager` class tracking texture and geometry memory
  - Set maximum texture memory budget (512MB)
  - Implement `disposeScene()` method properly disposing geometries, materials, textures
  - Traverse scene graph calling dispose on all disposable objects
  - Track memory usage and enforce budget limits
  - _Requirements: 12.10, 16.7_

- [~] 21.2 Integrate memory management with Scene Manager
  - Call `disposeScene()` when unloading scenes >2 positions away
  - Verify no memory leaks with Chrome DevTools heap snapshots
  - Test memory usage stays below 512MB budget during full journey
  - _Requirements: 12.10, 16.7_

- [ ]* 21.3 Write unit tests for Memory Manager
  - Test texture memory estimation calculations
  - Test disposal methods called for all materials and geometries
  - Test memory tracking updates correctly
  - _Requirements: 12.10_

### 22. Performance Optimization

- [~] 22.1 Implement texture compression
  - Convert textures to WebP format for color maps
  - Use Basis Universal for normal maps and roughness maps
  - Implement compression in asset build pipeline
  - Measure and compare texture file sizes before/after
  - _Requirements: 12.10_

- [~] 22.2 Implement model compression
  - Apply Draco compression to all GLTF/GLB models
  - Configure compression level balancing size vs. quality
  - Integrate compression in asset build pipeline
  - Measure model file sizes and load times
  - _Requirements: 12.10_

- [~] 22.3 Optimize draw calls
  - Verify instanced meshes used for all repeated geometry
  - Verify texture atlases minimize material switches
  - Use Chrome DevTools GPU profiler to analyze draw calls
  - Target <100 draw calls per frame
  - _Requirements: 3.2, 12.8, 12.9_

- [ ]* 22.4 Write performance benchmark tests
  - Measure initial load time (target <3s for Scene 1)
  - Measure FPS in each scene with varying particle counts
  - Measure memory usage across all scenes
  - Measure scene transition frame times (target <16ms)
  - Run benchmarks on multiple hardware tiers (high-end, mid-range, low-end)
  - _Requirements: 1.1, 1.2, 12.1_

### 23. Checkpoint - Performance and Memory Optimized

- [~] 23. Verify performance and memory optimization
  - Verify initial load completes in <3s for Scene 1
  - Verify 60 FPS maintained in all scenes at HIGH quality
  - Verify memory usage stays below 512MB
  - Verify draw calls <100 per frame
  - Verify texture compression reduces file sizes significantly
  - Run all performance benchmark tests - verify targets met
  - Ask the user if questions arise.

### 24. Integration Testing

- [ ]* 24.1 Write end-to-end test for full journey flow
  - User loads onboarding page
  - Scrolls through all 8 scenes
  - Verifies each scene renders correctly
  - Reaches completion screen
  - Clicks "Explore Your Universe" button
  - Verifies navigation to main platform with correct repository context
  - _Requirements: 1.1, 2.1, 19.2_

- [ ]* 24.2 Write end-to-end test for interaction flow
  - User hovers over planet in Scene 4
  - Info card appears with correct metadata
  - User clicks planet
  - Expanded card shows detailed information
  - User closes card
  - Camera progression resumes
  - _Requirements: 11.1, 11.2, 11.3, 11.6, 11.7, 11.8_

- [ ]* 24.3 Write end-to-end test for accessibility flow
  - User with prefers-reduced-motion loads page
  - Static scene screenshots displayed
  - User navigates with keyboard (arrow keys, number keys)
  - Screen reader announcements verified
  - _Requirements: 14.1, 14.2, 14.3, 14.6, 14.7, 14.10_

- [ ]* 24.4 Write end-to-end test for performance adaptation flow
  - Simulate low FPS environment using Chrome DevTools CPU throttling
  - Verify automatic quality downgrade
  - Verify particle count reduction
  - Verify post-processing effects disabled
  - _Requirements: 12.2, 12.3_

- [ ]* 24.5 Write end-to-end test for asset loading flow
  - Simulate slow network using Chrome DevTools network throttling
  - Verify loading indicators displayed
  - Verify progressive scene loading
  - Verify cached assets used on second visit
  - _Requirements: 16.1, 16.2, 16.3, 16.8_

### 25. Visual Regression Testing

- [ ]* 25.1 Set up visual regression testing with Percy/Chromatic
  - Install Percy or Chromatic CLI and SDK
  - Configure snapshot capture for all 8 scenes
  - Define snapshot points at key camera positions per scene
  - Set up baseline images
  - Integrate with CI pipeline
  - _Requirements: All scene requirements_

- [ ]* 25.2 Capture UI component snapshots
  - Capture info card states (hover, expanded, closed)
  - Capture loading screen
  - Capture progress indicator
  - Capture navigation hints
  - Capture skip button
  - Capture audio toggle
  - _Requirements: 11.3, 13.2, 14.4_

- [ ]* 25.3 Capture fallback view snapshots
  - Capture reduced motion static views
  - Capture WebGL unsupported fallback
  - Capture portrait orientation message
  - _Requirements: 14.2, 14.3, 15.7, 1.4_

### 26. Documentation and Polish

- [~] 26.1 Write developer documentation
  - Document architecture and component hierarchy
  - Document scene configuration JSON schema
  - Document particle system API
  - Document camera rail definition format
  - Document interaction metadata format
  - Document performance optimization techniques
  - Document accessibility features
  - _Requirements: All requirements_

- [~] 26.2 Write user guide
  - Create visual guide showing navigation controls
  - Document keyboard shortcuts
  - Document accessibility features for users
  - Create troubleshooting section for common issues
  - _Requirements: 14.6, 14.7, 14.8_

- [~] 26.3 Final polish and bug fixes
  - Review all animations for smoothness
  - Review all transitions for timing
  - Fix any visual glitches or artifacts
  - Ensure consistent styling across all components
  - Test on multiple browsers (Chrome, Firefox, Safari, Edge)
  - Test on multiple devices (desktop, laptop, tablet)
  - _Requirements: All requirements_

### 27. Final Checkpoint - Production Readiness

- [~] 27. Verify production readiness
  - All 8 scenes render correctly with smooth transitions
  - All interactions work (hover, click, keyboard)
  - All accessibility features functional
  - All analytics events tracked correctly
  - Performance targets met (60 FPS, <3s load, <512MB memory)
  - All tests passing (unit, property-based, integration, visual regression)
  - Error handling works for all failure scenarios
  - Documentation complete
  - Ask the user if questions arise.


## Notes

- **Tasks marked with `*` are optional** and can be skipped for faster MVP delivery. These include all test-related sub-tasks (unit tests, property tests, integration tests, visual regression tests).
- **Core implementation tasks (unmarked) must be implemented** to deliver a functional cinematic onboarding experience.
- **Each task references specific requirements** for traceability using `_Requirements: X.Y_` notation.
- **Checkpoints ensure incremental validation** - stop and verify functionality before proceeding to the next phase.
- **Property tests validate universal correctness properties** defined in the design document using fast-check.
- **Unit tests validate specific examples and edge cases** for individual components and functions.
- **Integration tests validate end-to-end user flows** across multiple components using Playwright.
- **Visual regression tests ensure UI consistency** across changes using Percy or Chromatic.
- **Implementation follows bottom-up approach**: infrastructure → particle systems → scenes → interactions → integration.
- **All code examples in the design use TypeScript** - use TypeScript throughout the implementation.
- **Performance is critical**: maintain 60 FPS target across all hardware tiers through adaptive quality, LOD, frustum culling, instancing.
- **Accessibility is non-negotiable**: provide reduced motion mode, keyboard navigation, screen reader support.

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1.1", "1.2"]
    },
    {
      "id": 1,
      "tasks": ["1.3", "1.5", "1.7", "1.9", "1.12", "1.14", "1.16"]
    },
    {
      "id": 2,
      "tasks": ["1.4", "1.6", "1.8", "1.10", "1.11", "1.13", "1.15"]
    },
    {
      "id": 3,
      "tasks": ["3.1", "3.2", "3.3", "3.4", "3.6", "3.7", "5.1"]
    },
    {
      "id": 4,
      "tasks": ["3.5", "5.2", "5.3"]
    },
    {
      "id": 5,
      "tasks": ["5.4", "6.1"]
    },
    {
      "id": 6,
      "tasks": ["6.2", "6.3"]
    },
    {
      "id": 7,
      "tasks": ["6.4", "7.1"]
    },
    {
      "id": 8,
      "tasks": ["7.2", "7.3"]
    },
    {
      "id": 9,
      "tasks": ["7.4", "8.1"]
    },
    {
      "id": 10,
      "tasks": ["8.2", "8.3"]
    },
    {
      "id": 11,
      "tasks": ["8.4", "10.1", "10.3", "10.5", "10.6"]
    },
    {
      "id": 12,
      "tasks": ["10.2", "10.4", "10.7", "10.8", "11.1", "11.2", "12.1", "12.2"]
    },
    {
      "id": 13,
      "tasks": ["11.3", "12.3", "13.1", "13.2", "13.3", "13.4"]
    },
    {
      "id": 14,
      "tasks": ["13.5", "14.1", "14.2"]
    },
    {
      "id": 15,
      "tasks": ["14.3", "16.1", "16.2", "16.3", "16.4"]
    },
    {
      "id": 16,
      "tasks": ["16.5", "17.1", "17.2"]
    },
    {
      "id": 17,
      "tasks": ["17.3", "18.1", "18.2", "18.3", "18.4"]
    },
    {
      "id": 18,
      "tasks": ["18.5", "20.1", "20.2", "20.3", "20.4"]
    },
    {
      "id": 19,
      "tasks": ["20.5", "21.1", "21.2"]
    },
    {
      "id": 20,
      "tasks": ["21.3", "22.1", "22.2", "22.3"]
    },
    {
      "id": 21,
      "tasks": ["22.4", "24.1", "24.2", "24.3", "24.4", "24.5"]
    },
    {
      "id": 22,
      "tasks": ["25.1", "25.2", "25.3"]
    },
    {
      "id": 23,
      "tasks": ["26.1", "26.2", "26.3"]
    }
  ]
}
```
