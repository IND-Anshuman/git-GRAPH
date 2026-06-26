# Cinematic Onboarding Experience

A GPU-accelerated, scroll-driven 3D journey built with Next.js 15, React Three Fiber, and Three.js that transforms users' understanding of the Software Intelligence Platform through eight interconnected cinematic scenes.

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Strict type checking
- **React Three Fiber** - React renderer for Three.js
- **Three.js** - WebGL 3D graphics library
- **@react-three/drei** - Helper components for R3F
- **GSAP** - Animation library with ScrollTrigger
- **Zustand** - Lightweight state management
- **Framer Motion** - Animation library for UI overlays
- **Tailwind CSS** - Utility-first CSS framework

## Testing Stack

- **Vitest** - Unit testing framework
- **@testing-library/react** - React component testing
- **fast-check** - Property-based testing
- **Playwright** - End-to-end testing

## Project Structure

```
cinematic-onboarding/
├── app/                 # Next.js App Router pages
├── components/          # React components (2D UI + 3D scenes)
├── lib/                 # Utility functions and helpers
├── hooks/               # Custom React hooks
├── stores/              # Zustand state stores
├── config/              # Scene configurations (JSON)
├── shaders/             # GLSL shader programs
├── types/               # TypeScript type definitions
├── public/assets/       # Static assets (models, textures, audio)
├── e2e/                 # Playwright E2E tests
└── vitest.setup.ts      # Vitest test setup
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run test` - Run unit tests in watch mode
- `npm run test:run` - Run unit tests once
- `npm run test:coverage` - Generate test coverage report
- `npm run test:e2e` - Run Playwright E2E tests
- `npm run test:e2e:ui` - Run E2E tests with UI
- `npm run type-check` - TypeScript type checking

## Architecture

The experience consists of 8 cinematic scenes:

1. **The Chaos** - Millions of code fragments floating in chaos
2. **Stardust of Code** - Repository decomposed into semantic particles
3. **Knowledge Constellations** - Particles clustering into concepts
4. **Planets of Capability** - Constellations forming capability planets
5. **Solar Systems of Architecture** - Capabilities organized into domains
6. **Rings of Decisions** - Architectural decisions orbiting capabilities
7. **Constellation of Reasoning** - Neural network of evidence-backed reasoning
8. **The Software Universe** - Complete knowledge universe visualization

## Performance Targets

- 60 FPS on modern hardware
- Automatic quality adjustment based on performance
- LOD (Level of Detail) system for distant objects
- Frustum culling for off-screen objects
- GPU-accelerated particle systems with instanced rendering

## Accessibility

- Keyboard navigation support
- Reduced motion mode
- Skip animation option
- WCAG 2.1 AA compliant UI elements
- Screen reader announcements

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 15+

Requires WebGL 2.0 support.

## License

Proprietary - All rights reserved
