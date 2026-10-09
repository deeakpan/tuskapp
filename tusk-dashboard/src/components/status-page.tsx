import Link from "next/link";
import type { ReactNode } from "react";
import { Wordmark } from "./logo";

/** Full-page message for 404s, errors and confirmations outside the dashboard shell. */
export function StatusPage({
  code,
  title,
  children,
  actions,
}: {
  code?: string;
  title: string;
  children: ReactNode;
  actions: ReactNode;
}) {
  return (
    <main className="flex min-h-screen flex-col px-5 py-6 sm:px-10">
      <Link href="/" aria-label="TuskApp home" className="w-fit">
        <Wordmark />
      </Link>
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col justify-center py-16">
        {code && <p className="num text-sm text-mint">{code}</p>}
        <h1 className="mt-2 text-[34px] leading-tight font-book tracking-[-0.035em] sm:text-[40px]">{title}</h1>
        <div className="mt-3 text-[15px] leading-relaxed text-muted">{children}</div>
        <div className="mt-8 flex flex-wrap gap-3">{actions}</div>
      </div>
    </main>
  );
}
