import type { ComponentProps, ReactNode } from "react";

export { Field } from "./field";

export function cx(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

export const buttonStyles = {
  primary:
    "inline-flex h-9 items-center justify-center gap-2 rounded-full bg-ink px-4 text-sm font-strong text-bg transition hover:bg-ink/85 disabled:opacity-50",
  secondary:
    "inline-flex h-9 items-center justify-center gap-2 rounded-full border border-line-strong bg-panel-2 px-4 text-sm font-strong text-ink transition hover:border-faint hover:bg-raised disabled:opacity-50",
  ghost:
    "inline-flex h-8 items-center justify-center gap-1.5 rounded-lg px-2.5 text-sm text-ink-2 transition hover:bg-raised hover:text-ink disabled:opacity-50",
  photo:
    "inline-flex size-5 items-center justify-center rounded-full border border-line-strong bg-panel text-ink shadow transition hover:bg-coral hover:text-white disabled:opacity-50",
  danger:
    "inline-flex h-8 items-center justify-center gap-1.5 rounded-lg px-2.5 text-sm text-coral transition hover:bg-coral/10 disabled:opacity-50",
  forest:
    "inline-flex h-9 items-center justify-center gap-2 rounded-full bg-forest-3 px-4 text-sm font-strong text-ink transition hover:bg-[#25593f] disabled:opacity-50",
};

export const inputStyles =
  "h-10 w-full rounded-xl border border-line bg-panel-2 px-3 text-sm text-ink placeholder:text-faint outline-none transition focus:border-forest-3 focus:ring-2 focus:ring-forest-3/40 user-invalid:border-coral user-invalid:ring-coral/30 aria-invalid:border-coral aria-invalid:ring-2 aria-invalid:ring-coral/30";

export function Card({ className, ...props }: ComponentProps<"div">) {
  return <div className={cx("rounded-2xl border border-line bg-panel", className)} {...props} />;
}

export function CardHeader({ title, subtitle, action }: { title: ReactNode; subtitle?: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-line px-5 py-4">
      <div>
        <h2 className="text-[15px] font-strong text-ink">{title}</h2>
        {subtitle && <p className="mt-0.5 text-[13px] text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-[30px] leading-tight font-book tracking-[-0.03em] text-ink">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  confirmed: "bg-mint/12 text-mint",
  held: "bg-amber/12 text-amber",
  cancelled: "bg-coral/12 text-coral",
  expired: "bg-raised text-muted",
  open: "bg-amber/12 text-amber",
  answered: "bg-mint/12 text-mint",
  chat: "bg-sky/12 text-sky",
  dashboard: "bg-raised text-ink-2",
  ok: "bg-sky/12 text-sky",
  error: "bg-coral/12 text-coral",
};

const STATUS_LABELS: Record<string, string> = {
  held: "Awaiting deposit",
  confirmed: "Confirmed",
  cancelled: "Cancelled",
  expired: "Expired",
  open: "Needs answer",
  answered: "Answered",
  chat: "From chat",
  dashboard: "Added here",
};

export function StatusPill({ status, label }: { status: string; label?: string }) {
  return (
    <span
      className={cx(
        "inline-flex h-6 items-center rounded-full px-2.5 text-xs font-strong whitespace-nowrap",
        STATUS_STYLES[status] ?? "bg-raised text-ink-2",
      )}
    >
      {label ?? STATUS_LABELS[status] ?? status}
    </span>
  );
}

export function Tag({ children, tone = "mint" }: { children: ReactNode; tone?: "mint" | "muted" }) {
  return (
    <span
      className={cx(
        "text-[10px] font-strong tracking-[0.08em] uppercase",
        tone === "mint" ? "text-mint" : "text-muted",
      )}
    >
      {children}
    </span>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx("skeleton", className)} />;
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-14 text-center">
      <div className="mb-3 size-10 rounded-full border border-dashed border-line-strong" />
      <p className="text-sm font-strong text-ink">{title}</p>
      {children && <div className="mt-1 max-w-sm text-[13px] text-muted">{children}</div>}
    </div>
  );
}

export function Avatar({ name, className }: { name: string; className?: string }) {
  const letters = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]!.toUpperCase())
    .join("");
  return (
    <div
      className={cx(
        "flex size-9 shrink-0 items-center justify-center rounded-xl bg-forest-2 text-xs font-strong text-mint",
        className,
      )}
    >
      {letters || "?"}
    </div>
  );
}

export function ListSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="divide-y divide-line">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="flex items-center gap-3 px-5 py-3.5">
          <Skeleton className="size-9 rounded-xl" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3 w-1/3" />
            <Skeleton className="h-2.5 w-1/2" />
          </div>
          <Skeleton className="h-3 w-16" />
        </div>
      ))}
    </div>
  );
}
