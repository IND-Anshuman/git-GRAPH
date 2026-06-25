import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

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
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} dark`} suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
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

