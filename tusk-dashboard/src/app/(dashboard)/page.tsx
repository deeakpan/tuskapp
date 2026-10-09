import type { Metadata } from "next";
import { ArrowUpRight } from "lucide-react";
import Link from "next/link";
import { Suspense, cache } from "react";
import { ActivityFeed } from "@/components/activity-feed";
import { Card, CardHeader, EmptyState, ListSkeleton, Skeleton, StatusPill, Tag, cx } from "@/components/ui";
import { api } from "@/lib/api";
import { getMe } from "@/lib/data";
import type { Overview } from "@/lib/types";

export const metadata: Metadata = {
  title: "Overview",
  description: "Today’s bookings, deposits collected, upcoming appointments and what customers are asking for in ChatGPT and Claude.",
};

const getOverview = cache(() => api<Overview>("/overview"));

async function Greeting() {
  const { user, business } = await getMe();
  return (
    <p className="mt-1 text-sm text-muted">
      {business.name} · {business.area || "Add your area in Settings"} · signed in as {user.name.split(" ")[0]}
    </p>
  );
}

async function SetupNudge() {
  const { business } = await getMe();
  const missing = [
    business.about.trim().length < 80 && "a description of your business, so chat can recommend you to the right customers",
    !business.whatsapp && "a WhatsApp number, so customers who need a person can reach you",
  ].filter(Boolean);
  if (missing.length === 0) return null;
  return (
    <Card className="flex flex-col gap-3 border-mint/30 p-4 sm:flex-row sm:items-center">
      <p className="flex-1 text-[13.5px] text-ink-2">Add {missing.join(" and ")}.</p>
      <Link href="/settings#about" className="flex shrink-0 items-center gap-1 text-[13px] text-mint hover:underline">
        Open settings <ArrowUpRight className="size-3.5" aria-hidden />
      </Link>
    </Card>
  );
}

async function HighlightTiles() {
  const { stats } = await getOverview();
  const tiles = [
    { title: "Bookings today", tag: "Live", value: stats.bookings_today, note: `${stats.upcoming_bookings} upcoming` },
    { title: "Customers", tag: "Synced from chat", value: stats.customers, note: "Phone + email saved" },
    { title: "Chat requests", tag: "Last 7 days", value: stats.chat_requests_7d, note: "From ChatGPT & Claude" },
  ];
  return (
    <div className="grid overflow-hidden rounded-2xl border border-line md:grid-cols-4">
      {tiles.map((tile) => (
        <div key={tile.title} className="border-b border-line bg-panel px-5 py-4 md:border-r md:border-b-0">
          <div className="flex items-center gap-2">
            <span className="text-[13.5px] font-strong">{tile.title}</span>
            <Tag>{tile.tag}</Tag>
          </div>
          <p className="num mt-2 text-[26px] text-ink">{tile.value}</p>
          <p className="text-xs text-muted">{tile.note}</p>
        </div>
      ))}
      <div className="relative bg-gradient-to-br from-forest-3 to-forest-2 px-5 py-4">
        <span className="text-[13.5px] font-strong">Deposits collected</span>
        <p className="num mt-2 text-[26px]">{stats.deposits_collected}</p>
        <p className="text-xs text-ink-2/80">{stats.awaiting_deposit} awaiting payment</p>
        <span className="absolute top-4 right-4 size-6 rounded-full bg-white" />
      </div>
    </div>
  );
}

async function Upcoming() {
  const { upcoming } = await getOverview();
  if (upcoming.length === 0) {
    return <EmptyState title="No upcoming bookings">Bookings made in ChatGPT or Claude appear here within seconds.</EmptyState>;
  }
  return (
    <ul className="divide-y divide-line">
      {upcoming.map((booking) => (
        <li key={booking.ref} className="flex items-center gap-4 px-5 py-3.5">
          <div className="w-28 shrink-0">
            <p className="text-[13.5px]">{booking.when.split(", ")[0]}</p>
            <p className="num text-xs text-muted">{booking.when.split(", ")[1]}</p>
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-[13.5px]">{booking.service}</p>
            <p className="truncate text-xs text-muted">
              {booking.customer_name} · <span className="num">{booking.customer_phone}</span>
            </p>
          </div>
          <span className="num hidden text-[13px] sm:block">{booking.total}</span>
          <StatusPill status={booking.status} />
        </li>
      ))}
    </ul>
  );
}

async function Demand() {
  const { insights } = await getOverview();
  const services = Object.entries(insights.most_asked_services);
  const days = Object.entries(insights.days_customers_asked_about);
  const max = Math.max(1, ...services.map(([, count]) => count));
  if (services.length === 0 && days.length === 0) {
    return <EmptyState title="No chat demand yet">Once customers check prices and availability, you’ll see what they want most.</EmptyState>;
  }
  return (
    <div className="space-y-5 px-5 py-4">
      <ul className="space-y-3">
        {services.map(([name, count]) => (
          <li key={name}>
            <div className="mb-1.5 flex justify-between text-[13px]">
              <span>{name}</span>
              <span className="num text-muted">{count}</span>
            </div>
            <div className="h-1.5 rounded-full bg-raised">
              <div className="h-full rounded-full bg-mint" style={{ width: `${(count / max) * 100}%` }} />
            </div>
          </li>
        ))}
      </ul>
      {days.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {days.map(([day, count]) => (
            <span key={day} className="rounded-lg bg-panel-2 px-2.5 py-1 text-xs text-ink-2">
              {day} <span className="num text-muted">×{count}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

async function Activity() {
  const { activity } = await getOverview();
  return <ActivityFeed items={activity} />;
}

function TilesSkeleton() {
  return (
    <div className="grid gap-px overflow-hidden rounded-2xl border border-line md:grid-cols-4">
      {[0, 1, 2, 3].map((i) => (
        <div key={i} className={cx("space-y-3 bg-panel px-5 py-4", i === 3 && "bg-forest-2")}>
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-6 w-16" />
          <Skeleton className="h-2.5 w-28" />
        </div>
      ))}
    </div>
  );
}

export default function OverviewPage() {
  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
      <div className="min-w-0 space-y-6">
        <div>
          <h1 className="text-[32px] leading-tight font-book tracking-[-0.035em]">Your business, inside every chat</h1>
          <Suspense fallback={<Skeleton className="mt-2 h-3.5 w-72" />}>
            <Greeting />
          </Suspense>
        </div>
        <Suspense fallback={null}>
          <SetupNudge />
        </Suspense>
        <Suspense fallback={<TilesSkeleton />}>
          <HighlightTiles />
        </Suspense>
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          <Card>
            <CardHeader
              title="Upcoming bookings"
              subtitle="Held slots expire if the deposit isn’t paid"
              action={
                <Link href="/bookings" className="flex items-center gap-1 text-[13px] text-muted hover:text-ink">
                  All <ArrowUpRight className="size-3.5" />
                </Link>
              }
            />
            <Suspense fallback={<ListSkeleton rows={5} />}>
              <Upcoming />
            </Suspense>
          </Card>
          <Card>
            <CardHeader title="What customers ask about" subtitle="From availability checks in chat" />
            <Suspense fallback={<ListSkeleton rows={4} />}>
              <Demand />
            </Suspense>
          </Card>
        </div>
      </div>
      <Card className="h-fit overflow-hidden xl:sticky xl:top-[88px]">
        <div className="grid grid-cols-2 gap-1 border-b border-line p-1.5">
          <span className="rounded-xl bg-panel-2 py-2 text-center text-[13.5px] font-strong">All activity</span>
          <Link href="/questions" className="rounded-xl py-2 text-center text-[13.5px] font-strong text-muted hover:text-ink">
            Questions
          </Link>
        </div>
        <Suspense fallback={<ListSkeleton rows={7} />}>
          <Activity />
        </Suspense>
      </Card>
    </div>
  );
}
