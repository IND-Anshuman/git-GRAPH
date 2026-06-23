import { redirect } from "next/navigation";

/** Root page — redirects to dashboard. */
export default function RootPage() {
  redirect("/dashboard");
}
