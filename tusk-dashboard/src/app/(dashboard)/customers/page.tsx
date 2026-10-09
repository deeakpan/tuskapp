import type { Metadata } from "next";
import { ChevronRight, Mail, Phone } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { addCustomer } from "@/app/actions/dashboard";
import { TimeAgo } from "@/components/client";
import { ActionForm, CustomerFields } from "@/components/forms";
import { Avatar, Card, CardHeader, EmptyState, ListSkeleton, PageHeader, StatusPill } from "@/components/ui";
import { api } from "@/lib/api";
import type { Customer } from "@/lib/types";

export const metadata: Metadata = {
  title: "Customers",
  description: "Names, phone numbers and emails of customers who booked or asked questions in chat.",
};

async function CustomerList({ searchParams }: { searchParams: PageProps<"/customers">["searchParams"] }) {
  const { q } = await searchParams;
  const query = typeof q === "string" ? q.trim() : "";
  const customers = await api<Customer[]>(`/customers${query ? `?q=${encodeURIComponent(query)}` : ""}`);
  return (
    <Card className="overflow-hidden">
      <CardHeader
        title={query ? `Results for “${query}”` : "All customers"}
        subtitle={`${customers.length} ${customers.length === 1 ? "person" : "people"}`}
        action={query ? <Link href="/customers" className="text-[13px] text-muted hover:text-ink">Clear</Link> : null}
      />
      {customers.length === 0 ? (
        <EmptyState title={query ? "No matches" : "No customers yet"}>
          Customers are saved automatically when they book or ask a question in chat.
        </EmptyState>
      ) : (
        <ul className="divide-y divide-line">
          {customers.map((c) => (
            <li key={c.id}>
              <Link href={`/customers/${c.id}`} className="flex items-center gap-3 px-4 py-3.5 transition hover:bg-panel-2/60 sm:gap-4 sm:px-5">
                <Avatar name={c.name} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[14px]">{c.name}</p>
                  <p className="flex flex-wrap items-center gap-x-3 text-xs text-muted">
                    <span className="num flex items-center gap-1"><Phone className="size-3" />{c.phone}</span>
                    {c.email && <span className="flex items-center gap-1"><Mail className="size-3" />{c.email}</span>}
                  </p>
                </div>
                <div className="hidden text-right md:block">
                  <p className="num text-[13px]">{c.total_value}</p>
                  <p className="text-xs text-muted">{c.bookings} booking{c.bookings === 1 ? "" : "s"}</p>
                </div>
                <span className="hidden sm:block">
                  <StatusPill status={c.source} />
                </span>
                <TimeAgo iso={c.last_seen} className="hidden w-16 text-right text-xs text-faint lg:block" />
                <ChevronRight className="size-4 text-faint" />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

export default function CustomersPage({ searchParams }: PageProps<"/customers">) {
  return (
    <>
      <PageHeader
        title="Customers"
        subtitle="Names, phone numbers and emails from chat, kept in sync with what you edit here."
      />
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <Suspense fallback={<Card><ListSkeleton rows={8} /></Card>}>
          <CustomerList searchParams={searchParams} />
        </Suspense>
        <Card className="h-fit">
          <CardHeader title="Add a customer" subtitle="Walk-ins and WhatsApp regulars. Chat finds them by phone." />
          <div className="p-5">
            <ActionForm action={addCustomer} submitLabel="Save customer" resetOnSuccess>
              <CustomerFields />
            </ActionForm>
          </div>
        </Card>
      </div>
    </>
  );
}
