"use client";

import Link from "next/link";
import { useEffect } from "react";
import { StatusPage } from "@/components/status-page";
import { buttonStyles } from "@/components/ui";

export default function RootError({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);
  return (
    <StatusPage
      title="Something went wrong"
      actions={
        <>
          <button type="button" onClick={retry} className={buttonStyles.primary}>
            Try again
          </button>
          <Link href="/" className={buttonStyles.secondary}>
            Go to dashboard
          </Link>
        </>
      }
    >
      We couldn’t load this page. Your bookings and customers are safe.
      {error.digest && <span className="num mt-2 block text-xs text-faint">Error ID {error.digest}</span>}
    </StatusPage>
  );
}
