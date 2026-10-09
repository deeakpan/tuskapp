"use client";

import { Cookie } from "lucide-react";
import Link from "next/link";
import { useSyncExternalStore } from "react";
import { CONSENT_COOKIE } from "@/lib/site";
import { buttonStyles } from "./ui";

const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

const hasChosen = () => document.cookie.split("; ").some((c) => c.startsWith(`${CONSENT_COOKIE}=`));

function choose(value: "all" | "essential") {
  const secure = location.protocol === "https:" ? "; Secure" : "";
  document.cookie = `${CONSENT_COOKIE}=${value}; Path=/; Max-Age=${60 * 60 * 24 * 365}; SameSite=Lax${secure}`;
  listeners.forEach((listener) => listener());
}

export function CookieBanner() {
  const chosen = useSyncExternalStore(subscribe, hasChosen, () => true);
  if (chosen) return null;
  return (
    <div
      role="region"
      aria-label="Cookie notice"
      className="fixed inset-x-3 bottom-20 z-50 mx-auto max-w-2xl rounded-2xl border border-line-strong bg-panel/95 p-4 shadow-2xl backdrop-blur md:bottom-12 md:inset-x-6"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <Cookie className="hidden size-5 shrink-0 text-mint sm:block" aria-hidden />
        <p className="flex-1 text-[13px] leading-relaxed text-ink-2">
          We use essential cookies to keep you signed in and remember this choice. We don’t use advertising
          cookies. See our{" "}
          <Link href="/privacy#cookies" className="text-ink underline underline-offset-4">
            privacy policy
          </Link>
          .
        </p>
        <div className="flex shrink-0 gap-2">
          <button type="button" className={buttonStyles.secondary} onClick={() => choose("essential")}>
            Essential only
          </button>
          <button type="button" className={buttonStyles.primary} onClick={() => choose("all")}>
            Accept
          </button>
        </div>
      </div>
    </div>
  );
}
