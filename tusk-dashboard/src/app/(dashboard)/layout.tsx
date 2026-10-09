import { LogOut, Search } from "lucide-react";
import type { Metadata } from "next";
import { Suspense } from "react";
import { logout } from "@/app/actions/auth";
import { AutoRefresh, CopyButton } from "@/components/client";
import { Wordmark } from "@/components/logo";
import { Notifications } from "@/components/notifications";
import { MobileNav, RailCopyLink, Sidebar } from "@/components/sidebar";
import { Avatar, Skeleton } from "@/components/ui";
import { getMe } from "@/lib/data";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

async function AccountActions() {
  const { user, business } = await getMe();
  return (
    <div className="flex items-center gap-2 sm:gap-3">
      <span className="hidden sm:block">
        <CopyButton value={business.customer_mcp_url} label="Copy MCP link" variant="primary" />
      </span>
      <div className="flex items-center gap-2.5 rounded-full border border-line bg-panel py-1 pr-1 pl-1">
        <Avatar name={business.name} className="size-7 rounded-full text-[10px]" />
        <div className="hidden pr-1 leading-tight lg:block">
          <p className="text-[13px] font-strong">{business.name}</p>
          <p className="text-[11px] text-muted">{user.email}</p>
        </div>
        <form action={logout}>
          <button
            className="flex size-7 items-center justify-center rounded-full text-muted hover:bg-raised hover:text-ink"
            title="Log out"
            aria-label="Log out"
          >
            <LogOut className="size-3.5" aria-hidden />
          </button>
        </form>
      </div>
    </div>
  );
}

async function SidebarChatLink() {
  const { business } = await getMe();
  return <RailCopyLink value={business.customer_mcp_url} />;
}

async function StatusLink() {
  const { business } = await getMe();
  return <span className="num truncate text-muted">{business.customer_mcp_url}</span>;
}

function SearchBox({ className }: { className?: string }) {
  return (
    <form action="/customers" role="search" className={className}>
      <label className="relative block">
        <span className="sr-only">Search customers</span>
        <Search className="pointer-events-none absolute top-1/2 left-4 size-4 -translate-y-1/2 text-faint" aria-hidden />
        <input
          name="q"
          type="search"
          placeholder="Search customers by name, phone or email"
          className="h-10 w-full rounded-xl border border-line bg-panel pr-12 pl-11 text-sm outline-none placeholder:text-faint focus:border-line-strong"
        />
        <kbd className="absolute top-1/2 right-3 hidden -translate-y-1/2 rounded-md border border-line-strong px-1.5 text-[11px] text-muted sm:block">
          ↵
        </kbd>
      </label>
    </form>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar
        footer={
          <Suspense fallback={<Skeleton className="h-14 w-full rounded-xl bg-white/5" />}>
            <SidebarChatLink />
          </Suspense>
        }
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 border-b border-line bg-bg/90 backdrop-blur">
          <div className="flex h-14 items-center gap-3 px-4 sm:h-16 sm:gap-6 sm:px-6">
            <Wordmark className="md:hidden" />
            <SearchBox className="mx-auto hidden w-full max-w-xl md:block" />
            <div className="ml-auto flex items-center gap-2 sm:gap-3 md:ml-0">
              <Suspense fallback={<Skeleton className="size-9 rounded-full" />}>
                <Notifications />
              </Suspense>
              <Suspense fallback={<Skeleton className="h-9 w-24 rounded-full sm:w-64" />}>
                <AccountActions />
              </Suspense>
            </div>
          </div>
          <SearchBox className="px-4 pb-3 md:hidden" />
        </header>

        <main className="flex-1 px-4 pt-5 pb-28 sm:px-6 sm:pt-7 md:pb-7 lg:px-8">{children}</main>

        <footer className="sticky bottom-0 hidden h-8 items-center gap-4 border-t border-line bg-bg/95 px-6 text-[11.5px] md:flex">
          <span className="flex items-center gap-1.5 text-ink-2">
            <span className="live-dot size-1.5 rounded-full bg-mint" aria-hidden />
            Live sync
          </span>
          <span className="text-faint" aria-hidden>·</span>
          <span className="text-muted">Customer MCP</span>
          <Suspense fallback={<Skeleton className="h-2.5 w-48" />}>
            <StatusLink />
          </Suspense>
        </footer>
      </div>
      <MobileNav />
      <AutoRefresh />
    </div>
  );
}
