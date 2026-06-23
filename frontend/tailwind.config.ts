import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Custom color palette — uses distinct prefix to avoid shadowing shadcn/ui defaults
      colors: {
        sip: {
          bg: "var(--color-bg-base)",
          surface: "var(--color-bg-surface)",
          elevated: "var(--color-bg-surface-elevated)",
          border: "var(--color-border)",
          "border-subtle": "var(--color-border-subtle)",
          "border-strong": "var(--color-border-strong)",
          primary: "var(--color-primary)",
          "primary-hover": "var(--color-primary-hover)",
          "primary-muted": "var(--color-primary-muted)",
          success: "var(--color-success)",
          "success-muted": "var(--color-success-muted)",
          warning: "var(--color-warning)",
          "warning-muted": "var(--color-warning-muted)",
          danger: "var(--color-danger)",
          "danger-muted": "var(--color-danger-muted)",
          info: "var(--color-info)",
          "text-primary": "var(--color-text-primary)",
          "text-secondary": "var(--color-text-secondary)",
          "text-tertiary": "var(--color-text-tertiary)",
          "text-muted": "var(--color-text-muted)",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      spacing: {
        "18": "4.5rem",
        "22": "5.5rem",
        "sidebar": "var(--sidebar-width)",
        "topbar": "var(--topbar-height)",
        "navigator": "var(--navigator-width)",
      },
      borderRadius: {
        DEFAULT: "var(--radius-md)",
      },
      boxShadow: {
        "sip-sm": "var(--shadow-sm)",
        "sip-md": "var(--shadow-md)",
        "sip-lg": "var(--shadow-lg)",
        "sip-xl": "var(--shadow-xl)",
        "sip-glow": "var(--shadow-glow)",
      },
      transitionDuration: {
        "quick": "100ms",
        "fast": "150ms",
        "normal": "200ms",
        "slow": "300ms",
        "slower": "400ms",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "slide-down": {
          from: { opacity: "0", transform: "translateY(-8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          from: { opacity: "0", transform: "scale(0.96)" },
          to: { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          from: { backgroundPosition: "-200% 0" },
          to: { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 200ms cubic-bezier(0, 0, 0.58, 1) forwards",
        "slide-up": "slide-up 300ms cubic-bezier(0, 0, 0.58, 1) forwards",
        "slide-down": "slide-down 200ms cubic-bezier(0, 0, 0.58, 1) forwards",
        "scale-in": "scale-in 200ms cubic-bezier(0, 0, 0.58, 1) forwards",
        shimmer: "shimmer 1.5s ease-in-out infinite",
      },
      // Sidebar widths as max-w / min-w
      width: {
        "sidebar": "220px",
        "sidebar-collapsed": "60px",
        "navigator": "300px",
        "detail": "calc(100% - 300px)",
      },
      minWidth: {
        "sidebar": "220px",
        "navigator": "280px",
      },
      maxWidth: {
        "navigator": "360px",
      },
      height: {
        "topbar": "56px",
        "content": "calc(100vh - 56px)",
      },
    },
  },
  plugins: [],
};

export default config;
