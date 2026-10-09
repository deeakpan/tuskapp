import type { Metadata } from "next";
import { Check, X } from "lucide-react";
import { Suspense } from "react";
import { cancelBooking, confirmBooking } from "@/app/actions/dashboard";
import { ActionButton } from "@/components/client";
import { LinkTabs } from "@/components/tabs";
import { Card, EmptyState, ListSkeleton, PageHeader, StatusPill } from "@/components/ui";
import { api } from "@/lib/api";
import type { Booking } from "@/lib/types";

export const metadata: Metadata = {
  title: "Bookings",
  description: "Every booking made through chat or confirmed in the dashboard, with deposit status and customer contacts.",
};

const TABS = [
  { key: "all", label: "All" },
  { key: "held", label: "Awaiting deposit" },
  { key: "confirmed", label: "Confirmed" },
  { key: "cancelled", label: "Cancelled" },
  { key: "expired", label: "Expired" },
];

function BookingActions({ booking }: { booking: Booking }) {
  return (
    <span className="inline-flex gap-1">
      {booking.status === "held" && (
        <ActionButton action={confirmBooking.bind(null, booking.ref)}>
          <Check className="size-3.5" aria-hidden /> Mark paid
        </ActionButton>
      )}
      {(booking.status === "held" || booking.status === "confirmed") && (
        <ActionButton action={cancelBooking.bind(null, booking.ref)} variant="danger" confirm={`Cancel ${booking.ref}?`}>
          <X className="size-3.5" aria-hidden /> Cancel
        </ActionButton>
      )}
    </span>
  );
}

async function BookingTable({ searchParams }: { searchParams: PageProps<"/bookings">["searchParams"] }) {
  const { status } = await searchParams;
  const active = typeof status === "string" && TABS.some((t) => t.key === status) ? status : "all";
  const bookings = await api<Booking[]>(`/bookings${active === "all" ? "" : `?status=${active}`}`);
  const sorted = [...bookings].sort((a, b) => b.start_time.localeCompare(a.start_time));

  return (
    <>
      <LinkTabs active={active} tabs={TABS.map((t) => ({ ...t, href: t.key === "all" ? "/bookings" : `/bookings?status=${t.key}` }))} />
      <Card className="mt-4 overflow-hidden">
        {sorted.length === 0 ? (
          <EmptyState title="No bookings here">When customers book in ChatGPT or Claude, they show up instantly.</EmptyState>
        ) : (
          <>
          <ul className="divide-y divide-line md:hidden">
            {sorted.map((b) => (
              <li key={b.ref} className="space-y-2 px-4 py-3.5 text-[13.5px]">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate">{b.service}</p>
                    <p className="text-xs text-muted">
                      <span className="num">{b.ref}</span> · {b.when}
                    </p>
                  </div>
                  <StatusPill status={b.status} />
                </div>
                <p className="text-xs text-muted">
                  {b.customer_name} · <span className="num">{b.customer_phone}</span>
                </p>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="num text-[13px]">
                    {b.total} <span className="text-muted">· deposit {b.deposit}</span>
                  </span>
                  <BookingActions booking={b} />
                </div>
              </li>
            ))}
          </ul>
          <div className="hidden overflow-x-auto md:block">
            <table className="w-full text-left text-[13.5px]">
              <thead className="border-b border-line text-xs text-muted">
                <tr>
                  {["Ref", "When", "Service", "Customer", "Total", "Deposit", "Status", ""].map((h) => (
                    <th key={h} className="px-5 py-3 font-book">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {sorted.map((b) => (
                  <tr key={b.ref} className="hover:bg-panel-2/60">
                    <td className="num px-5 py-3.5 text-ink-2">{b.ref}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap">{b.when}</td>
                    <td className="px-5 py-3.5">
                      {b.service}
                      {b.notes && <p className="max-w-56 truncate text-xs text-muted">{b.notes}</p>}
                    </td>
                    <td className="px-5 py-3.5">
                      {b.customer_name}
                      <p className="num text-xs text-muted">{b.customer_phone}</p>
                      {b.customer_email && <p className="text-xs text-muted">{b.customer_email}</p>}
                    </td>
                    <td className="num px-5 py-3.5">{b.total}</td>
                    <td className="num px-5 py-3.5 text-ink-2">{b.deposit}</td>
                    <td className="px-5 py-3.5">
                      <StatusPill status={b.status} />
                    </td>
                    <td className="px-5 py-3.5 text-right whitespace-nowrap">
                      <BookingActions booking={b} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          </>
        )}
      </Card>
    </>
  );
}

export default function BookingsPage({ searchParams }: PageProps<"/bookings">) {
  return (
    <>
      <PageHeader title="Bookings" subtitle="Everything booked through chat or confirmed here, newest first." />
      <Suspense fallback={<Card><ListSkeleton rows={8} /></Card>}>
        <BookingTable searchParams={searchParams} />
      </Suspense>
    </>
  );
}
