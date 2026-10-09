import type { Metadata } from "next";
import Link from "next/link";
import { StatusPage } from "@/components/status-page";
import { buttonStyles } from "@/components/ui";

export const metadata: Metadata = {
  title: "Page not found",
  description: "This page doesn’t exist on TuskApp. Head back to your dashboard.",
};

export default function NotFound() {
  return (
    <StatusPage
      code="404"
      title="This page isn’t here"
      actions={
        <>
          <Link href="/" className={buttonStyles.primary}>
            Go to dashboard
          </Link>
          <Link href="/customers" className={buttonStyles.secondary}>
            Find a customer
          </Link>
        </>
      }
    >
      The link may be old, or the booking or customer was removed. Everything else is where you left it.
    </StatusPage>
  );
}
