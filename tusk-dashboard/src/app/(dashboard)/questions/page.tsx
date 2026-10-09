import type { Metadata } from "next";
import { Mail, MessageCircle, Phone } from "lucide-react";
import { Suspense } from "react";
import { answerQuestion } from "@/app/actions/dashboard";
import { TimeAgo } from "@/components/client";
import { ActionForm } from "@/components/forms";
import { LinkTabs } from "@/components/tabs";
import { Card, EmptyState, ListSkeleton, PageHeader, StatusPill, inputStyles } from "@/components/ui";
import { api } from "@/lib/api";
import type { Enquiry } from "@/lib/types";
import { whatsappLink } from "@/lib/whatsapp";

export const metadata: Metadata = {
  title: "Questions",
  description: "Questions customers asked in chat that your business data couldn’t answer yet.",
};

function ReplyOnWhatsApp({
  phone,
  name,
  question,
  answer,
}: {
  phone: string;
  name: string | null;
  question: string;
  answer: string;
}) {
  const greeting = name && name !== "Customer" ? `Hi ${name.split(" ")[0]}` : "Hi";
  const href = whatsappLink(phone, `${greeting}, about your question “${question}”: ${answer}`);
  if (!href) return null;
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="mt-3 inline-flex items-center gap-1.5 text-[13px] text-mint hover:underline"
    >
      <MessageCircle className="size-3.5" aria-hidden /> Reply on WhatsApp
    </a>
  );
}

async function QuestionList({ searchParams }: { searchParams: PageProps<"/questions">["searchParams"] }) {
  const { status } = await searchParams;
  const active = status === "answered" ? "answered" : "open";
  const questions = await api<Enquiry[]>(`/enquiries?status=${active}`);
  return (
    <>
      <LinkTabs
        active={active}
        tabs={[
          { key: "open", label: "Needs answer", href: "/questions" },
          { key: "answered", label: "Answered", href: "/questions?status=answered" },
        ]}
      />
      <div className="mt-4 space-y-4">
        {questions.length === 0 && (
          <Card>
            <EmptyState title={active === "open" ? "Inbox zero" : "Nothing answered yet"}>
              When chat can’t answer from your data, the question lands here instead of being made up.
            </EmptyState>
          </Card>
        )}
        {questions.map((q) => (
          <Card key={q.id} className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[15px]">“{q.question}”</p>
                <p className="mt-1 flex flex-wrap items-center gap-x-3 text-xs text-muted">
                  <span>{q.customer_name ?? "Anonymous chat customer"}</span>
                  {q.customer_phone && <span className="num flex items-center gap-1"><Phone className="size-3" />{q.customer_phone}</span>}
                  {q.customer_email && <span className="flex items-center gap-1"><Mail className="size-3" />{q.customer_email}</span>}
                  <TimeAgo iso={q.created_at} />
                </p>
              </div>
              <StatusPill status={q.status} />
            </div>
            {q.customer_phone && (
              <ReplyOnWhatsApp phone={q.customer_phone} name={q.customer_name} question={q.question} answer={q.answer} />
            )}
            {q.status === "answered" ? (
              <p className="mt-3 rounded-xl bg-panel-2 px-4 py-3 text-[13.5px] text-ink-2">{q.answer}</p>
            ) : (
              <div className="mt-4">
                <ActionForm action={answerQuestion.bind(null, q.id)} submitLabel="Answer">
                  <textarea name="answer" required rows={2} className={`${inputStyles} h-auto py-2.5`} placeholder="Write the answer you’d give on WhatsApp…" />
                  <label className="flex items-center gap-2 text-[13px] text-ink-2">
                    <input type="checkbox" name="add_to_policies" defaultChecked className="accent-mint" />
                    Teach chat this answer for next time
                  </label>
                </ActionForm>
              </div>
            )}
          </Card>
        ))}
      </div>
    </>
  );
}

export default function QuestionsPage({ searchParams }: PageProps<"/questions">) {
  return (
    <>
      <PageHeader title="Questions" subtitle="What customers asked that your business data couldn’t answer yet." />
      <Suspense fallback={<Card><ListSkeleton rows={4} /></Card>}>
        <QuestionList searchParams={searchParams} />
      </Suspense>
    </>
  );
}
