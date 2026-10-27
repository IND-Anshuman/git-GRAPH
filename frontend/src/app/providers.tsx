"use client";

import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { useEffect, type ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { queryClient } from "@/lib/query-client";
import { registerTokenGetter, registerTokenRefresher } from "@/services/auth/tokenBridge";

/**
 * Registers the Clerk session-token getter + a forced-refresh function
 * into the non-React token bridge so the axios singleton can attach
 * Bearer headers and recover from 401s. Renders nothing.
 */
function AuthGate({ children }: { children: ReactNode }) {
  const { isLoaded, isSignedIn, getToken } = useAuth();

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    const unregisterGet = registerTokenGetter(() => getToken());
    // getToken() with no args uses Clerk's cache. Forcing a fresh token
    // requires `skipCache: true`. We wrap so the bridge stays typed.
    const unregisterRefresh = registerTokenRefresher(() =>
      getToken({ skipCache: true }),
    );
    return () => {
      unregisterGet();
      unregisterRefresh();
    };
  }, [isLoaded, isSignedIn, getToken]);

  return <>{children}</>;
}

/**
 * Root providers wrapper — Clerk (when configured) + TanStack Query.
 *
 * Clerk is OPTIONAL at build/runtime: when no publishable key is present
 * (local dev before the user adds real keys), the app renders without auth
 * and the backend's AUTH_ENABLED=false dev-user path matches. This keeps the
 * app runnable end-to-end before Clerk credentials exist.
 */
export function Providers({ children }: { children: ReactNode }) {
  const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

  const content = (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools
          initialIsOpen={false}
          buttonPosition="bottom-right"
        />
      )}
    </QueryClientProvider>
  );

  if (!clerkKey) {
    // No Clerk key yet — run unauthenticated (matches backend dev mode).
    return content;
  }

  return (
    <ClerkProvider>
      <AuthGate>{content}</AuthGate>
    </ClerkProvider>
  );
}
