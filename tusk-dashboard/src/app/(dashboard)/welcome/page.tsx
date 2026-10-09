import { ArrowRight, CalendarClock, MessagesSquare, NotebookPen, Tags } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { ChatPhones } from "@/components/chat-phones";
import { Suspense } from "react";
import { CopyButton } from "@/components/client";
import { Card, Skeleton, buttonStyles } from "@/components/ui";
import { getMe } from "@/lib/data";
export const metadata: Metadata = {
  title: "Thanks for joining",
  description: "Your TuskApp business is ready. Add your services, set your hours and share your chat link.",
};

const STEPS = [
  {
    icon: NotebookPen,
    title: "Describe your business",
    body: "What you’re known for and who you serve. Chat uses it to recommend you to the right customers.",
    href: "/settings#about",
    cta: "Write description",
  },
  {
    icon: Tags,
    title: "Add your price list",
    body: "Customers in chat only ever see prices from here — never made-up ones.",
    href: "/services",
    cta: "Add services",
  },
  {
    icon: CalendarClock,
    title: "Set hours, deposit and WhatsApp",
    body: "Chat only offers times you’re open, holds slots until the deposit is paid, and sends customers to your WhatsApp when they need you.",
    href: "/settings",
    cta: "Open settings",
  },
  {
    icon: MessagesSquare,
    title: "Share your chat link",
    body: "Add it as a connector in ChatGPT or Claude, or post it on your Instagram and WhatsApp status.",
    href: "/settings",
    cta: "Connect apps",
  },
];

async function Greeting() {
  const { user, business } = await getMe();
  return (
    <>
      <h1 className="text-[32px] leading-tight font-book tracking-[-0.035em] sm:text-[38px]">
        Thanks for joining, {user.name.split(" ")[0]}.
      </h1>
      <p className="mt-2 text-[15px] text-muted">
        {business.name} is set up. A few quick steps and customers can book you from chat.
      </p>
      <Card className="mt-6 overflow-hidden">
        <div className="flex flex-col gap-3 bg-gradient-to-br from-forest-3 to-forest-2 p-5 sm:flex-row sm:items-center">
          <div className="min-w-0 flex-1">
            <p className="text-[13px] font-strong">Your customer chat link</p>
            <code className="num mt-1 block truncate text-[12.5px] text-ink-2">{business.customer_mcp_url}</code>
          </div>
          <CopyButton value={business.customer_mcp_url} label="Copy link" variant="primary" />
        </div>
        <div className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center">
          <div className="min-w-0 flex-1">
            <p className="text-[13px] font-strong">Your public page</p>
            <a
              href={business.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="num mt-1 block truncate text-[12.5px] text-ink-2 hover:text-ink"
            >
              {business.profile_url.replace(/^https?:\/\//, "")}
            </a>
          </div>
          <CopyButton value={business.profile_url} label="Copy link" />
        </div>
      </Card>
    </>
  );
}

export default function WelcomePage() {
  return (
    <div className="mx-auto max-w-3xl py-4">
      <Suspense
        fallback={
          <>
            <Skeleton className="h-9 w-80 max-w-full" />
            <Skeleton className="mt-3 h-4 w-96 max-w-full" />
            <Skeleton className="mt-6 h-20 w-full rounded-2xl" />
          </>
        }
      >
        <Greeting />
      </Suspense>
      <ol className="mt-8 grid gap-4 sm:grid-cols-2">
        {STEPS.map(({ icon: Icon, title, body, href, cta }, i) => (
          <li key={title}>
            <Card className="flex h-full flex-col p-5">
              <div className="flex items-center gap-2">
                <span className="num flex size-7 items-center justify-center rounded-lg bg-forest-2 text-xs text-mint">
                  {i + 1}
                </span>
                <Icon className="size-4 text-muted" aria-hidden />
              </div>
              <h2 className="mt-4 text-[15px] font-strong">{title}</h2>
              <p className="mt-1 flex-1 text-[13px] leading-relaxed text-muted">{body}</p>
              <Link href={href} className={`${buttonStyles.secondary} mt-5 w-fit`}>
                {cta} <ArrowRight className="size-3.5" aria-hidden />
              </Link>
            </Card>
          </li>
        ))}
      </ol>
      <figure className="mt-8">
        <h2 className="text-[15px] font-strong">What your customers see</h2>
        <p className="mt-1 text-[13px] text-muted">
          A phone vendor in Uyo: recommended in Claude, reserved in ChatGPT.
        </p>
        <div className="mt-4 rounded-2xl border border-line bg-[#0d120f] px-4 py-8">
          <ChatPhones />
        </div>
      </figure>
      <Link href="/" className="mt-8 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink">
        Skip to your dashboard <ArrowRight className="size-3.5" aria-hidden />
      </Link>
    </div>
  );
}
