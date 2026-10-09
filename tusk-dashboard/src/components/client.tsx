"use client";

import { Check, Copy } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition, type ComponentProps, type ReactNode } from "react";
import { useFormStatus } from "react-dom";
import type { ActionState } from "@/lib/types";
import { buttonStyles, cx } from "./ui";

export function SubmitButton({
  children,
  variant = "primary",
  className,
  pendingLabel = "Saving…",
}: {
  children: ReactNode;
  variant?: keyof typeof buttonStyles;
  className?: string;
  pendingLabel?: string;
}) {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending} className={cx(buttonStyles[variant], className)}>
      {pending ? pendingLabel : children}
    </button>
  );
}

export function FormMessage({ state }: { state: ActionState }) {
  return (
    <p aria-live="polite" className={cx("text-[13px] empty:hidden", state?.error ? "text-coral" : "text-mint")}>
      {state?.error ?? state?.message ?? ""}
    </p>
  );
}

/** Runs a bound server action from a button and shows its error inline. */
export function ActionButton({
  action,
  children,
  variant = "ghost",
  confirm,
  label,
}: {
  action: () => Promise<ActionState>;
  children: ReactNode;
  variant?: keyof typeof buttonStyles;
  confirm?: string;
  /** Accessible name for icon-only buttons. */
  label?: string;
}) {
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string>();
  return (
    <span className="inline-flex items-center gap-2">
      <button
        type="button"
        disabled={pending}
        aria-busy={pending || undefined}
        aria-label={label}
        title={label}
        className={buttonStyles[variant]}
        onClick={() => {
          if (confirm && !window.confirm(confirm)) return;
          startTransition(async () => setError((await action())?.error));
        }}
      >
        {children}
      </button>
      {error && (
        <span role="alert" className="text-xs text-coral">
          {error}
        </span>
      )}
    </span>
  );
}

export function CopyButton({
  value,
  label = "Copy",
  variant = "secondary",
}: {
  value: string;
  label?: string;
  variant?: keyof typeof buttonStyles;
}) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      className={buttonStyles[variant]}
      onClick={async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 1600);
      }}
    >
      {copied ? (
        <Check className={cx("size-4", variant === "primary" ? "text-forest-3" : "text-mint")} />
      ) : (
        <Copy className="size-4" />
      )}
      {copied ? "Copied" : label}
    </button>
  );
}

export function CountedTextarea({
  maxLength,
  defaultValue = "",
  className,
  ...props
}: ComponentProps<"textarea"> & { maxLength: number; defaultValue?: string }) {
  const [length, setLength] = useState(defaultValue.length);
  return (
    <div className="relative">
      <textarea
        {...props}
        maxLength={maxLength}
        defaultValue={defaultValue}
        onChange={(event) => setLength(event.target.value.length)}
        className={cx(className, "pb-7")}
      />
      <span className="num pointer-events-none absolute right-3 bottom-2 text-[11px] text-faint" aria-hidden>
        {length}/{maxLength}
      </span>
    </div>
  );
}

/** Re-fetches server data on an interval so chat bookings appear without reloading. */
export function AutoRefresh({ seconds = 5 }: { seconds?: number }) {
  const router = useRouter();
  useEffect(() => {
    const id = setInterval(() => {
      if (document.visibilityState === "visible") router.refresh();
    }, seconds * 1000);
    return () => clearInterval(id);
  }, [router, seconds]);
  return null;
}

function ago(iso: string): string {
  const seconds = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000));
  if (seconds < 45) return "just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return days < 30 ? `${days}d ago` : new Date(iso).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export function TimeAgo({ iso, className }: { iso: string; className?: string }) {
  const [, tick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => tick((n) => n + 1), 30_000);
    return () => clearInterval(id);
  }, []);
  return (
    <time dateTime={iso} className={className} suppressHydrationWarning>
      {ago(iso)}
    </time>
  );
}
