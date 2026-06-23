import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: {
    default: "Software Intelligence Platform",
    template: "%s | SIP",
  },
  description:
    "Enterprise software intelligence platform for exploring code capabilities, architecture, and reasoning across large codebases.",
  keywords: ["software intelligence", "code analysis", "capabilities", "architecture"],
  robots: { index: false, follow: false }, // Internal tool — no indexing
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        {/* Preconnect to Google Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body
        className="min-h-screen antialiased"
        style={{
          backgroundColor: "var(--color-bg-base)",
          color: "var(--color-text-primary)",
          fontFamily: "var(--font-sans)",
        }}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
