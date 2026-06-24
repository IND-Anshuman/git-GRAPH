import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow all external image domains (for avatars, etc.)
  images: {
    remotePatterns: [],
  },

  // Strict React mode for better error detection
  reactStrictMode: true,


  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },

  // Experimental features
  experimental: {
    // Optimize package imports for commonly-used libraries
    optimizePackageImports: ["lucide-react", "recharts", "framer-motion"],
  },

  // Typescript errors fail the build
  typescript: {
    ignoreBuildErrors: false,
  },

};

export default nextConfig;
