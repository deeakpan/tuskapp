import { ArrowLeft, MessageCircle } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { updateCustomer } from "@/app/actions/dashboard";
import { TimeAgo } from "@/components/client";
import { ActionForm, CustomerFields } from "@/components/forms";
import { Avatar, Card, CardHeader, EmptyState, ListSkeleton, Skeleton, StatusPill, buttonStyles, cx } from "@/components/ui";
import { ApiError } from "@/lib/api";
import { getCustomer } from "@/lib/data";
import { utc } from "@/lib/time";
import type { CustomerDetail } from "@/lib/types";
import { whatsappLink } from "@/lib/whatsapp";

async function loadCustomer(id: string): Promise<CustomerDetail> {
  if (!/^\d+$/.test(id)) notFound();
  try {
    return await getCustomer(Number(id));
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: PageProps<"/customers/[id]">): Promise<Metadata> {
  const customer = await loadCustomer((await params).id);
  return {
    title: customer.name,
    description: `${customer.name}’s bookings, conversation with your assistant and questions they asked.`,
  };
}

async function Detail({ params }: { params: PageProps<"/customers/[id]">["params"] }) {
  const customer = await loadCustomer((await params).id);
  const whatsapp = whatsappLink(customer.phone, `Hi ${customer.name.split(" ")[0]}, `);

  return (
    <>
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <Avatar name={customer.name} className="size-12 rounded-2xl text-sm" />
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-[24px] leading-tight font-book tracking-[-0.03em] sm:text-[28px]">{customer.name}</h1>
          <p className="flex items-center gap-2 text-sm text-muted">
            <StatusPill status={customer.source} /> First seen <TimeAgo iso={customer.first_seen} />
          </p>
        </div>
        {whatsapp && (
          <a href={whatsapp} target="_blank" rel="noopener noreferrer" className={buttonStyles.secondary}>
            <MessageCircle className="size-4" aria-hidden /> Message on WhatsApp
          </a>
        )}
      </div>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-px overflow-hidden rounded-2xl border border-line bg-line">
            {[
              ["Bookings", customer.bookings],
              ["Confirmed", customer.confirmed_bookings],
              ["Confirmed value", customer.total_value],
            ].map(([label, value]) => (
              <div key={label} className="bg-panel px-5 py-4">
                <p className="text-xs text-muted">{label}</p>
                <p className="num mt-1 text-xl">{value}</p>
              </div>
            ))}
          </div>
          <Card>
            <CardHeader title="Bookings" />
            {customer.booking_history.length === 0 ? (
              <EmptyState title="No bookings yet" />
            ) : (
              <ul className="divide-y divide-line">
                {customer.booking_history.map((b) => (
                  <li key={b.ref} className="flex items-center gap-4 px-5 py-3.5 text-[13.5px]">
                    <span className="num w-20 text-ink-2">{b.ref}</span>
                    <span className="flex-1">{b.service}</span>
                    <span className="text-muted">{b.when}</span>
                    <span className="num">{b.total}</span>
                    <StatusPill status={b.status} />
                  </li>
                ))}
              </ul>
            )}
          </Card>
          <Card>
            <CardHeader
              title="Conversation with your assistant"
              subtitle="A read-only record of what they asked in ChatGPT or Claude. To talk to them yourself, use WhatsApp."
            />
            {customer.chat.length === 0 ? (
              <EmptyState title="No conversation yet" />
            ) : (
              <ul className="max-h-[480px] space-y-3 overflow-y-auto p-5">
                {customer.chat.map((m) => (
                  <li key={m.id} className={cx("flex flex-col", m.from === "customer" ? "items-end" : "items-start")}>
                    <p
                      className={cx(
                        "max-w-[80%] rounded-2xl px-3.5 py-2 text-[13.5px] leading-relaxed",
                        m.from === "customer" ? "rounded-br-md bg-mint/15 text-ink" : "rounded-bl-md bg-raised text-ink-2",
                      )}
                    >
                      {m.text}
                    </p>
                    <span className="mt-1 text-[11px] text-faint">
                      {m.from === "customer" ? customer.name : "Assistant"} · <TimeAgo iso={utc(m.at)} />
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
          <Card>
            <CardHeader title="Questions asked in chat" />
            {customer.questions.length === 0 ? (
              <EmptyState title="No questions" />
            ) : (
              <ul className="divide-y divide-line">
                {customer.questions.map((q) => (
                  <li key={q.id} className="px-5 py-3.5 text-[13.5px]">
                    <div className="flex items-center justify-between gap-4">
                      <span>{q.question}</span>
                      <StatusPill status={q.status} />
                    </div>
                    {q.answer && <p className="mt-1 text-muted">↳ {q.answer}</p>}
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
        <Card className="h-fit">
          <CardHeader title="Contact details" subtitle="Changes apply to chat too — they look up bookings by this phone." />
          <div className="p-5">
            <ActionForm action={updateCustomer.bind(null, customer.id)} submitLabel="Save changes">
              <CustomerFields customer={customer} />
            </ActionForm>
          </div>
        </Card>
      </div>
    </>
  );
}

export default function CustomerPage({ params }: PageProps<"/customers/[id]">) {
  return (
    <>
      <Link href="/customers" className="mb-5 inline-flex items-center gap-1.5 text-[13px] text-muted hover:text-ink">
        <ArrowLeft className="size-3.5" /> Customers
      </Link>
      <Suspense
        fallback={
          <>
            <Skeleton className="mb-6 h-12 w-72" />
            <Card><ListSkeleton rows={5} /></Card>
          </>
        }
      >
        <Detail params={params} />
      </Suspense>
    </>
  );
}
