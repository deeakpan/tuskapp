"use client";

import { CalendarCheck2, Check, LayoutGrid, Link2, MessageCircleQuestion, Settings2, Tags, Users } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { type ReactNode, Suspense, useState } from "react";
import { TuskMark } from "./logo";
import { cx } from "./ui";

const NAV = [
  { href: "/", label: "Overview", icon: LayoutGrid },
  { href: "/bookings", label: "Bookings", icon: CalendarCheck2 },
  { href: "/customers", label: "Customers", icon: Users },
  { href: "/services", label: "Services", icon: Tags },
  { href: "/questions", label: "Questions", icon: MessageCircleQuestion },
  { href: "/settings", label: "Settings", icon: Settings2 },
] as const;

function isActive(pathname: string | null, href: string): boolean {
  return pathname !== null && (href === "/" ? pathname === "/" : pathname.startsWith(href));
}

function RailLinks({ pathname }: { pathname: string | null }) {
  return NAV.map(({ href, label, icon: Icon }) => {
    const active = isActive(pathname, href);
    return (
      <Link
        key={href}
        href={href}
        aria-current={active ? "page" : undefined}
        className={cx(
          "flex h-11 items-center gap-3 overflow-hidden rounded-xl border px-[13px] text-[14.5px] font-strong whitespace-nowrap transition-colors",
          active
            ? "border-white/15 bg-white/10 text-ink"
            : "border-transparent text-ink-2/75 hover:bg-white/5 hover:text-ink",
        )}
      >
        <Icon className={cx("size-[18px] shrink-0", active && "text-mint")} strokeWidth={1.8} aria-hidden />
        <span className="opacity-0 transition-opacity duration-150 group-hover/rail:opacity-100 group-focus-within/rail:opacity-100">
          {label}
        </span>
      </Link>
    );
  });
}

function ActiveRailLinks() {
  return <RailLinks pathname={usePathname()} />;
}

/** Copies the business's customer MCP URL, the link owners paste into ChatGPT or Claude as a connector. */
export function RailCopyLink({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      title={value}
      onClick={async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 1600);
      }}
      className="flex h-14 w-full items-center gap-3 overflow-hidden rounded-xl border border-white/10 px-[13px] text-left whitespace-nowrap text-ink-2/75 transition-colors hover:bg-white/5 hover:text-ink"
    >
      {copied ? (
        <Check className="size-[18px] shrink-0 text-mint" strokeWidth={1.8} aria-hidden />
      ) : (
        <Link2 className="size-[18px] shrink-0" strokeWidth={1.8} aria-hidden />
      )}
      <span className="min-w-0 leading-tight opacity-0 transition-opacity duration-150 group-hover/rail:opacity-100 group-focus-within/rail:opacity-100">
        <span className="block text-[14px] font-strong text-ink">{copied ? "Copied" : "Copy chat link"}</span>
        <span className="num block truncate text-[11px] text-muted">{value.replace(/^https?:\/\//, "")}</span>
      </span>
    </button>
  );
}

/** Icon rail that widens over the page on hover or keyboard focus. */
export function Sidebar({ footer }: { footer?: ReactNode }) {
  return (
    <div className="hidden w-[68px] shrink-0 md:block">
      <aside className="group/rail fixed inset-y-0 left-0 z-40 flex w-[68px] flex-col gap-1 overflow-hidden border-r border-forest-2 bg-gradient-to-b from-forest-2 to-forest px-2.5 py-4 transition-[width,box-shadow] duration-200 ease-out hover:w-60 hover:shadow-[12px_0_40px_rgba(0,0,0,0.45)] focus-within:w-60">
        <Link
          href="/"
          aria-label="TuskApp overview"
          className="mb-5 flex h-10 items-center gap-2.5 px-[11px] text-mint whitespace-nowrap"
        >
          <TuskMark className="size-[22px] shrink-0" />
          <span className="text-[18px] font-strong tracking-[-0.02em] text-ink opacity-0 transition-opacity duration-150 group-hover/rail:opacity-100 group-focus-within/rail:opacity-100">
            TUSKAPP
          </span>
        </Link>
        <nav aria-label="Main" className="flex flex-col gap-1">
          <Suspense fallback={<RailLinks pathname={null} />}>
            <ActiveRailLinks />
          </Suspense>
        </nav>
        {footer && <div className="mt-auto pt-4">{footer}</div>}
      </aside>
    </div>
  );
}

function TabLinks({ pathname }: { pathname: string | null }) {
  return NAV.map(({ href, label, icon: Icon }) => {
    const active = isActive(pathname, href);
    return (
      <Link
        key={href}
        href={href}
        aria-current={active ? "page" : undefined}
        className={cx(
          "flex min-w-0 flex-1 flex-col items-center gap-1 rounded-xl py-2 text-[10px] transition",
          active ? "bg-white/10 text-ink" : "text-ink-2/70 hover:bg-white/5 hover:text-ink",
        )}
      >
        <Icon className={cx("size-[18px]", active && "text-mint")} strokeWidth={1.8} aria-hidden />
        <span className="max-w-full truncate">{label}</span>
      </Link>
    );
  });
}

function ActiveTabLinks() {
  return <TabLinks pathname={usePathname()} />;
}

export function MobileNav() {
  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-30 flex gap-0.5 border-t border-forest-2 bg-forest/95 px-1.5 pt-1.5 pb-[max(0.375rem,env(safe-area-inset-bottom))] backdrop-blur md:hidden"
    >
      <Suspense fallback={<TabLinks pathname={null} />}>
        <ActiveTabLinks />
      </Suspense>
    </nav>
  );
}
