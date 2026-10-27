"use client";

/**
 * Root page — branches on auth + onboarding state.
 *
 * Replaces the previous blind `redirect("/dashboard")`. Now:
 *  - signed-out           → /sign-in
 *  - signed-in, new user  → /onboarding (one-time 2-min tour)
 *  - signed-in, onboarded → /dashboard
 *
 * "Onboarded" is a localStorage flag (sip-onboarding-completed). The
 * Settings page can clear it to re-trigger the tour.
 */
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useHydrated } from "@/hooks/useHydrated";
import { Compass } from "lucide-react";
import { Card, Stack, Text } from "@/components/ui";
import { SignedIn, SignedOut, useUser } from "@clerk/nextjs";

const ONBOARDING_KEY = "sip-onboarding-completed";
const HAS_CLERK = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

export default function RootPage() {
  const router = useRouter();
  const isHydrated = useHydrated();

  if (HAS_CLERK) {
    return <ClerkBranch router={router} isHydrated={isHydrated} />;
  }

  // No Clerk → dev mode: treat as signed-in, check onboarding.
  return <DevBranch router={router} isHydrated={isHydrated} />;
}

function DevBranch({
  router,
  isHydrated,
}: {
  router: ReturnType<typeof useRouter>;
  isHydrated: boolean;
}) {
  useEffect(() => {
    if (!isHydrated) return;
    const onboarded = isOnboarded();
    router.replace(onboarded ? "/dashboard" : "/onboarding");
  }, [isHydrated, router]);

  return <LoadingCard />;
}

function ClerkBranch({
  router,
  isHydrated,
}: {
  router: ReturnType<typeof useRouter>;
  isHydrated: boolean;
}) {
  const { isSignedIn, isLoaded } = useUser();

  useEffect(() => {
    if (!isHydrated || !isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in");
      return;
    }
    router.replace(isOnboarded() ? "/dashboard" : "/onboarding");
  }, [isHydrated, isLoaded, isSignedIn, router]);

  // Belt-and-suspenders: if Clerk is misconfigured, fall through to the
  // dashboard rather than showing a blank page.
  return (
    <>
      <SignedIn>
        <LoadingCard />
      </SignedIn>
      <SignedOut>
        <LoadingCard />
      </SignedOut>
    </>
  );
}

function isOnboarded(): boolean {
  try {
    return window.localStorage.getItem(ONBOARDING_KEY) === "true";
  } catch {
    return false;
  }
}

function LoadingCard() {
  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <Card padded className="max-w-md w-full">
        <Stack direction="vertical" gap={4} align="center">
          <Compass
            size={32}
            className="text-[var(--color-primary)]"
            aria-hidden
          />
          <Stack direction="vertical" gap={1} align="center">
            <Text variant="heading" className="text-center">
              Software Intelligence Platform
            </Text>
            <Text variant="body" tone="muted" className="text-center">
              Loading your workspace…
            </Text>
          </Stack>
        </Stack>
      </Card>
    </div>
  );
}

export const ONBOARDING_STORAGE_KEY = ONBOARDING_KEY;
