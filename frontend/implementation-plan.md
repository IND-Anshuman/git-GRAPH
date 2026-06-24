# Implementation Plan: Software Intelligence Platform

## Overview

This document provides the actionable implementation roadmap for the Software Intelligence Platform frontend.

**Stage 1 Status:** ✅ COMPLETE (All 60+ tasks implemented)  
**Stage 2 Status:** 📋 PLANNING IN PROGRESS

---

## STAGE 1: COMPLETE ✅

All 14 phases and 60+ tasks have been successfully implemented with production-grade quality.

### Implementation Summary

- **Framework:** Next.js 16 + Turbopack (upgraded from planned Next.js 15)
- **React:** React 19 with TypeScript strict mode
- **Components:** 60+ fully functional components
- **Architecture:** Three-tier (UI → State → API) operational
- **Performance:** All targets exceeded (<3s load, <500KB bundle, ≥55 FPS)
- **Quality:** Zero `any` types, WCAG AA compliant, error-resilient

### Stage 1 Phases (All Complete)

### Phase 1: Project Bootstrap & Design System (8 Tasks)
**Estimated Duration:** 4-6 hours | **Complexity:** Medium

#### Task 1.1: Initialize Next.js 15 Project
- Create Next.js 15 app with TypeScript strict mode
- Directory structure: `/frontend` at project root
- Features: App Router, src/ directory, ESLint enabled
- **Acceptance:** `next dev` runs without errors, TypeScript strict config validates

#### Task 1.2: Install All Dependencies
- Core: @tanstack/react-query, zustand, framer-motion, axios
- UI: @radix-ui/react-*, shadcn/ui, lucide-react, recharts
- Utilities: clsx, tailwind-merge, class-variance-authority, fuse.js
- Dev: typescript, eslint, prettier, @types/react, @types/node
- **Acceptance:** All packages install, package.json frozen versions, no peer dependency conflicts

#### Task 1.3: Configure TypeScript Strict Mode
- Set noImplicitAny, strictNullChecks, strictFunctionTypes true
- Configure baseUrl aliases: @/* → ./src/*
- Enable sourceMap, declaration for debugging
- **Acceptance:** `tsc --noEmit` passes, all type errors resolved

#### Task 1.4: Create Design Token System (tokens.ts)
- Define tokens object: colors, typography, spacing, shadows, radii, transitions, zIndex
- Export TypeScript constants for programmatic access
- Support 10-tier neutral gray scale, semantic colors (success/warning/error/info)
- **Acceptance:** tokens.ts exports all required scales, no magic numbers, type-safe exports
- **References:** Design Spec Part 7.1

#### Task 1.5: Implement Global Styles & CSS Variables
- Create globals.css with CSS variable definitions
- Set up @layer base/components/utilities for Tailwind
- Define motion animations (@keyframes fadeIn, slideUp, scale)
- Configure focus indicators, reduced-motion media query support
- **Acceptance:** CSS variables output in browser dev tools, animations smooth on prefers-reduced-motion: reduce
- **References:** Design Spec Part 7.2, Requirement 1

#### Task 1.6: Configure TailwindCSS with Design Tokens
- Create tailwind.config.ts extending default theme
- Map colors (bg-primary, neutral, success, error, etc.)
- Extend spacing, borderRadius, boxShadow, transitionDuration
- Preserve shadcn/ui defaults (no conflicts)
- **Acceptance:** `npm run build` succeeds, colors apply correctly in browser
- **References:** Design Spec Part 7.3

#### Task 1.7: Initialize shadcn/ui Components
- Add all required components: Button, Card, Input, Badge, Dialog, Dropdown, Tabs, Tooltip, etc.
- Configure component aliases in tsconfig.json
- Verify all components compile without errors
- **Acceptance:** All components importable, no build errors, visual inspection in Storybook (if setup)

#### Task 1.8: Set Up ESLint & Prettier
- Configure ESLint for TypeScript/React (next/eslint config)
- Set up Prettier with consistent formatting rules
- Create .prettierrc with 80-char line length, semicolons, trailing commas
- Add pre-commit hook (optional for CI/CD)
- **Acceptance:** `npm run lint` and `npm run format` work without errors

---

### Phase 2: API Integration Layer (6 Tasks)
**Estimated Duration:** 5-7 hours | **Complexity:** High

#### Task 2.1: Define API Response Types
- Create types/api.ts with Capability, Concept, Entity, Repository, SearchResult
- Define PaginatedResponse, DashboardResponse, ErrorResponse
- Add JSDoc comments for all interfaces
- **Acceptance:** All types compile, match backend schema assumptions
- **References:** Design Spec Part 12.3, Requirement 8

#### Task 2.2: Create Axios Base Client
- Implement APIClient class with axios instance
- Add request/response interceptors for logging
- Store requestId in config for tracing
- Implement timeout (10 seconds)
- **Acceptance:** Client logs requests/responses to console in development
- **References:** Design Spec Part 6.1

#### Task 2.3: Implement Error Normalization
- Create DomainError type with code, message, status, details
- Map HTTP status codes to domain error codes (NOT_FOUND, UNAUTHORIZED, etc.)
- Add retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Acceptance:** Failed requests trigger retries, errors serialize correctly
- **References:** Design Spec Part 6.1, Requirement 8

#### Task 2.4: Create Type-Safe Endpoint Functions
- Implement fetchCapabilities, fetchCapability, fetchConcepts, fetchSearch
- All functions return typed responses
- Each function handles errors with domain normalization
- **Acceptance:** Type checking prevents calling endpoints incorrectly
- **References:** Design Spec Part 6.2

#### Task 2.5: Create TanStack Query Key Factory
- Build queryKeys object with hierarchical structure
- Include repositories.all, capabilities.list, concepts.detail, search.results
- Support filter objects as keys: queryKeys.capabilities.list(filters)
- **Acceptance:** Keys can be used to invalidate capabilities when filters change
- **References:** Design Spec Part 5.1, Requirement 8

#### Task 2.6: Configure TanStack Query (QueryClient)
- Create QueryClient with defaults: 5-min staleTime, 10-min gcTime
- Set up retry: 2 attempts with exponential backoff
- Enable refetchOnWindowFocus: 'stale'
- Add global error handler for toast notifications (stub)
- **Acceptance:** QueryClient initializes without errors, cache times respected
- **References:** Design Spec Part 5.3

---

### Phase 3: State Management with Zustand (4 Tasks)
**Estimated Duration:** 2-3 hours | **Complexity:** Low-Medium

#### Task 3.1: Implement UI Store
- Create useUIStore: sidebarOpen, selectedCapabilityId, activeDetailTab, expandedCategories, reducedMotion
- Add actions: setSidebarOpen, setSelectedCapabilityId, setActiveDetailTab, toggleCategory, setReducedMotion
- Enable persist middleware for sidebarOpen, activeDetailTab, reducedMotion
- **Acceptance:** State persists on page refresh, no hydration mismatch
- **References:** Design Spec Part 4.1

#### Task 3.2: Implement Search Store
- Create useSearchStore: recentSearches (last 10), addRecentSearch, clearRecentSearches
- Each recent search: { query, timestamp, resultCount }
- Dedup by query text (replace old with new)
- Enable persist middleware
- **Acceptance:** Recent searches appear in search modal, persisted across refreshes
- **References:** Design Spec Part 4.2

#### Task 3.3: Implement Command Palette Store
- Create useCommandPaletteStore: isOpen, setIsOpen, recentCommands, recordCommandExecution
- Track command execution count and last executed timestamp
- Keep last 20 commands
- Enable persist middleware
- **Acceptance:** Command execution records correctly, recent commands listed first

#### Task 3.4: Set Up Store Initialization & Exports
- Create stores/index.ts exporting all stores
- Verify no cross-store dependencies
- Add store initialization in app/layout.tsx
- **Acceptance:** All stores initialize on app start, no circular dependencies

---

### Phase 4: Custom Hooks (7 Tasks)
**Estimated Duration:** 4-5 hours | **Complexity:** Medium

#### Task 4.1: Create useRepositories Hook
- Wrap useQuery for GET /repositories
- Cache time: 10 minutes (repo metadata changes infrequently)
- No refetch on window focus (repo list is stable)
- **Acceptance:** Hook returns typed Repository[], cached correctly
- **References:** Design Spec Part 5.2

#### Task 4.2: Create useCapabilities Hook
- Wrap useQuery with CapabilityFilters params (search, category, riskLevel, dependencyCount, recency, limit, offset)
- Cache time: 2 minutes (filters change frequently)
- Enable refetchOnWindowFocus: 'stale'
- **Acceptance:** Hook accepts filters, invalidates cache on filter change
- **References:** Design Spec Part 5.2, Requirement 3

#### Task 4.3: Create useCapability Hook
- Wrap useQuery for GET /capabilities/{id}
- Cache time: 3 minutes
- Add enabled flag to prevent fetch if id is null
- **Acceptance:** Hook only fetches when id is provided
- **References:** Design Spec Part 5.2

#### Task 4.4: Create useSearch Hook
- Wrap useQuery with debounced query (300ms)
- Cache time: 2 minutes (search results cached locally)
- Enabled: query length >= 2
- Return: { data: SearchResult, isLoading, error }
- **Acceptance:** Rapid typing doesn't trigger multiple API calls
- **References:** Design Spec Part 5.2, Requirement 5

#### Task 4.5: Create useConcepts Hook
- Wrap useQuery for GET /concepts with filters
- Cache time: 3 minutes
- **Acceptance:** Hook works like useCapabilities but for concepts

#### Task 4.6: Create useKeyboardShortcut Hook
- Listen for Ctrl+K (Cmd+K on macOS) for command palette
- Listen for Cmd+/ (Ctrl+/ on Windows) for search
- Support keyboard navigation in modals
- **Acceptance:** Shortcuts trigger without conflicts
- **References:** Requirement 6, Requirement 5

#### Task 4.7: Create useNetworkStatus Hook
- Detect navigator.onLine
- Detect connection type (4g, 3g, 2g) via NavigationNetworkInformation API
- Emit 'offline' banner if offline
- Emit 'slow connection' banner if 2g/3g
- **Acceptance:** Banner appears when offline, disappears when back online
- **References:** Design Spec Part 11.3

---

### Phase 5: UI Components (12 Tasks)
**Estimated Duration:** 8-10 hours | **Complexity:** Medium

#### Task 5.1: Create Common Components (ScoreRing, StatusBadge, MetricCard)
- ScoreRing: circular progress ring (0-100 score), animated
- StatusBadge: health/risk badge with color mapping (healthy→green, critical→red)
- MetricCard: KPI card with title, value, change indicator, icon
- **Acceptance:** Components render without errors, animations work
- **References:** Design Spec Part 8

#### Task 5.2: Create ErrorBoundary Component
- Wrap entire app at root
- Catch errors and display user-friendly message
- Show error details in development mode
- Include "Try Again" button to reset boundary
- **Acceptance:** App doesn't white-screen on error, recovery works
- **References:** Design Spec Part 11.1, Requirement 14

#### Task 5.3: Create Modal/Dialog Wrapper
- Generic modal component built on @radix-ui/dialog
- Support title, description, closeButton
- Manage focus trap and escape key handling
- **Acceptance:** Focus trapped inside modal, escape closes
- **References:** Design Spec Part 8, Requirement 10

#### Task 5.4: Create Tooltip & Popover Components
- Built on @radix-ui/tooltip and @radix-ui/popover
- Support side, align, trigger options
- **Acceptance:** Tooltips appear on hover, popovers on click

#### Task 5.5: Create Icon Library Setup
- Wrap lucide-react icons
- Export common icons: ChevronDown, Search, Settings, AlertTriangle, Check, X, etc.
- **Acceptance:** Icons render with consistent sizing and styling

#### Task 5.6: Create LoadingSpinner Component
- Animated spinner using Framer Motion
- Support size variants (sm, md, lg)
- Respect reduced-motion preference
- **Acceptance:** Spinner animates smoothly, stops on reduced-motion
- **References:** Design Spec Part 1, Requirement 9

#### Task 5.7: Create PageShell Wrapper
- Generic layout for pages (header, main, footer)
- Support breadcrumbs
- Manage page transitions with Framer Motion
- **Acceptance:** Page transitions fade smoothly

#### Task 5.8: Create WidgetContainer Component
- Container for dashboard widgets
- Support loading skeleton state
- Support error state with retry button
- Prevent layout shift with skeleton matching dimensions
- **Acceptance:** Skeletons match final widget dimensions
- **References:** Requirement 2

#### Task 5.9: Create CapabilityCard Component
- Display capability name, description, risk level, category
- Show expandable details on click
- Support selection state (highlighted border)
- **Acceptance:** Card renders capability data correctly

#### Task 5.10: Create RiskBadge Component
- Color-coded badge for risk levels (low/medium/high/critical)
- Accessibility: aria-label with full risk description
- **Acceptance:** Colors match design tokens, WCAG AA contrast

#### Task 5.11: Create HealthIndicator Component
- Status circle with color (healthy→green, warning→yellow, critical→red)
- Support size variants
- **Acceptance:** Indicator renders correct color for status

#### Task 5.12: Create EmptyState Component
- Generic empty state with icon, message, optional action button
- Support different empty state types (no results, no data, error)
- **Acceptance:** Used in search results, capability navigator, tab panels
- **References:** Requirement 3, Requirement 5

---

### Phase 6: Layout Components (5 Tasks)
**Estimated Duration:** 3-4 hours | **Complexity:** Medium

#### Task 6.1: Create AppShell Component
- Root layout wrapper combining Sidebar + TopBar + MainContent
- Render Command Palette & Search Modal globally
- Apply ErrorBoundary at top level
- **Acceptance:** App structure renders without errors
- **References:** Design Spec Part 3.1

#### Task 6.2: Create Sidebar Component
- Navigation links: Dashboard, Capabilities, Settings
- Disabled placeholders: Architecture, Decisions, Reasoning, Timeline (with "Coming Soon" badge)
- Collapsible on mobile (<lg breakpoint)
- Store sidebar state in Zustand
- **Acceptance:** Navigation works, disabled items show badge, collapse toggles
- **References:** Requirement 7, Design Spec Part 12

#### Task 6.3: Create TopBar Component
- Repository selector dropdown (placeholder: "Current Repository")
- Global search trigger (opens SearchModal)
- Notifications bell (placeholder)
- Profile menu (placeholder)
- **Acceptance:** Search trigger opens modal, dropdowns function

#### Task 6.4: Create RepositorySelector Component
- Dropdown showing list of repositories
- Select one to set active repository
- Store selection in Zustand
- **Acceptance:** Repository selector dropdown works, selection persists

#### Task 6.5: Create Breadcrumbs Component
- Display current page path
- Support clickable breadcrumb navigation
- **Acceptance:** Breadcrumbs appear on pages, clicking navigates

---

### Phase 7: Dashboard Page (5 Tasks)
**Estimated Duration:** 3-4 hours | **Complexity:** Medium

#### Task 7.1: Create Dashboard Layout
- 2-column grid on desktop (lg+): Health+Inventory left, Dependencies+Changes right
- Single column on tablet (md): Health→Inventory→Changes→Dependencies stacking
- Vertical stack on mobile (<md)
- **Acceptance:** Layout responsive across breakpoints
- **References:** Requirement 2

#### Task 7.2: Create HealthWidget Component
- Fetch repository health via useRepository hook
- Display status, health message, score
- Show skeleton while loading
- Support error state with retry
- **Acceptance:** Widget renders health status correctly, handles errors
- **References:** Requirement 2

#### Task 7.3: Create CapabilityInventoryWidget Component
- Fetch capability breakdown via useCapabilityBreakdown hook
- Display total count and top 5 categories
- Include "View All" link to /capabilities
- **Acceptance:** Widget shows categories and counts correctly

#### Task 7.4: Create DependencyGraphWidget Component
- Fetch top 5 at-risk dependencies via useDependencies hook
- Display dependency name, severity badge, reason
- Show links to dependencies (placeholder for Stage 2)
- **Acceptance:** Widget displays top 5 dependencies with severity badges

#### Task 7.5: Create RecentChangesWidget Component
- Fetch last 10 capability changes via useRecentChanges hook
- Display timestamp (formatted), change type, capability name
- Clickable to navigate to capability detail
- **Acceptance:** Widget shows recent changes, clickable

---

### Phase 8: Capability Explorer (8 Tasks)
**Estimated Duration:** 8-10 hours | **Complexity:** High

#### Task 8.1: Create ExplorerLayout (Split-View Container)
- Two-panel split view: Navigator (left ~40%) + DetailPanel (right ~60%)
- Independent scrolling for each panel
- Resizable divider (future enhancement)
- **Acceptance:** Split view renders, both panels scroll independently
- **References:** Design Spec Part 3.2, Requirement 3

#### Task 8.2: Create Navigator Component (Left Panel)
- Search input with fuzzy filtering (<150ms)
- Filter panel: category, risk level, dependency count, recency
- Capability tree with virtualization (>50 items)
- Display applied filter count
- **Acceptance:** Search/filter works <150ms, tree virtualizes >50 items
- **References:** Design Spec Part 3.2, Requirement 3

#### Task 8.3: Create FilterPanel Component
- Multi-select filters: category, riskLevel, dependencyCount, recency
- Display active filter count
- "Clear all filters" button
- Sync filters to URL query params
- **Acceptance:** Filters apply, URL updates, clear works
- **References:** Requirement 3

#### Task 8.4: Create CapabilityTreeItem Component
- Hierarchical tree item with disclosure triangle (if children)
- Show name, category, risk badge
- Selected state (highlighted)
- Expand/collapse children with persistence per session
- **Acceptance:** Tree navigation works, selection highlights, expands/collapses
- **References:** Design Spec Part 8.1, Requirement 3

#### Task 8.5: Create DetailPanel Component (Right Panel)
- Tab bar: Structural, Semantic, Behavior, Concept, Capability, Architecture, Decision
- Active tab tracked in Zustand
- Tab content lazy-loaded
- Empty state if no capability selected
- **Acceptance:** Tab switching works, content loads
- **References:** Design Spec Part 3.2, Requirement 4

#### Task 8.6: Create CapabilityTab (Overview)
- Display: name, description, category, risk score, dependency count, last modified
- Show related concepts/entities as expandable cards
- **Acceptance:** Tab renders capability overview correctly
- **References:** Design Spec Part 8.2, Requirement 4

#### Task 8.7: Create Semantic Layer Tabs (Structural, Semantic, Behavior, Concept, Architecture, Decision)
- Each tab displays semantic layer data as received from API
- Fallback: "No [Tab Name] data available" if empty
- Support pagination (>50 items)
- Use lazy loading (@dynamic import)
- **Acceptance:** All tabs render, pagination works, placeholders display
- **References:** Design Spec Part 8.2, Requirement 4

#### Task 8.8: Implement Tab Prefetching & Performance
- Prefetch adjacent tabs on tab bar hover
- Use dynamic imports to code-split tab components
- Support <100ms tab switching for cached data
- **Acceptance:** Tab switching feels instant, prefetch reduces load times
- **References:** Design Spec Part 5, Requirement 9

---

### Phase 9: Search & Command Palette (4 Tasks)
**Estimated Duration:** 3-4 hours | **Complexity:** Medium

#### Task 9.1: Create SearchModal Component
- Modal triggered by global search button or Cmd+K
- Input field with fuzzy search
- Shows recent searches when empty
- Displays search results grouped by type
- **Acceptance:** Modal opens/closes, search triggers, results display
- **References:** Design Spec Part 8.3, Requirement 5

#### Task 9.2: Create SearchResults Component
- Display Capabilities, Concepts, Entities grouped
- Max 5 per group with "View more" link
- Highlight matching query text in bold
- Click to navigate to selected entity
- **Acceptance:** Results grouped, highlighting works, clicking navigates
- **References:** Design Spec Part 8.3, Requirement 5

#### Task 9.3: Create CommandPalette Component
- Modal triggered by Ctrl+K
- Input field with fuzzy filtering
- Display all commands prioritized: recent/frequent first, then others alphabetically
- Keyboard navigation (↑/↓, Enter, Escape)
- **Acceptance:** Palette opens, keyboard nav works, commands execute
- **References:** Design Spec Part 8.3, Requirement 6

#### Task 9.4: Create CommandList Component
- List of available commands (Go to Dashboard, Go to Capabilities, Refresh Data, etc.)
- Track execution count in store
- Execute commands and close palette
- **Acceptance:** Commands execute, execution count increments
- **References:** Requirement 6

---

### Phase 10: Error Handling & Resilience (4 Tasks)
**Estimated Duration:** 2-3 hours | **Complexity:** Low-Medium

#### Task 10.1: Create Global ErrorBoundary
- Wrap entire app at root layout
- Catch and display errors with recovery UI
- Show error details in development
- **Acceptance:** App doesn't white-screen, recovery works
- **References:** Design Spec Part 11.1

#### Task 10.2: Create Error Pages (404, error.tsx)
- Custom 404 page with navigation suggestions
- Global error.tsx page with retry button
- **Acceptance:** 404 pages display, error pages show suggestions
- **References:** Requirement 14

#### Task 10.3: Implement API Timeout Handling
- 10-second timeout on API requests
- Display timeout error message with manual retry
- **Acceptance:** Requests timeout after 10s, user can retry
- **References:** Design Spec Part 11.2, Requirement 14

#### Task 10.4: Create Network Resilience Layer
- Detect offline state (navigator.onLine)
- Detect slow connection (2G/3G)
- Display appropriate banners
- Disable animations on slow connections
- **Acceptance:** Banners appear offline/slow, animations disable
- **References:** Design Spec Part 11.3, Requirement 9

---

### Phase 11: Performance Optimization (5 Tasks)
**Estimated Duration:** 3-4 hours | **Complexity:** Medium

#### Task 11.1: Implement Code Splitting & Lazy Loading
- Dynamic imports for routes: /dashboard, /capabilities, /settings
- Lazy load modals: SearchModal, CommandPalette
- Lazy load tab components in DetailPanel
- **Acceptance:** Code chunks separate in build, fast initial load
- **References:** Design Spec Part 10

#### Task 11.2: Implement Memoization Strategy
- React.memo on list item components (CapabilityTreeItem)
- useMemo for expensive computations (filtered lists)
- useCallback for event handlers passed to memoized children
- **Acceptance:** Component re-renders optimized, no unnecessary renders
- **References:** Design Spec Part 10.2

#### Task 11.3: Implement Virtualization (react-window)
- Virtualize capability navigator lists when >50 items
- Virtualize search results, concept lists
- Maintain 55 FPS during scrolling
- **Acceptance:** Large lists scroll smoothly, FPS stays ≥55
- **References:** Design Spec Part 10.3, Requirement 9

#### Task 11.4: Configure Next.js Bundle Analysis
- Add bundle analyzer to detect chunk sizes
- Monitor total bundle <500 KB gzipped
- Identify and optimize large dependencies
- **Acceptance:** Bundle analysis runs, shows chunk breakdown
- **References:** Design Spec Part 10.4

#### Task 11.5: Implement Image & Asset Lazy Loading
- Use next/image for lazy image loading
- Lazy load non-critical scripts
- Defer CSS for non-critical styles
- **Acceptance:** Images load on scroll, non-critical assets deferred
- **References:** Design Spec Part 10.5

---

### Phase 12: Accessibility & WCAG AA (4 Tasks)
**Estimated Duration:** 3-4 hours | **Complexity:** Medium

#### Task 12.1: Implement Keyboard Navigation
- Tab order correct across all components
- Escape closes modals
- Arrow keys navigate lists and trees
- Enter selects items
- **Acceptance:** Full keyboard navigation works, no traps
- **References:** Design Spec Part 13.2, Requirement 10

#### Task 12.2: Add ARIA Labels & Roles
- All buttons have aria-label
- Modals have role="dialog" and aria-modal="true"
- Tree items have role="treeitem", aria-expanded
- Tab panels have role="tabpanel"
- **Acceptance:** Screen reader test confirms labels and roles
- **References:** Design Spec Part 13.1, Requirement 10

#### Task 12.3: Verify Color Contrast
- Text on background: 4.5:1 minimum
- UI components on background: 3:1 minimum
- Test with contrast checker tool
- **Acceptance:** All colors meet WCAG AA thresholds
- **References:** Design Spec Part 13.5, Requirement 10

#### Task 12.4: Implement Focus Management & Indicators
- Focus indicators visible (2px minimum)
- Focus trap in modals
- Focus restoration on modal close
- Skip-to-main-content link present
- **Acceptance:** Focus visible, traps work, skip link functional
- **References:** Design Spec Part 13.2, Requirement 10

---

### Phase 13: Testing Setup (3 Tasks)
**Estimated Duration:** 2-3 hours | **Complexity:** Low

#### Task 13.1: Configure Vitest or Jest
- Install test runner and utilities
- Configure jsdom environment
- Set up test utilities (@testing-library/react)
- **Acceptance:** `npm run test` runs without errors

#### Task 13.2: Create Test Utilities & Setup Files
- Test setup: mocked API client, QueryClient, Zustand stores
- Render utilities for components
- Mock fixtures for capabilities, concepts
- **Acceptance:** Tests can import from test utilities

#### Task 13.3: Write Example Tests
- Test useCapabilities hook with mocked data
- Test API error handling (retry, timeout)
- Test Zustand store persistence
- **Acceptance:** Example tests pass

---

### Phase 14: Documentation & Deployment (3 Tasks)
**Estimated Duration:** 2 hours | **Complexity:** Low

#### Task 14.1: Create README with Setup Instructions
- Clone, install, run instructions
- Environment variables (.env.local template)
- Backend setup (uvicorn command)
- **Acceptance:** New developer can setup in 10 minutes

#### Task 14.2: Document Component Library & Usage Patterns
- Component prop documentation
- Usage examples for common patterns
- Design system token reference
- **Acceptance:** Developers understand how to use components

#### Task 14.3: Create Next.js Build Optimization Config
- Configure next.config.ts for production
- Enable SWC minification
- Set up image optimization
- Security headers
- **Acceptance:** `npm run build` creates optimized bundle

---

## Task Dependency Graph

```
Phase 1 (Bootstrap & Design System)
    ↓
Phase 2 (API Integration)
    ├→ Phase 3 (Zustand Stores)
    ├→ Phase 4 (Custom Hooks)
    └→ Phase 5 (UI Components)
           ↓
Phase 6 (Layout Components)
    ├→ Phase 7 (Dashboard Page)
    ├→ Phase 8 (Explorer)
    ├→ Phase 9 (Search & Command Palette)
    └→ Phase 10 (Error Handling)
           ↓
Phase 11 (Performance)
    ↓
Phase 12 (Accessibility)
    ↓
Phase 13 (Testing)
    ↓
Phase 14 (Documentation)
```

---

## Execution Roadmap

1. **Start with Phase 1:** All subsequent phases depend on design tokens and project structure
2. **Parallel execution:** Phases 3-5 can run concurrently after Phase 2 completes
3. **Component-first:** Build reusable components before pages
4. **Testing throughout:** Don't wait for Phase 13; write tests as you implement
5. **Performance optimization:** Virtualization and code splitting should be considered during component development, not added later

---

## Success Criteria

- ✅ All 60+ tasks completed with acceptance criteria met
- ✅ <3s Dashboard load time (4G, Lighthouse measured)
- ✅ <2s LCP on Explorer page
- ✅ <500KB gzipped bundle size
- ✅ ≥55 FPS scrolling on lists with 1000+ items
- ✅ WCAG AA compliance (keyboard nav, screen reader, color contrast)
- ✅ All TypeScript types strict, no any/unknown
- ✅ Zero runtime errors (error boundaries catch and recover)
- ✅ Production-ready code quality (comprehensive comments, consistent patterns)

---

## Next Steps

### Stage 1: Complete ✅
All tasks executed successfully. Production deployment ready.

### Stage 2: Architecture Studio - Begin Planning
1. Create detailed Stage 2 requirements document
2. Design React Flow + ELK.js architecture
3. Plan API endpoints for graph data
4. Break down 20-25 implementation tasks
5. Define integration points with Stage 1

---

---

# STAGE 2: Architecture Studio Implementation Plan

## Overview

Stage 2 adds interactive graph visualization capabilities using React Flow and ELK.js for architecture exploration, dependency mapping, and pattern detection.

**Status:** 📋 Planning  
**Estimated Duration:** 12-17 days (20-25 tasks)  
**Complexity:** High  
**Integration:** Non-breaking extension of Stage 1

---

## Phase Breakdown - Stage 2

### Phase 2.1: Graph Infrastructure Setup (4-5 Tasks)
**Estimated Duration:** 2-3 days | **Complexity:** High

#### Task 2.1.1: Install Graph Dependencies
- Install: reactflow (^11.10.0), @elkjs/elk (^0.9.0), d3-force (^3.0.0), @visx/visx (^3.10.0)
- Verify compatibility with Next.js 16/Turbopack
- Update package.json with locked versions
- **Acceptance:** All packages install without peer dependency conflicts, build succeeds

#### Task 2.1.2: Create Architecture Store (Zustand)
- Create stores/architecture-store.ts
- State: selectedNodeIds, layoutMode (hierarchical/force/radial), graphFilters, viewportState
- Actions: selectNode, setLayoutMode, updateFilters, resetGraph
- Enable persist middleware for layoutMode and filters
- **Acceptance:** Store initializes, state persists across refreshes, no hydration issues

#### Task 2.1.3: Implement useArchitectureGraph Hook
- Create hooks/useArchitectureGraph.ts wrapping TanStack Query
- Fetch GET /api/v1/architecture/graph with filters (capabilityIds, depth, includePatterns)
- Cache time: 5 minutes, refetchOnWindowFocus: 'stale'
- Return typed graph data: { nodes: Node[], edges: Edge[], patterns: Pattern[] }
- **Acceptance:** Hook fetches graph data, caches correctly, type-safe

#### Task 2.1.4: Create React Flow Base Canvas Component
- Create features/architecture/ArchitectureCanvas.tsx
- Set up ReactFlow with background, controls (zoom, fit view, minimap)
- Configure node/edge types
- Handle viewport changes and persist to store
- **Acceptance:** Canvas renders, pan/zoom works, controls functional

#### Task 2.1.5: Integrate ELK.js Layout Engine
- Create lib/graph-layout.ts with ELK worker setup
- Implement layout algorithms: hierarchical (layered), force-directed, radial
- Support configurable spacing, direction (TB/LR/BT/RL)
- Handle layout calculation in Web Worker to prevent blocking
- **Acceptance:** Layouts calculate <2s for 500 nodes, UI stays responsive

---

### Phase 2.2: Architecture Graph Components (5-6 Tasks)
**Estimated Duration:** 3-4 days | **Complexity:** High

#### Task 2.2.1: Create Custom Node Components
- CapabilityNode.tsx: displays capability name, type badge, risk indicator, mini metrics
- EntityNode.tsx: displays entity name, type, file path tooltip
- ConceptNode.tsx: displays concept name, semantic layer badge
- Support selection state, hover effects, color coding by type
- **Acceptance:** Nodes render with correct data, selection highlights, accessible

#### Task 2.2.2: Create Custom Edge Components
- DependencyEdge.tsx: arrow edge with dependency type label
- RelationshipEdge.tsx: bidirectional edge for non-directional relationships
- Support edge weight visualization (thickness)
- Color coding by relationship type (uses/implements/extends)
- **Acceptance:** Edges render correctly, labels visible, animations smooth

#### Task 2.2.3: Implement Node Clustering Algorithm
- Create lib/graph-clustering.ts
- Cluster nodes by: architecture pattern, capability category, risk level
- Visual clusters: subtle background rectangles, labeled groups
- Support expand/collapse clusters
- **Acceptance:** Clustering groups related nodes, collapse/expand works

#### Task 2.2.4: Add Graph Controls & Minimap
- Integrate React Flow Controls component (zoom in/out, fit view, lock)
- Add MiniMap component with node color coding
- Custom toolbar: layout selector dropdown, filter panel toggle, export button
- Keyboard shortcuts: Ctrl+0 (fit view), Ctrl++ (zoom in), Ctrl+- (zoom out)
- **Acceptance:** All controls functional, keyboard shortcuts work

#### Task 2.2.5: Implement Node Selection & Multi-Select
- Single-click: select node, update Zustand store, show detail panel
- Ctrl+click: add to selection (multi-select)
- Shift+click: range select (shortest path between two nodes)
- Keyboard: arrow keys navigate, Space selects, Escape deselects all
- **Acceptance:** Selection modes work, keyboard navigation functional

#### Task 2.2.6: Add Node Context Menu
- Right-click on node: show context menu
- Menu items: View Details, Expand Dependencies, Focus (hide unrelated), Copy ID, Export Subgraph
- Handle menu actions with Zustand store updates
- **Acceptance:** Context menu appears, all actions execute correctly

---

### Phase 2.3: Dependency Visualization (4-5 Tasks)
**Estimated Duration:** 2-3 days | **Complexity:** Medium-High

#### Task 2.3.1: Implement Blast Radius Calculation & Visualization
- Create lib/blast-radius.ts
- Calculate downstream impact depth from selected node
- Visualize as concentric rings or color gradient (depth 1-5+)
- Show affected capability count in overlay
- **Acceptance:** Blast radius calculates correctly, visualization clear

#### Task 2.3.2: Create Circular Dependency Detector
- Implement cycle detection algorithm (DFS-based)
- Highlight circular dependencies with red dashed edges
- Show warning badge on nodes involved in cycles
- Panel listing all detected cycles with severity scores
- **Acceptance:** Cycles detected accurately, highlights visible

#### Task 2.3.3: Build Dependency Depth Visualization
- Color-code nodes by dependency depth (0=root, 1-5+ layers)
- Create legend showing depth color mapping
- Support filtering by depth range
- **Acceptance:** Depth coloring accurate, legend clear, filter works

#### Task 2.3.4: Add Impact Analysis Panel
- Sidebar showing details of selected node's impact
- List affected capabilities (downstream)
- List dependencies (upstream)
- Show metrics: dependency count, dependents count, blast radius score
- **Acceptance:** Panel displays accurate impact data, updates on selection

#### Task 2.3.5: Implement Bidirectional Relationship Tracing
- Highlight path between two selected nodes (shortest path algorithm)
- Show both upstream and downstream connections simultaneously
- Support "Show all paths" mode (display top 5 paths)
- **Acceptance:** Path highlighting accurate, multiple paths display correctly

---

### Phase 2.4: Pattern Detection UI (3-4 Tasks)
**Estimated Duration:** 2-3 days | **Complexity:** Medium

#### Task 2.4.1: Create Pattern Detection Card Component
- ArchitecturePatternCard.tsx: displays detected pattern (layered, microservices, event-driven)
- Show pattern confidence score, description, affected components
- Click to highlight pattern nodes in graph
- **Acceptance:** Cards render detected patterns, clicking highlights nodes

#### Task 2.4.2: Implement Anti-Pattern Highlight System
- Detect anti-patterns: god objects (high in-degree), cyclic dependencies, tight coupling
- Visual indicators: red border on nodes, warning badge, tooltip explanation
- Anti-pattern severity score (low/medium/high/critical)
- **Acceptance:** Anti-patterns detected, highlights visible, severity accurate

#### Task 2.4.3: Add Boundary Visualization Overlay
- Visualize architectural layers (presentation, business, data, infrastructure)
- Semi-transparent rectangles grouping nodes by layer
- Support toggle on/off
- **Acceptance:** Boundaries display correctly, toggle works, layers clear

#### Task 2.4.4: Create Pattern Metrics Dashboard Widget
- Widget showing: pattern count, anti-pattern count, boundary adherence score
- Mini bar chart of pattern distribution
- Clickable to navigate to Architecture Studio
- **Acceptance:** Widget displays metrics, clickable navigation works

---

### Phase 2.5: Integration & Optimization (4-5 Tasks)
**Estimated Duration:** 3-4 days | **Complexity:** Medium-High

#### Task 2.5.1: Link Dashboard Dependency Widgets to Architecture Studio
- Update DependencyOverviewWidget with "View Graph" button
- Pass selected capability IDs as query params to /architecture
- Graph opens with focus on selected nodes
- **Acceptance:** Navigation works, graph focuses on correct nodes

#### Task 2.5.2: Add "View in Graph" Button to Capability Detail Panel
- Add button to CapabilityTab (Stage 1 component)
- Click navigates to /architecture with selected capability focused
- Syncs selection state with Architecture Store
- **Acceptance:** Button appears, navigation works, state syncs

#### Task 2.5.3: Synchronize Selection State Between Navigator and Graph
- Selecting node in graph → updates Capability Navigator selection
- Selecting capability in Navigator → highlights node in graph
- Bidirectional sync using Zustand store
- **Acceptance:** Two-way sync works, no infinite loops

#### Task 2.5.4: Optimize Graph Rendering Performance
- Implement node virtualization for 1000+ nodes (only render visible viewport)
- Throttle layout recalculations (debounce 300ms)
- Use React.memo on node/edge components
- Profile with Chrome DevTools, target ≥30 FPS
- **Acceptance:** Graph with 1000 nodes maintains ≥30 FPS, smooth interactions

#### Task 2.5.5: Add Graph Export Functionality
- Export as PNG (high-res screenshot)
- Export as SVG (vector graphics)
- Export as JSON (graph data structure)
- Export button in toolbar with format selector
- **Acceptance:** All export formats work, files downloadable

---

## Task Dependency Graph - Stage 2

```
Phase 2.1 (Graph Infrastructure)
    ↓
Phase 2.2 (Graph Components)
    ├→ Phase 2.3 (Dependency Visualization)
    └→ Phase 2.4 (Pattern Detection UI)
           ↓
Phase 2.5 (Integration & Optimization)
```

---

## Execution Roadmap - Stage 2

1. **Start with Phase 2.1:** Set up infrastructure (React Flow, ELK.js, stores, hooks)
2. **Phase 2.2:** Build graph components (nodes, edges, controls) - can overlap with 2.1
3. **Parallel execution:** Phases 2.3 and 2.4 can run concurrently after 2.2
4. **Final integration (Phase 2.5):** Link with Stage 1, optimize performance
5. **Testing throughout:** Test graph interactions, performance, accessibility

---

## Success Criteria - Stage 2

- ✅ Graph renders 1000+ nodes smoothly (≥30 FPS)
- ✅ Layout calculation <2s for 500 nodes
- ✅ Selection syncs between Navigator and Graph
- ✅ All patterns/anti-patterns detected correctly
- ✅ Blast radius calculations accurate
- ✅ Circular dependencies detected
- ✅ Graph state persists across navigation
- ✅ WCAG AA compliance maintained
- ✅ No performance regression in Stage 1 features
- ✅ Export functionality works (PNG/SVG/JSON)

---

## Integration Checkpoints with Stage 1

1. **Architecture Store** integrates with existing Zustand stores (no conflicts)
2. **Graph hooks** follow same TanStack Query patterns as Stage 1
3. **Component reuse:** Badge, Card, MetricCard, EmptyState from Stage 1
4. **Routing:** `/architecture` added without modifying Stage 1 routes
5. **Navigation:** Sidebar link to Architecture Studio activated
6. **Cross-linking:** Dashboard widgets and Capability Detail link to graph
7. **Type system:** Extend existing types in `types/domain.ts` and `types/api.ts`

---

## API Endpoints Required - Stage 2

### New Backend Endpoints

1. **GET /api/v1/architecture/graph**
   - Query params: capabilityIds[], depth (1-5), includePatterns (boolean)
   - Returns: { nodes: Node[], edges: Edge[], patterns: Pattern[] }

2. **GET /api/v1/dependencies/tree**
   - Query params: capabilityId, direction (upstream/downstream/both)
   - Returns: Tree structure with dependency relationships

3. **GET /api/v1/patterns/detect**
   - Query params: repositoryId
   - Returns: { patterns: Pattern[], antiPatterns: AntiPattern[], metrics: Metrics }

4. **POST /api/v1/architecture/subgraph**
   - Body: { nodeIds: string[], depth: number }
   - Returns: Filtered subgraph for selected nodes

---

## Stage 2 Next Steps

1. **Finalize Stage 2 requirements document**
   - Write 15-20 detailed requirements for graph features
   - Define acceptance criteria for each requirement
   - Map requirements to design sections

2. **Create Stage 2 design document**
   - React Flow component architecture
   - ELK.js layout configuration
   - Graph state management patterns
   - Performance optimization strategies
   - API response type definitions

3. **Break down tasks with acceptance criteria**
   - Detail all 20-25 tasks
   - Define clear acceptance criteria
   - Estimate task durations
   - Identify task dependencies

4. **Update testing strategy**
   - Graph interaction testing (selection, zoom, pan)
   - Layout algorithm testing
   - Performance testing (1000+ nodes)
   - Integration testing with Stage 1

---

**Stage 1:** ✅ COMPLETE (60+ tasks, production-ready)  
**Stage 2:** 📋 PLANNING (20-25 tasks estimated, 12-17 days)  
**Next:** Create detailed Stage 2 specification documents (requirements.md, design.md)
