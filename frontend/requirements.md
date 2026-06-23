# Requirements Document

## Introduction

The Software Intelligence Platform (SIP) is a production-grade frontend for exploring software capabilities, architecture, and reasoning across large codebases. Stage 1 establishes the foundational UI layer for discovering and analyzing software capabilities as the primary abstraction.

The platform aggregates semantic intelligence from a FastAPI backend exposing 7 semantic layers: Structural, Semantic, Behavior, Concept, Capability, Architecture, and Decision. This document specifies Stage 1 requirements covering the design system, repository dashboard, capability intelligence explorer, global search, and command palette.

Key constraints: the frontend must support 1000+ capabilities and 10000+ concepts without performance degradation. The architecture must remain extensible for Stages 2–4 without refactoring. All components must follow enterprise minimal design principles with a dark-first theme.

## Glossary

- **Capability**: A distinct, composable unit of software functionality. The primary abstraction representing what the system can do. Capabilities have metadata (description, category, dependencies, risk level) and relationships to other capabilities.
- **Concept**: A domain-level abstraction extracted from the codebase representing key ideas (e.g., "rate limiting", "user authentication", "caching strategy").
- **Entity**: A low-level code artifact (class, function, module, file) that participates in semantic layers.
- **Semantic Layer**: One of seven layers providing different perspectives on software: Structural (code organization), Semantic (meaning), Behavior (runtime patterns), Concept (domain abstractions), Capability (functional units), Architecture (system design), Decision (tech choices), Reasoning (inference and justification).
- **Repository**: A single codebase or project being analyzed.
- **Dashboard**: The Repository Command Center providing executive overview of health, capabilities, dependencies, and recent changes.
- **Explorer**: The Capability Intelligence Explorer providing split-view navigation and deep analysis of capabilities and related entities.
- **Command_Palette**: Global command launcher for quick navigation and actions (Ctrl+K trigger).
- **Search_Engine**: Global fuzzy search with grouping by entity type and recent searches.
- **UI_System**: Shared design system, components, and tokens (typography, spacing, colors, motion).
- **API_Client**: Typed TypeScript client for FastAPI backend endpoints.
- **State_Store**: Client-side state management using Zustand for UI state, selections, and filters.
- **Query_Cache**: Server state management using TanStack Query for API data caching and synchronization.


## Requirements

### Requirement 1: Design System Implementation

**User Story:** As a developer, I want a consistent, production-grade design system, so that the platform maintains enterprise visual standards and scales to support 1000+ capabilities.

#### Acceptance Criteria

1. THE Design_System SHALL define a complete dark theme with base color #090B10 for background, #111318 for surface, and a 10-tier neutral gray scale (gray-50 #F9FAFB through gray-900 #111318).
2. THE Typography_System SHALL provide scaling tokens with explicit font-weights (400–700) and line-heights (1.2–1.6) for: H1 (32px, 700, 1.2), H2 (28px, 700, 1.25), H3 (24px, 700, 1.3), H4 (20px, 600, 1.35), H5 (16px, 600, 1.4), H6 (14px, 600, 1.4), Body (14px, 400, 1.5), Caption (12px, 400, 1.4), Code (13px monospace, 500, 1.6).
3. THE Spacing_System SHALL define a consistent 8px-based scale: xs (4px), sm (8px), md (12px), lg (16px), xl (24px), 2xl (32px), 3xl (48px), 4xl (64px).
4. WHEN a user navigates between pages, THE Motion_System SHALL apply a fade transition (opacity 0→1, 200ms, ease-out).
5. WHEN a component enters the viewport, THE Motion_System SHALL apply a slide-up transition (translateY +20px→0, 300ms, ease-out).
6. WHEN a modal or overlay opens, THE Motion_System SHALL apply a scale transition (scale 0.95→1, 200ms, ease-out).
7. WHERE shadcn/ui components are used, THE UI_System SHALL provide a Tailwind configuration that preserves shadcn/ui defaults by using distinct key names that do not shadow built-in values.
8. THE Design_System SHALL expose all tokens as: (a) CSS variables following format var(--{category}-{name}) (e.g., var(--color-primary), var(--spacing-lg)), (b) a flat TypeScript object exported from src/styles/tokens.ts with hierarchical key names (e.g., colors.primary, spacing.lg), and (c) TailwindCSS theme extensions that map to CSS variables.
9. THE Design_System SHALL support future theme extensions (Stages 2–4) by centralizing all token definitions in a single src/styles/tokens.ts module without requiring changes to component files.


### Requirement 2: Repository Command Center Dashboard

**User Story:** As a platform user, I want an executive dashboard, so that I can quickly assess repository health, capability inventory, dependency risks, and recent changes.

#### Acceptance Criteria

1. THE Dashboard SHALL display at minimum four primary widgets: Health Overview, Capability Inventory, Dependency Graph Summary, and Recent Changes.
2. WHEN the Dashboard loads, THE API_Client SHALL fetch the following required metrics within 2 seconds and render the full view by 3 seconds (including TanStack Query caching and hydration): (a) repository health status (healthy/warning/critical), (b) total capability count and breakdown by category (top 5), (c) top 5 at-risk dependencies ranked by severity score (highest first), (d) last 10 capability changes with timestamp and change type.
3. THE Health_Widget SHALL display repository status (healthy, warning, critical) with color-coded indicator and an explanation text limited to max 100 characters.
4. THE Capability_Widget SHALL show total capability count, breakdown by category (displaying top 5 categories), and a "View All" link to the Capability Explorer.
5. THE Dependency_Widget SHALL render a summary of the top 5 at-risk dependencies (ranked by severity score, highest first) with severity badges and links to each dependency (future Stage 2 deep analysis feature, disabled in Stage 1 but present in navigation).
6. THE Recent_Changes_Widget SHALL list the last 10 capability updates with: timestamp (ISO 8601 format), change type (added/modified/removed), and affected capability name.
7. WHILE a widget is loading, THE Dashboard SHALL display a skeleton loader matching the widget's final layout dimensions to prevent cumulative layout shift.
8. IF a widget fails to load due to (a) network error, (b) timeout (>5 seconds), or (c) invalid API response format, THE Error_Boundary SHALL display a recoverable error message (max 100 chars) and a "Retry" button; previously loaded data SHALL persist on screen if available.
9. THE Dashboard_Responsive_Behavior SHALL be: on screens 1024px and wider, display 2-column grid (Health + Inventory left, Dependencies + Changes right); on screens 768px–1023px, display single column with priority order (Health → Inventory → Changes → Dependencies); on screens <768px, stack all widgets vertically.


### Requirement 3: Capability Intelligence Explorer - Navigator Panel

**User Story:** As a developer, I want to navigate and filter capabilities by multiple dimensions, so that I can find relevant capabilities in a repository with 1000+ capabilities.

#### Acceptance Criteria

1. THE Explorer_Navigator SHALL display a hierarchical tree of capabilities grouped by category (or an "Uncategorized" group for capabilities without category) and searchable by name, description, and metadata fields (category, risk level, owner).
2. WHEN the user types in the Navigator search field, THE Navigator SHALL filter visible capabilities using fuzzy matching (up to 2 character substitutions or omissions allowed) and update results within 150ms of the last keystroke.
3. THE Navigator SHALL support multi-select capability filtering (AND logic—all selected filters must match) by: (a) category, (b) risk level (low/medium/high/critical), (c) dependency count (ranges: 0, 1–5, 6–20, 20+), (d) update recency (today, this week, this month, older). THE Navigator SHALL display the number of currently applied filters in the filter panel.
4. WHEN a filter is applied or removed, THE Navigator SHALL update the browser URL query parameters (e.g., ?category=auth&risk=high) and preserve these settings for shareability and bookmarking.
5. THE Navigator SHALL render up to 50 capabilities per viewport without virtualization; when more than 50 visible items remain after filtering, THE Navigator SHALL implement row virtualization (e.g., react-window) rendering only visible rows in the viewport. Target scrolling performance: average frame rate ≥55 FPS during continuous 2-second scroll tests.
6. WHEN a capability is selected in the Navigator, THE Detail_Panel SHALL update within 300ms to load and display capability details without a full page reload; the update scope includes loading the capability's semantic metadata and rendering the selected tab.
7. WHERE a capability has child capabilities or child components, THE Navigator SHALL display a disclosure triangle (►/▼) allowing expand/collapse of the hierarchy; expanded state SHALL persist per session.
8. IF no capabilities match the current filters, THE Navigator SHALL display a distinct empty state with: (a) the message "No capabilities match your filters", (b) up to 3 suggested alternative filters to clear, and (c) a "Clear all filters" button.


### Requirement 4: Capability Intelligence Explorer - Detail Panel with 7 Tabs

**User Story:** As a developer, I want deep analysis of a capability across seven semantic layers, so that I understand its implementation, dependencies, risks, and design decisions.

#### Acceptance Criteria

1. THE Detail_Panel SHALL display seven tabs corresponding to semantic layers: Structural, Semantic, Behavior, Concept, Capability (overview), Architecture, and Decision.
2. WHEN a capability is selected, THE Detail_Panel SHALL load and display the Capability (overview) tab first, showing: name, full description, category, risk assessment (score + rationale), dependency count, last modified date (ISO 8601), and linked concepts/entities as expandable cards.
3. THE Structural_Tab SHALL render a visual code tree showing files, classes, functions, and modules that implement the capability with click-to-navigate links (stage 2+) to source code locations.
4. THE Semantic_Tab SHALL display semantic annotations, type information, and extracted domain concepts associated with the capability, with bidirectional links to related concepts.
5. THE Behavior_Tab SHALL show runtime patterns, call graphs, and state transitions for the capability as either diagrams (stage 2+) or text descriptions (stage 1).
6. THE Concept_Tab SHALL list domain-level abstractions and related concepts linked to the capability with description text and relationship types (e.g., "implements", "uses", "extends").
7. THE Capability_Tab SHALL provide an overview including all fields listed in criterion 2 (name, description, category, risk, stats, links).
8. THE Architecture_Tab SHALL display architectural role, integration points, and relationships to other architectural components; in Stage 1, show text descriptions and links (placeholder for Stage 2 deep analysis).
9. THE Decision_Tab SHALL list technology and design decisions associated with the capability with rationale, alternatives considered, and approval status; in Stage 1, show as list items (placeholder for Stage 2 reasoning explorer).
10. WHEN switching between tabs, THE Detail_Panel SHALL display tab content within 100ms for pre-fetched data or show a spinner for on-demand fetches (>100ms expected load time).
11. WHERE a tab contains more than 50 items (e.g., 50+ related concepts), THE Tab_View SHALL implement pagination (max 25 items per page) or row virtualization to maintain performance.
12. IF a tab has no data available for the current capability, THE Tab_View SHALL display a placeholder message: "No [tab name] data available" with an optional "Learn more" link to documentation.
13. THE Detail_Panel SHALL have its own scrollbar independent from the Navigator, allowing independent scrolling of both panel and navigation tree in split-view layout.


### Requirement 5: Global Search Interface

**User Story:** As a platform user, I want fast, intelligent search across capabilities, concepts, and entities, so that I can find relevant code knowledge without navigating menus.

#### Acceptance Criteria

1. THE Search_Engine SHALL support fuzzy matching on capability names, descriptions, concepts, and entity names (up to 2 character substitutions or omissions allowed).
2. WHEN a search query is entered, THE Search_Engine SHALL return results within 200ms, grouped by entity type: Capabilities (up to 5 results), Concepts (up to 5 results), Entities (up to 5 results).
3. WITHIN each result group, THE Results SHALL be ranked by relevance score (highest first), then alphabetically; results SHALL display intra-group rank position and provide a "View more [group] results" link.
4. WHERE a user has performed searches previously, THE Search_Interface SHALL display a "Recent Searches" section showing the last 10 unique searches (matched by exact query text) with timestamps and a preview of the first 3 results from each search.
5. WHEN a user clicks a search result, THE Search_Interface SHALL navigate to the selected entity and highlight it in context (e.g., open Capability Explorer, select the capability, scroll to result in Detail Panel).
6. THE Search_Box SHALL be accessible globally, positioned in the top navigation bar and visible on all pages; clicking the search box SHALL open a search modal or dropdown overlay.
7. IF the search query is empty, THE Search_Interface SHALL display: (a) "Recent Searches" section (if history exists) OR (b) "Popular Searches" showing most-viewed searches from the last 30 days OR (c) a blank state with placeholder text.
8. THE Search_Results SHALL highlight matching query terms in bold text for visual clarity.
9. WHERE search results include deprecated or low-priority items (if applicable), THE Search_Engine SHALL rank them last in their respective result group, ordered alphabetically.


### Requirement 6: Command Palette

**User Story:** As a power user, I want a command palette (Ctrl+K), so that I can navigate and execute actions without leaving the keyboard.

#### Acceptance Criteria

1. THE Command_Palette SHALL open when the user presses Ctrl+K (or Cmd+K on macOS); pressing Escape SHALL close the modal; initial focus SHALL be placed on the search input field upon open.
2. WHEN invoked, THE Command_Palette SHALL accept keyboard input and filter available commands in real time using fuzzy matching; results SHALL be displayed within 200 milliseconds.
3. WHEN the palette opens with no input, THE Command_List SHALL display all available commands (navigation commands: "Go to Dashboard", "Go to Capabilities"; action commands: "Refresh Data", "Toggle Sidebar", "Open Settings"; these are refreshed on each palette open).
4. THE Command_Palette SHALL prioritize display order: (a) recently executed commands (within last 7 days, executed >5 times total) displayed first, (b) then frequently used commands (executed >5 times total but not recent), (c) then all other commands alphabetically.
5. WHEN a user selects a command with Enter key, THE Command_Palette SHALL execute the action immediately and close the modal 500ms after command completion.
6. THE Command_Palette SHALL support navigation with arrow keys (↑/↓) to move between commands and Enter to select; the currently highlighted command SHALL have a visible indicator (background color change or border).
7. WHEN the user presses Escape, THE Command_Palette SHALL close without executing any command and focus SHALL return to the previously focused element.
8. WHERE a command shows a description or category, THE Palette_View SHALL display it as secondary text (smaller font, reduced opacity) below or beside the command name.
9. IF a command execution fails, THE Command_Palette SHALL display an error message (max 100 chars) in the modal and remain open for manual retry.
10. THE Command_Palette SHALL remain keyboard-accessible and shall not block screen readers; all commands SHALL have semantic labels and descriptions for assistive technologies (WCAG 2.1 Level AA compliance).


### Requirement 7: Frontend Architecture and Application Structure

**User Story:** As a developer, I want a scalable, maintainable frontend architecture, so that future stages (2–4) can be integrated without refactoring.

#### Acceptance Criteria

1. THE Frontend_App SHALL be structured using Next.js 15 App Router with TypeScript strict mode enabled (noImplicitAny, strictNullChecks, strictFunctionTypes, strictBindCallApply all set to true in tsconfig.json).
2. THE Folder_Structure SHALL follow this clear separation: `/app` (routes), `/components` (UI components), `/features` (feature modules), `/lib` (utilities), `/hooks` (custom hooks), `/types` (TypeScript types), `/stores` (Zustand state), `/api` (API clients and query definitions), `/styles` (global styles and tokens). An audit of all directories SHALL confirm they follow this hierarchy.
3. WHERE a feature is added (Stage 2+), THE Folder_Structure SHALL accommodate it by adding new feature directories in `/features` and new route directories in `/app` WITHOUT moving or modifying existing Stage 1 code.
4. THE Routing_Layer SHALL use Next.js App Router with primary routes: `/` (redirects to `/dashboard`), `/dashboard` (Repository Command Center), `/capabilities` (Capability Explorer), `/settings` (placeholder for future Stage 2+), and reserved (but unimplemented) route paths: `/architecture`, `/decisions`, `/reasoning`, `/time-machine`, `/universe` that return 404 with navigation suggestions until implemented.
5. WHEN the application initializes, THE Boot_Process SHALL: (a) load and parse Design_System tokens from `/styles/tokens.ts`, (b) initialize all Zustand stores (ui-store, search-store, command-palette-store) with default state, (c) configure TanStack Query QueryClient with: 5-minute cache time, 30-second stale time, and automatic retry on mount if data is stale.
6. THE State_Management_Layer SHALL use: (a) Zustand for transient UI state (selected capability ID, filter panel open/close, sidebar collapsed, active tab) using stores in `/stores/`, and (b) TanStack Query (@tanstack/react-query) for server state (API responses, cache management) using hooks and query definitions.
7. THE API_Client_Layer SHALL expose typed TypeScript functions (defined in `/api/endpoints.ts`) for each backend endpoint with: (a) consistent error handling (catch HTTP errors 4xx/5xx and network failures), (b) retry logic: 2 retry attempts with exponential backoff (100ms, then 200ms), (c) request/response logging in development mode.
8. THE Error_Handling_Boundary_Component (global React Error Boundary) SHALL wrap the entire page tree, catching errors and displaying a user-friendly error message (max 100 characters) with details in development mode only.
9. WHERE a component requires data from the API, THE Component SHALL use TanStack Query hooks (custom hooks from `/hooks/`) to manage loading, error, and success states with proper TypeScript types.
10. THE Build_System SHALL use Next.js production build (`next build`) with output directory at `.next`, supporting both SSR and static generation (ISR) where applicable; the build SHALL complete without TypeScript errors.


### Requirement 8: API Integration Layer

**User Story:** As a developer, I want type-safe, predictable API integration, so that I can reliably fetch and cache software intelligence data.

#### Acceptance Criteria

1. THE API_Client SHALL expose typed TypeScript functions mirroring FastAPI endpoints at `http://localhost:8000/api/v1/` with explicit response type definitions matching backend schemas.
2. THE API_Endpoints_Used SHALL include at minimum: `GET /repositories/{id}`, `GET /capabilities` (with pagination: limit, offset params), `GET /capabilities/{id}`, `GET /concepts`, `GET /entities`, and `POST /search` (with query parameter support for fuzzy search).
3. WHEN an API request is made, THE API_Client SHALL handle errors as follows: HTTP 4xx/5xx errors and network failures SHALL trigger automatic retry with exponential backoff (1 second delay, then 2 seconds, then 4 seconds, for 3 total attempts); after 3 failed retries, the error SHALL be returned to the calling component with: error code (e.g., "CAPABILITY_NOT_FOUND"), user-friendly message (max 100 chars), and HTTP status.
4. THE Response_Shapes SHALL match TypeScript interfaces defined in `/types/api.ts` for all endpoints: Capability, Concept, Entity, SearchResult, Repository, PaginatedResponse, ErrorResponse (each with required fields, optional fields marked with `?`).
5. WHERE the backend returns pagination metadata (limit, offset, total), THE Query_Cache SHALL respect these values and load additional pages on demand using TanStack Query's infinite query pattern.
6. IF an API endpoint returns a 401 or 403 error, THE Error_Handler SHALL store the error state (for Stage 2+ auth integration); in Stage 1, a placeholder message SHALL be displayed ("Authentication required—please refresh").
7. THE API_Client_Configuration SHALL assume the frontend runs on `localhost:3000` and backend on `localhost:8000`; CORS headers are already configured on the backend (config.py).
8. THE API_Client SHALL log to console: (a) request start/end timestamps and duration, (b) retry attempts with backoff delays, (c) error details (code, message, status) in development mode; in production, errors are sent to optional telemetry service (stubbed, not implemented in Stage 1).
9. WHEN the Query_Cache detects stale data (>30 seconds old), THE Query_Cache SHALL silently refetch in the background if the application window has focus; the UI SHALL NOT display loading state during background refetch (transparent refetch).


### Requirement 9: Performance and Scalability

**User Story:** As a platform operator, I want the frontend to scale to 1000+ capabilities and 10000+ concepts without performance degradation, so that large repositories remain usable.

#### Acceptance Criteria

1. THE Dashboard SHALL load and display within 3 seconds on a 4G connection (measured via Lighthouse metrics: First Contentful Paint <1s, Largest Contentful Paint <2s, Cumulative Layout Shift <0.1).
2. WHEN the Explorer opens with 1000 capabilities loaded, THE Navigator_View SHALL display initial content without blocking the main thread (First Contentful Paint <1s, Largest Contentful Paint <2s).
3. WHEN a user scrolls through a paginated or virtualized list of 500+ items, THE Navigation_Performance SHALL maintain an average frame rate of ≥55 FPS measured over continuous 2-second scroll tests.
4. WHEN a user applies 1 to 5 simultaneous filter criteria to 1000 capabilities, THE Filter_Engine SHALL update and display filtered results within 150ms of the last filter change.
5. WHEN a user enters a search query, THE Search_Engine SHALL return fuzzy-matched results for 1000 capabilities within 200ms using local filtering (browser-side processing, not server round-trip).
6. WHERE a component renders >50 items, THE Component SHALL implement row virtualization (e.g., react-window) rendering only visible rows in the viewport, with start/end indices visible during scrolling.
7. THE Bundle_Size of the frontend application (JavaScript + CSS) SHALL not exceed 500 KB gzipped (excluding images, fonts, and code split chunks for future stages).
8. WHEN a user navigates between routes, THE Route_Transition SHALL complete within 500ms using code-splitting and lazy loading to minimize blocking time on the main thread.
9. THE API_Caching_Strategy SHALL cache responses for 5 minutes by default; cache invalidation SHALL occur on user actions: (a) applying filters, (b) search queries, (c) manual "Refresh" button click, (d) capability modifications (future Stage 2+).
10. IF the application detects a slow connection (Edge or 2G network types), THE App_Shell SHALL: (a) disable Framer Motion animations (prefers-reduced-motion respected), (b) defer loading of non-critical images, (c) display compressed data summaries instead of full details.


### Requirement 10: Accessibility (WCAG AA Compliance)

**User Story:** As an inclusive platform, I want to meet WCAG AA standards, so that users with disabilities can navigate and interact with all features.

#### Acceptance Criteria

1. THE Application_Markup SHALL use semantic HTML5 elements: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>` where structurally appropriate; screen reader testing with NVDA or JAWS SHALL verify semantic structure is recognized.
2. ALL Interactive_Elements (buttons, links, form inputs) SHALL have appropriate ARIA labels (`aria-label`, `aria-labelledby`) and roles (`role="button"`, `role="tab"`, etc.); a screen reader testing pass SHALL confirm all interactive elements are announced with their purpose.
3. THE Color_Contrast of text and interactive elements against their background in the dark theme SHALL meet WCAG AA minimum: text 4.5:1 ratio, UI components 3:1 ratio; contrast testing tool validation SHALL confirm all text and UI components meet these thresholds.
4. THE Keyboard_Navigation SHALL provide full access to all features using Tab, Shift+Tab (forward/backward navigation), Enter, Space, and arrow keys; a keyboard-only navigation pass SHALL confirm no keyboard traps exist and all functionality is reachable.
5. WHEN focus moves on the page, THE Focus_Indicator SHALL be clearly visible with: min-height of 2px, color contrast ≥3:1 against background, and distinct styling (border or outline); focus indicators SHALL remain visible at all times during keyboard navigation.
6. THE Page_Structure SHALL include a skip-to-main-content link (`<a href="#main-content">Skip to main content</a>`) as the first focusable element on every page; pressing Tab once SHALL focus this link.
7. ALL Form_Inputs (search, filters, dropdowns) SHALL be associated with labels: either via `<label for="id">` or `aria-label="description"`; error messages SHALL be linked to inputs via `aria-describedby="error-id"` so screen readers announce errors together with the input.
8. WHERE complex components (tree views in Navigator, tab panels in Detail, dialogs in Command Palette) are used, THE Component SHALL follow WAI-ARIA authoring practices: `aria-expanded` (for tree), `aria-selected` (for tabs), `aria-current` (for active item), `role="dialog"` (for modals), and `aria-live="polite"` (for dynamic content updates).
9. THE Application_Alerts and dynamic content updates (e.g., search results, error messages) SHALL announce content changes to screen readers using ARIA live regions: `aria-live="polite"` for non-critical updates, `aria-live="assertive"` for critical alerts (e.g., errors); a screen reader session SHALL verify announcements are made.
10. WHERE images or visual-only UI elements are present (icons, charts in Stage 1 or future stages), THE Element SHALL include alt text or `aria-label`; an audit of all img tags and icon components SHALL confirm alt/aria-label attributes are present and descriptive (150-character limit for brevity).
11. THE Application_Scope (in-scope for WCAG AA testing): dashboard, capabilities explorer, search interface, command palette, navigation, error messages; content loaded from backend (capability descriptions, code samples) are not in scope for Stage 1 alt text requirements but should follow best practices in Stage 2+.
12. WHEN testing for accessibility, the application SHALL pass WCAG 2.1 Level AA automated checks (axe DevTools, Lighthouse) with zero violations; manual testing with a screen reader (NVDA on Windows or JAWS) SHALL confirm keyboard navigation and announcements work as designed.


### Requirement 11: Browser Support and Compatibility

**User Story:** As an enterprise platform, I want to support modern browsers, so that users on standard development environments can access the platform.

#### Acceptance Criteria

1. THE Application SHALL support these browsers with no unsupported API calls: Chrome/Chromium 120+, Edge 120+, Firefox 121+, Safari 17+; caniuse.com verification SHALL confirm target features are supported in baseline versions.
2. THE Polyfills_And_Fallbacks for ES2020+ features not natively supported in baseline browsers SHALL include (via Next.js and core-js): Promise, Array methods (flat, flatMap, includes), Object methods (fromEntries), String methods (matchAll, replaceAll), WeakMap, Proxy (if used); an automated dependency audit SHALL verify no unsupported syntax is used.
3. WHEN the user's browser is not supported (older than baseline versions), THE App_Shell SHALL display a non-dismissible banner at the top with message "Your browser is not supported. Please upgrade to [Chrome 120+, Firefox 121+, Safari 17+, Edge 120+]" and a link to browser upgrade pages; the banner SHALL be persistent until user upgrades.
4. THE Application SHALL render basic static content without JavaScript enabled (no-JS fallback): page structure visible, navigation links functional, error message displayed ("This application requires JavaScript. Please enable it in your browser settings."); interactive features (search, filters, command palette) gracefully disabled without blocking page load.
5. WHERE responsive design is implemented, THE Breakpoints_Used SHALL follow TailwindCSS defaults: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px); a Lighthouse audit on multiple viewport widths SHALL confirm responsive behavior.
6. THE Mobile_Layout (320px–767px) SHALL: (a) stack all components vertically, (b) adjust typography minimum 16px font size for readability, (c) use touch targets ≥44px height/width per WCAG guidelines, (d) hide non-critical sidebar or move to hamburger menu.
7. THE Tablet_Layout (768px–1023px) SHALL present: (a) single-column primary content with optional sidebar toggled via button, or (b) two-column layout if space permits; responsive grid system SHALL reflow components naturally.
8. THE Desktop_Layout (1024px+) SHALL use the full split-view design: Navigator panel (240–320px fixed or collapsible) + Detail panel (remaining width); sidebar remains visible and expanded by default.
9. IF the browser's JavaScript runtime detects unsupported APIs (e.g., missing fetch, WeakMap, Proxy if used), THE Polyfill_Loader SHALL attempt dynamic injection of fallback polyfills; if injection fails, the application SHALL disable dependent features and display an error message ("Some features are unavailable in your browser; please upgrade").


### Requirement 12: Future-Ready Architecture (Stages 2–4 Extensibility)

**User Story:** As a platform architect, I want to design the Stage 1 UI to support Stages 2–4 without refactoring, so that new features integrate cleanly.

#### Acceptance Criteria

1. THE Navigation_Structure (sidebar) SHALL include menu items for future stages with these attributes: text label (e.g., "Architecture Studio"), icon, href pointing to placeholder route, and `disabled: true` styling (opacity 0.5, cursor not-allowed, no hover effects) until stage is released; a visual indicator (e.g., "Coming Soon" badge) SHALL appear on disabled items.
2. THE Routing_System SHALL reserve but NOT implement route paths: `/architecture`, `/decisions`, `/reasoning`, `/time-machine`, `/universe`; requests to these routes SHALL return a 404 error page with the message "This feature is coming in Stage [N]" and navigation suggestions back to Stage 1 features.
3. THE API_Client_Layer SHALL be designed to accept additional endpoint registrations without modifying existing layer implementations; a plugin-based endpoint registration function SHALL accept new endpoint definitions (method, path, handler) allowing Stage 2+ modules to register their API clients at app initialization.
4. WHERE React Flow and ELK.js are needed for graph visualization (Architecture Studio in Stage 2, 3D Universe in Stage 4), THE Application_Dependencies (package.json) SHALL include these libraries as optional dependencies (lazy-loaded, not bundled with Stage 1); the import statements SHALL use dynamic `import()` only when graph features are accessed.
5. THE Component_Library_Structure SHALL support new component categories (GraphView, TimelineView, ReasoningPanel, 3DViewer) by directory organization; new directories in `/components` MAY be created for Stages 2–4 without affecting Stage 1 component exports or build system.
6. THE Zustand_Store_Architecture SHALL be designed such that each store module exports its own hook (e.g., `useUIStore`, `useSearchStore`) with no cross-store dependencies; new stores for future stages (DecisionStore, ReasoningStore) MAY be added in `/stores` directory WITHOUT modifying existing stage 1 stores or requiring index.ts restructuring (additive composition pattern).
7. THE TypeScript_Types_Directory (`/types`) SHALL export base types designed for extension: `type Entity`, `type SemanticLayer`, `type GraphNode`, `type GraphEdge` with generic parameters allowing future types to extend without modification; TSDoc comments SHALL document extension patterns with examples.
8. WHEN Stage 2 or later is integrated, THE Integration_Process SHALL require changes ONLY to: (a) environment variables (feature flags), (b) new directories added under `/app`, `/components`, `/features`, `/stores` (no moving/renaming of Stage 1 code), (c) updating navigation sidebar; Stage 1 files SHALL NOT be modified.
9. THE Build_Configuration (next.config.js) SHALL support feature flags using environment variables: `NEXT_PUBLIC_STAGE_{STAGE_NAME}_ENABLED` (e.g., `NEXT_PUBLIC_STAGE_ARCHITECTURE_ENABLED`); feature flags have default value `false` at build time and MAY be toggled via environment variables during deployment; a feature-gated route component SHALL conditionally render based on feature flags.
10. THE Default_Feature_Flag_Behavior SHALL be: (a) all Stage 2+ features disabled by default (NEXT_PUBLIC_STAGE_* = false), (b) Stage 1 features always enabled, (c) disabled routes return 404 with helpful messaging, (d) sidebar items for disabled features show "Coming Soon" badge.
11. THE Route_Guard_System SHALL implement a helper function (`isFeatureEnabled(stage)`) that checks feature flags and returns true/false; protected routes use this guard to conditionally render or return 404, enabling clean Stage 2+ rollout without code changes to Stage 1.


### Requirement 13: Constraints and Dependencies

**User Story:** As a project stakeholder, I want clear constraints and dependencies, so that scope and technical choices remain fixed.

#### Acceptance Criteria

1. THE Technology_Stack_Is_Fixed_and_Locked: (a) Next.js 15 (no version 14 or earlier, no version 16+), (b) React 19 (no earlier versions), (c) TypeScript (latest, strict mode), (d) TailwindCSS v4 (no v3 or earlier), (e) shadcn/ui (latest compatible), (f) Zustand (latest), (g) TanStack Query v5 (no v4 or earlier), (h) Framer Motion (latest); any attempt to substitute or upgrade these SHALL be flagged as out-of-scope and require explicit stakeholder approval.
2. THE Backend_Endpoint_Is_Fixed at `http://localhost:8000/api/v1` and THE Frontend_Runs_On_Fixed port `3000`; no backend changes are allowed to accommodate frontend requirements; frontend architecture SHALL assume backend API contracts are immutable and only configurable via environment variables (API_URL) if deployment environments change.
3. THE Design_Philosophy_Is_Fixed_and_Enforced: (a) dark-first color scheme only (#090B10 background, #111318 surface), (b) enterprise minimal aesthetic (no bright colors, no cartoon-like UI elements), (c) motion curation (Framer Motion animations only, no external animation libraries), (d) no extraneous animations (animations purposeful, <400ms, follow reduced-motion preference); design review SHALL enforce these constraints.
4. THE Backend_API_Contracts_Are_Assumed and fixed (no modifications allowed to align with frontend requirements): all JSON responses use `application/json` content-type; error responses follow structure `{ error: { code: string, message: string, status: number } }`; pagination responses include `{ items: [...], limit: number, offset: number, total: number }`; Capability, Concept, Entity types have required fields and optional fields marked with `?` in TypeScript interfaces.
5. WHEN a requirement conflicts with the fixed tech stack (e.g., a requirement demands Vue.js or a custom CSS-in-JS solution), THE Requirement_Specification_Adjustment takes precedence: the stack is NOT modified; instead, the requirement is reframed to work within the fixed stack constraints.
6. THE No_Breaking_Changes_Rule_Is_Enforced: the Stage 1 architecture SHALL remain compatible with Stages 2–4 integration; adding new features SHALL NOT require refactoring or moving existing Stage 1 code; any Stage 1 file modifications during Stage 2+ integration SHALL be limited to: (a) adding new imports for optional dependencies, (b) enabling feature flags, (c) updating navigation sidebar, (d) no changes to component signatures, state structure, or API client contracts.
7. WHERE CORS is required, THE Configuration SHALL assume frontend at `localhost:3000` and backend at `localhost:8000` (no proxy layer); CORS is already configured on backend (config.py) to accept requests from `localhost:3000`; frontend proxy configuration is NOT needed.
8. THE Development_Dependencies (not included in Stage 1 build, reserved for future build/test phases) SHALL include: TypeScript compiler, ESLint, Prettier, Vitest or Jest (test runner), Testing Library (@testing-library/react), Storybook (optional component library tool); these are documented in package.json as devDependencies but tests are not written until Stage 2+ (or post-Stage 1 iteration).


### Requirement 14: Error Handling and Edge Cases

**User Story:** As a resilient platform, I want graceful handling of errors and edge cases, so that users are never left with broken experiences.

#### Acceptance Criteria

1. IF the backend API is unreachable (connection refused, ECONNREFUSED, DNS failure, or timeout after 10 seconds), THE Error_Boundary SHALL display: error message "Unable to connect to the server. Please check your connection and try again." with a "Retry" button; users MAY continue browsing cached data if available.
2. WHEN an API request times out (no response after 10 seconds), THE Request_Handler SHALL display a timeout error: "Request timed out. Please try again or check your connection." with manual retry option; the request SHALL NOT auto-retry after timeout.
3. IF a required environment variable is missing at runtime (e.g., NEXT_PUBLIC_API_URL), THE Application_Bootstrap SHALL: (a) log to console: "Missing environment variable: NEXT_PUBLIC_API_URL", (b) render an error page displaying "Configuration error: application cannot start. Please check server logs." in a user-friendly format (gray background, centered text).
4. WHEN a user navigates to a non-existent capability ID or invalid route (e.g., `/capabilities/invalid-id`), THE Application SHALL: (a) render a 404 error page, (b) display message "Capability not found", (c) provide navigation suggestions with links to Dashboard and Capabilities Explorer.
5. IF the TanStack Query cache becomes invalid or corrupted, THE Cache_Recovery_Mechanism SHALL: (a) automatically detect corruption (by comparing cache version against schema), (b) invalidate the corrupted query, (c) trigger automatic refetch on next access; users SHALL not see errors during recovery (transparent).
6. WHEN the user's browser localStorage is full or unavailable, THE State_Persistence (Zustand store persistence middleware) SHALL: (a) catch localStorage errors, (b) gracefully degrade: UI state (selected capability, filters) is lost on refresh but features work normally, (c) log warning "localStorage unavailable—session state not persisted".
7. WHERE a third-party library fails to load (e.g., Framer Motion, React Flow, ELK.js lazy-loaded for Stage 2+), THE Component_Fallback SHALL: (a) render a basic version without the library (e.g., static content instead of animation, matrix view instead of graph), (b) display optional message: "Advanced rendering unavailable", (c) allow users to continue using core features.
8. IF the application detects unsupported JavaScript features at runtime (via try-catch or feature detection), THE Polyfill_Loader SHALL: (a) attempt dynamic polyfill injection, (b) if injection fails, disable dependent features with message "Some features unavailable in your browser. Please upgrade."
9. WHERE API errors occur during search or filtering, THE Error_Handler SHALL: (a) preserve user input in search/filter form, (b) display error message "Search failed. Please try again." with a Retry button, (c) allow users to continue with cached results if available.


### Requirement 15: Design System Tokens and Theme Configuration

**User Story:** As a developer, I want a comprehensive design system with all tokens centralized, so that theming and component styling remain consistent.

#### Acceptance Criteria

1. THE Color_Palette SHALL include: (a) base colors: background #090B10, surface #111318; (b) semantic colors: primary #3B82F6, success #10B981, warning #F59E0B, error #EF4444, info #06B6D4; (c) 10-tier neutral grays: gray-50 #F9FAFB through gray-900 #111318 with 50-point increments; (d) text colors: primary #F9FAFB, secondary #D1D5DB, tertiary #9CA3AF.
2. THE Typography_Scale SHALL define: H1 (32px, weight 700, line-height 1.2), H2 (28px, 700, 1.25), H3 (24px, 700, 1.3), H4 (20px, 600, 1.35), H5 (16px, 600, 1.4), H6 (14px, 600, 1.4), Body (14px, 400, 1.5), Caption (12px, 400, 1.4), Code (13px monospace, 500, 1.6).
3. THE Spacing_Scale SHALL define: xs (4px), sm (8px), md (12px), lg (16px), xl (24px), 2xl (32px), 3xl (48px), 4xl (64px) for all margins, padding, and gaps.
4. WHEN a page transition occurs, THE Motion_Preset fade-in SHALL apply: opacity 0→1 over 200ms with ease-out cubic-bezier(0, 0, 0.58, 1).
5. WHEN a component enters (mounts), THE Motion_Preset slide-up SHALL apply: translateY +20px→0 over 300ms with ease-out cubic-bezier(0, 0, 0.58, 1).
6. WHEN a modal or overlay opens, THE Motion_Preset scale-in SHALL apply: scale 0.95→1 over 200ms with ease-out cubic-bezier(0, 0, 0.58, 1).
7. THE Border_Radius_Scale SHALL define: sm (2px), md (4px), lg (8px), xl (12px), full (9999px) for all corners, pills, and circles.
8. THE Shadow_Scale SHALL define: sm (0 1px 2px rgba(0,0,0,0.12)), md (0 4px 6px rgba(0,0,0,0.1)), lg (0 10px 15px rgba(0,0,0,0.1)), xl (0 20px 25px rgba(0,0,0,0.15)).
9. WHERE these tokens are used, THE Implementation SHALL expose them as: (a) CSS variables using format `var(--{category}-{name})` with examples `var(--color-primary)`, `var(--spacing-lg)`, `var(--shadow-md)`; (b) a flat TypeScript object exported from `/styles/tokens.ts` with hierarchical keys (e.g., `colors.primary`, `spacing.lg`, `shadows.md`); (c) TailwindCSS theme extensions in `tailwind.config.js` that map custom keys to CSS variables.
10. THE Tailwind_Config SHALL extend the base theme with custom tokens WITHOUT overriding shadcn/ui defaults; custom token keys SHALL use distinct naming (e.g., `customColor` not `color`) to avoid shadowing built-in Tailwind utilities.
11. THE Design_System SHALL support future theme extensions (Stages 2–4) by centralizing all token definitions in a single `/styles/tokens.ts` module; new tokens MAY be added to this module without requiring changes to component files or TailwindCSS config (additive pattern).


## Non-Functional Requirements

### Performance

- **First Contentful Paint (FCP)**: <1 second on 4G
- **Largest Contentful Paint (LCP)**: <2 seconds on 4G
- **Cumulative Layout Shift (CLS)**: <0.1
- **Time to Interactive (TTI)**: <3 seconds
- **Bundle Size (gzipped)**: <500 KB (JS + CSS)
- **API Response Time**: <500ms (p95)
- **Search Latency**: <200ms for 1000 capabilities
- **Filter Update Latency**: <150ms for multi-criteria filters
- **Scroll Performance**: 60 FPS on lists with 500+ items (virtualized)

### Scalability

- **Concurrent Users**: Design for 100 simultaneous users without performance degradation
- **Capability Count**: Support 1000+ capabilities without UI lag
- **Concept Count**: Support 10000+ concepts without performance issues
- **Entity Count**: Support 100000+ entities (lazy-loaded, not all in memory)
- **Query Cache**: Maintain up to 50 MB of cached data
- **Browser Memory**: Target <200 MB heap usage at typical usage (1 dashboard + 1 explorer open)

### Reliability

- **Uptime Target**: N/A for frontend (but gracefully handles backend downtime)
- **Error Recovery**: All errors recoverable with retry or reload
- **Data Consistency**: Cache invalidation triggers full refetch on data changes
- **Session Duration**: Session persists for 8 hours or until browser close

### Maintenance and Testing

- **Code Coverage**: Targeting >70% coverage for utilities and hooks (tests created in Stage 2+)
- **TypeScript Strictness**: Strict mode enabled (noImplicitAny, strictNullChecks, etc.)
- **Linting**: ESLint rules enforced, Prettier formatting applied
- **Documentation**: All components and hooks include JSDoc comments

## API Contract Assumptions

### Base Endpoint
- `http://localhost:8000/api/v1`

### Assumed Endpoints and Response Shapes

#### 1. List Capabilities
```
GET /capabilities?limit=50&offset=0&category=auth
Response: {
  items: Array<Capability>,
  total: number,
  limit: number,
  offset: number
}

Capability = {
  id: string,
  name: string,
  description: string,
  category: string,
  risk_level: "low" | "medium" | "high" | "critical",
  dependency_count: number,
  last_modified: string (ISO 8601),
  concepts: Array<{ id: string, name: string }>,
  entities: Array<{ id: string, name: string, type: string }>,
  stats: { complexity: number, coverage: number }
}
```

#### 2. Get Capability Detail
```
GET /capabilities/{id}
Response: Capability (as above, potentially with expanded nested data)
```

#### 3. Get Repository Overview
```
GET /repositories/{id}
Response: {
  id: string,
  name: string,
  health: { status: "healthy" | "warning" | "critical", score: number },
  capabilities_total: number,
  concepts_total: number,
  entities_total: number,
  recent_changes: Array<{ timestamp: string, type: "added" | "modified" | "removed", capability_id: string, capability_name: string }>
}
```

#### 4. Search
```
GET /search?query=auth&limit=20
Response: {
  capabilities: Array<Capability>,
  concepts: Array<Concept>,
  entities: Array<Entity>
}

Concept = { id: string, name: string, description: string, related_capabilities: Array<{ id: string, name: string }> }
Entity = { id: string, name: string, type: string, capability_id: string }
```

#### 5. Get Semantic Layers (per capability)
```
GET /capabilities/{id}/semantic/structural
GET /capabilities/{id}/semantic/semantic
GET /capabilities/{id}/semantic/behavior
GET /capabilities/{id}/semantic/concept
GET /capabilities/{id}/semantic/architecture
GET /capabilities/{id}/semantic/decision

Response shapes vary per layer but follow a LayerData structure:
{
  layer: string,
  data: object (layer-specific),
  metadata: { generated_at: string, version: number }
}
```

### Error Responses
```
All error responses follow:
{
  error: {
    code: string (e.g., "CAPABILITY_NOT_FOUND"),
    message: string,
    status: number (HTTP status)
  }
}

Common error codes:
- NOT_FOUND (404): Resource doesn't exist
- VALIDATION_ERROR (400): Request validation failed
- INTERNAL_ERROR (500): Server error
- UNAUTHORIZED (401): Authentication required
- FORBIDDEN (403): Permission denied
```


## Design System Requirements - Detailed Specifications

### Color Palette (Dark Theme)

#### Base Colors
- **Background**: #090B10 (near-black, primary page background)
- **Surface**: #111318 (slightly lighter, for cards, modals, elevated surfaces)
- **Overlay**: rgba(0, 0, 0, 0.5) (for dimmed backdrops)

#### Semantic Colors
- **Primary**: #3B82F6 (blue, for primary actions and highlights)
- **Success**: #10B981 (green, for success states)
- **Warning**: #F59E0B (amber, for warnings)
- **Error**: #EF4444 (red, for errors and critical states)
- **Info**: #06B6D4 (cyan, for informational content)

#### Neutral Grays
- **Gray-900**: #111318 (text on light backgrounds)
- **Gray-800**: #1F2937 (secondary text)
- **Gray-700**: #374151 (tertiary text, borders)
- **Gray-600**: #4B5563 (disabled text, subtle borders)
- **Gray-500**: #6B7280 (lighter borders)
- **Gray-400**: #9CA3AF (placeholders, hints)
- **Gray-300**: #D1D5DB (light borders)
- **Gray-200**: #E5E7EB (very light backgrounds)
- **Gray-100**: #F3F4F6 (lightest, not used in dark theme)

#### Text Colors
- **Primary Text**: #F9FAFB (near-white for body text)
- **Secondary Text**: #D1D5DB (muted text)
- **Tertiary Text**: #9CA3AF (additional info, hints)
- **Link**: #3B82F6 (primary blue)
- **Link Hover**: #1D4ED8 (darker blue)

### Typography

#### Font Families
- **Heading Font**: System font stack (e.g., -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif)
- **Body Font**: Same system stack for consistency
- **Code Font**: "Courier New", "Monaco", "Consolas", monospace

#### Type Scale
| Level | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| H1 | 32px | 700 | 1.2 | Page title |
| H2 | 28px | 700 | 1.25 | Section heading |
| H3 | 24px | 700 | 1.3 | Subsection heading |
| H4 | 20px | 600 | 1.35 | Component heading |
| H5 | 16px | 600 | 1.4 | Sub-heading |
| H6 | 14px | 600 | 1.4 | Small heading |
| Body-L | 16px | 400 | 1.5 | Long-form text, body |
| Body | 14px | 400 | 1.5 | Default body text |
| Caption | 12px | 400 | 1.4 | Captions, hints |
| Code | 13px | 500 | 1.6 | Code blocks, inline code |

### Spacing Scale

All spacing values follow an 8px base:
- **xs**: 4px (fine spacing within components)
- **sm**: 8px (default spacing between elements)
- **md**: 12px (moderate spacing)
- **lg**: 16px (larger spacing, common for padding)
- **xl**: 24px (section spacing)
- **2xl**: 32px (major spacing between sections)
- **3xl**: 48px (large spacing, rarely used)
- **4xl**: 64px (extra-large spacing, rarely used)

### Border Radius

- **sm**: 2px (minimal rounding)
- **md**: 4px (default, most UI elements)
- **lg**: 8px (buttons, cards)
- **xl**: 12px (larger modals, panels)
- **full**: 9999px (fully rounded, pills, circles)

### Shadows

- **sm**: 0 1px 2px rgba(0, 0, 0, 0.12)
- **md**: 0 4px 6px rgba(0, 0, 0, 0.1)
- **lg**: 0 10px 15px rgba(0, 0, 0, 0.1)
- **xl**: 0 20px 25px rgba(0, 0, 0, 0.15)

### Motion and Transitions

#### Default Durations
- **Quick**: 150ms (micro-interactions)
- **Normal**: 200ms (standard transitions)
- **Slow**: 300ms (emphasis transitions)
- **Slower**: 400ms (large component transitions)

#### Easing Functions (cubic-bezier)
- **Ease-In**: (0.42, 0, 1, 1) (accelerating motion)
- **Ease-Out**: (0, 0, 0.58, 1) (decelerating motion)
- **Ease-In-Out**: (0.42, 0, 0.58, 1) (smooth, natural motion)
- **Linear**: (0, 0, 1, 1) (constant speed)

#### Common Motion Presets
- **Fade In**: opacity 0 → 1, 200ms ease-out
- **Slide Up**: translateY +20px → 0, 300ms ease-out
- **Scale In**: scale 0.95 → 1, 200ms ease-out
- **Rotate In**: rotate -10deg → 0, 300ms ease-out

### Component Sizing

- **Icon Size - Small**: 16px
- **Icon Size - Medium**: 24px
- **Icon Size - Large**: 32px
- **Button Height - Small**: 32px
- **Button Height - Medium**: 40px
- **Button Height - Large**: 48px
- **Input Height**: 40px
- **List Item Height**: 40px–48px


## Project Structure and File Organization

The frontend SHALL be organized as follows (to be created during design phase):

```
frontend/
├── app/                          # Next.js 15 App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Dashboard page (/)
│   ├── capabilities/            # Capability Explorer
│   │   └── page.tsx
│   ├── api/                     # API routes (if needed for middleware)
│   ├── error.tsx                # Global error boundary
│   └── not-found.tsx            # 404 page
├── components/                  # Reusable UI components
│   ├── ui/                      # shadcn/ui and custom UI components
│   ├── layout/                  # Layout components (Header, Sidebar, Footer)
│   ├── dashboard/               # Dashboard-specific components
│   ├── explorer/                # Explorer-specific components
│   ├── search/                  # Search-related components
│   └── command-palette/         # Command palette components
├── features/                    # Feature modules (for future stages)
│   ├── dashboard/               # Dashboard module
│   ├── explorer/                # Explorer module
│   ├── search/                  # Search module
│   └── [future-stage]/          # Placeholder directories for Stages 2–4
├── lib/                         # Utility functions and helpers
│   ├── api.ts                   # API client factory
│   ├── utils.ts                 # Common utilities (cn, debounce, etc.)
│   ├── constants.ts             # App constants and URLs
│   └── formatting.ts            # Formatters (date, size, etc.)
├── hooks/                       # Custom React hooks
│   ├── useSearch.ts
│   ├── useDashboard.ts
│   ├── useExplorer.ts
│   └── useCommandPalette.ts
├── api/                         # API client layer
│   ├── client.ts                # Axios/fetch client
│   ├── endpoints.ts             # Endpoint definitions and functions
│   ├── queries.ts               # TanStack Query definitions
│   └── types.ts                 # API response types
├── stores/                      # Zustand state stores
│   ├── ui-store.ts              # UI state (selected capability, filters, sidebar state)
│   ├── search-store.ts          # Search state (recent searches)
│   ├── [future-stage]-store.ts  # Placeholders for future stages
│   └── index.ts                 # Store exports
├── types/                       # TypeScript type definitions
│   ├── capability.ts
│   ├── concept.ts
│   ├── entity.ts
│   ├── api.ts
│   ├── semantic.ts              # Semantic layer types
│   └── index.ts
├── styles/                      # Global styles and tokens
│   ├── globals.css              # Global styles
│   ├── tokens.ts                # Design system tokens (TypeScript)
│   └── animations.css           # Animation definitions
├── public/                      # Static assets
│   └── [images, icons, etc.]
├── .env.local                   # Local environment variables
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # TailwindCSS configuration
├── tsconfig.json                # TypeScript configuration
├── package.json                 # Project dependencies
└── README.md                    # Project documentation
```

## Acceptance Criteria Summary

| Requirement | Key Acceptance Criteria |
|-------------|------------------------|
| 1. Design System | Dark theme (#090B10, #111318), 8px spacing scale, motion presets |
| 2. Dashboard | 4 widgets, <3s load, status indicators, recent changes |
| 3. Explorer Navigator | Hierarchical tree, fuzzy search <150ms, filters, virtualization >50 items |
| 4. Explorer Detail Tabs | 7 tabs (Structural, Semantic, Behavior, Concept, Capability, Architecture, Decision) |
| 5. Global Search | Fuzzy search <200ms, grouping, recent searches, highlights |
| 6. Command Palette | Ctrl+K trigger, keyboard nav, filtering, recent commands |
| 7. Architecture | Next.js App Router, clear folder structure, extensible for Stages 2–4 |
| 8. API Integration | Typed endpoints, retry logic (3x), error handling, pagination |
| 9. Performance | <3s load (4G), 60 FPS lists, <500KB bundle, <200ms search |
| 10. Accessibility | WCAG AA, semantic HTML, ARIA labels, keyboard navigation, 4.5:1 contrast |
| 11. Browser Support | Chrome/Edge 120+, Firefox 121+, Safari 17+, no JS degradation |
| 12. Future Extensibility | Placeholder routes and stores, lazy-loaded Stage 2–4 libraries, no breaking changes |
| 13. Constraints | Fixed tech stack, no backend changes, dark theme only, localhost:3000/8000 |
| 14. Error Handling | Graceful fallbacks, user-friendly messages, retry logic, error logging |
| 15. Design Tokens | Complete color palette, typography scale, spacing, shadows, motion |

