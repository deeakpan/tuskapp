"use client";

import { RotateCw } from "lucide-react";
import { useEffect } from "react";
import { Card, buttonStyles } from "@/components/ui";

export default function DashboardError({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);
  return (
    <Card className="mx-auto mt-10 max-w-lg p-8 text-center" role="alert">
      <h1 className="text-xl font-strong">This page didn’t load</h1>
      <p className="mt-2 text-sm text-muted">
        The TuskApp server may be restarting. Your bookings and customers are safe — try again in a moment.
      </p>
      {error.digest && <p className="num mt-2 text-xs text-faint">Error ID {error.digest}</p>}
      <button type="button" onClick={retry} className={`${buttonStyles.primary} mt-6`}>
        <RotateCw className="size-4" aria-hidden /> Try again
      </button>
    </Card>
  );
}
