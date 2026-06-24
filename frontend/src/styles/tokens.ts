/**
 * Design System Tokens — Software Intelligence Platform
 * Single source of truth for all design tokens.
 * Consumed by: globals.css (CSS variables), tailwind.config.ts, components.
 */

export const tokens = {
  colors: {
    // Base backgrounds
    bg: {
      base: "#090B10",
      surface: "#111318",
      surfaceElevated: "#161A22",
      overlay: "rgba(0, 0, 0, 0.5)",
    },
    // Border
    border: {
      default: "#222938",
      subtle: "#1A1F2E",
      strong: "#2D3548",
    },
    // Semantic colors
    primary: "#4F7CFF",
    primaryHover: "#3D67E8",
    primaryMuted: "rgba(79, 124, 255, 0.12)",
    success: "#22C55E",
    successMuted: "rgba(34, 197, 94, 0.12)",
    warning: "#F59E0B",
    warningMuted: "rgba(245, 158, 11, 0.12)",
    danger: "#EF4444",
    dangerMuted: "rgba(239, 68, 68, 0.12)",
    info: "#06B6D4",
    infoMuted: "rgba(6, 182, 212, 0.12)",
    // Neutral grays
    gray: {
      50: "#F9FAFB",
      100: "#F3F4F6",
      200: "#E5E7EB",
      300: "#D1D5DB",
      400: "#9CA3AF",
      500: "#6B7280",
      600: "#4B5563",
      700: "#374151",
      800: "#1F2937",
      900: "#111318",
    },
    // Text
    text: {
      primary: "#F0F2F8",
      secondary: "#8B95B0",
      tertiary: "#5A6480",
      muted: "#3D4560",
      inverse: "#090B10",
      link: "#4F7CFF",
      linkHover: "#3D67E8",
    },
  },

  typography: {
    fontFamily: {
      sans: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      mono: '"JetBrains Mono", "Courier New", "Monaco", "Consolas", monospace',
    },
    fontSize: {
      h1: "2rem",        // 32px
      h2: "1.75rem",     // 28px
      h3: "1.5rem",      // 24px
      h4: "1.25rem",     // 20px
      h5: "1rem",        // 16px
      h6: "0.875rem",    // 14px
      bodyLg: "1rem",    // 16px
      body: "0.875rem",  // 14px
      caption: "0.75rem",// 12px
      code: "0.8125rem", // 13px
      xs: "0.6875rem",   // 11px
    },
    fontWeight: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.2,
      snug: 1.25,
      normal: 1.5,
      relaxed: 1.6,
    },
    letterSpacing: {
      tight: "-0.02em",
      normal: "0em",
      wide: "0.05em",
      wider: "0.1em",
    },
  },

  spacing: {
    0: "0px",
    xs: "4px",
    sm: "8px",
    md: "12px",
    lg: "16px",
    xl: "24px",
    "2xl": "32px",
    "3xl": "48px",
    "4xl": "64px",
    "5xl": "80px",
    "6xl": "96px",
  },

  radii: {
    none: "0px",
    sm: "2px",
    md: "4px",
    lg: "6px",
    xl: "8px",
    "2xl": "12px",
    full: "9999px",
  },

  shadows: {
    none: "none",
    sm: "0 1px 2px rgba(0, 0, 0, 0.4)",
    md: "0 4px 6px rgba(0, 0, 0, 0.3)",
    lg: "0 10px 15px rgba(0, 0, 0, 0.3)",
    xl: "0 20px 25px rgba(0, 0, 0, 0.35)",
    glow: "0 0 0 1px rgba(79, 124, 255, 0.3), 0 0 12px rgba(79, 124, 255, 0.15)",
    glowDanger: "0 0 0 1px rgba(239, 68, 68, 0.3)",
  },

  motion: {
    duration: {
      instant: "0ms",
      quick: "100ms",
      fast: "150ms",
      normal: "200ms",
      slow: "300ms",
      slower: "400ms",
    },
    easing: {
      easeOut: "cubic-bezier(0, 0, 0.58, 1)",
      easeIn: "cubic-bezier(0.42, 0, 1, 1)",
      easeInOut: "cubic-bezier(0.42, 0, 0.58, 1)",
      spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
      linear: "linear",
    },
  },

  zIndex: {
    base: 0,
    raised: 1,
    dropdown: 100,
    sticky: 200,
    overlay: 300,
    modal: 400,
    toast: 500,
    tooltip: 600,
  },

  breakpoints: {
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px",
  },

  sizing: {
    sidebar: {
      expanded: "220px",
      collapsed: "60px",
    },
    topBar: "56px",
    navigatorPanel: "300px",
  },
} as const;

export type Tokens = typeof tokens;

// Risk level color map — used across multiple components
export const riskColors = {
  low: tokens.colors.success,
  medium: tokens.colors.warning,
  high: "#F97316", // orange
  critical: tokens.colors.danger,
} as const;

export type RiskLevel = keyof typeof riskColors;

// Health status color map
export const healthColors = {
  healthy: tokens.colors.success,
  warning: tokens.colors.warning,
  critical: tokens.colors.danger,
  unknown: tokens.colors.gray[500],
} as const;

export type HealthStatus = keyof typeof healthColors;

// Capability type color map
export const capabilityTypeColors: Record<string, string> = {
  AI: "#8B5CF6",
  BUSINESS: tokens.colors.primary,
  TECHNICAL: tokens.colors.info,
  INFRASTRUCTURE: "#F97316",
  SECURITY: tokens.colors.danger,
  INTEGRATION: "#10B981",
  DEFAULT: tokens.colors.gray[500],
};

export default tokens;
