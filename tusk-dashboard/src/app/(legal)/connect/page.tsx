import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Suspense } from "react";
import { ChatGPTLogo, ClaudeLogo } from "@/components/ai-logos";
import { CopyButton } from "@/components/client";
import { cx } from "@/components/ui";
import { publicApiUrl } from "@/lib/api";

export const metadata: Metadata = {
  title: "Use TuskApp in ChatGPT or Claude",
  description: "Add TuskApp to ChatGPT or Claude in a minute, then find, book and pay local Nigerian businesses from chat.",
  alternates: { canonical: "/connect" },
};

type Shot = { src: string; width: number; height: number; alt: string };
type Step = { title: string; body: React.ReactNode; shot?: Shot };

const APPS = {
  chatgpt: { name: "ChatGPT", Logo: ChatGPTLogo },
  claude: { name: "Claude", Logo: ClaudeLogo },
} as const;
type AppKey = keyof typeof APPS;

const STEPS: Record<AppKey, Step[]> = {
  chatgpt: [
    {
      title: "Turn on Developer mode",
      body: (
        <>
          Open <b>Settings → Apps & Connectors → Advanced settings</b> and switch on <b>Developer mode</b>.
        </>
      ),
    },
    {
      title: "Create the TuskApp connector",
      body: (
        <>
          In <b>Apps & Connectors</b>, click <b>Create</b>. Name it TuskApp and paste the link above as the{" "}
          <b>Server URL</b>. Set <b>Authentication</b> to <b>No authentication</b>, tick{" "}
          <b>I understand and want to continue</b>, then click <b>Create</b>.
        </>
      ),
      shot: { src: "/connect/chatgpt-create.png", width: 810, height: 112, alt: "ChatGPT's Create connector form with the TuskApp link pasted as the Server URL" },
    },
    {
      title: "Switch it on in a chat",
      body: (
        <>
          Start a new chat, click <b>+ → More → TuskApp</b>. Leave <b>Web search</b> off so ChatGPT answers from
          TuskApp. It stays on for the whole chat.
        </>
      ),
    },
  ],
  claude: [
    {
      title: "Open Connectors",
      body: (
        <>
          Go to <b>Settings → Connectors</b> and click <b>Add custom connector</b>.
        </>
      ),
    },
    {
      title: "Add TuskApp",
      body: (
        <>
          Name it TuskApp, paste the link above and click <b>Add</b>. There’s nothing to sign in to.
        </>
      ),
      shot: { src: "/connect/claude-add-connector.png", width: 642, height: 318, alt: "Claude's Add custom connector form with the name TuskApp and the TuskApp link" },
    },
    {
      title: "Switch it on in a chat",
      body: (
        <>
          In a new chat, open the tools menu, make sure <b>TuskApp</b> is on and turn <b>Web search</b> off so
          Claude answers from TuskApp.
        </>
      ),
    },
  ],
};

const ASKS = [
  "I’m moving into a new apartment in Uyo. Where can I get furniture?",
  "I need a plumber in Abuja to fix a leaking pipe.",
  "Book the mahogany dining table and send me the payment link.",
  "Give me the seller’s number, I want to talk to him.",
];

export default function ConnectPage({ searchParams }: PageProps<"/connect">) {
  return (
    <article>
      <h1 className="text-[30px] leading-tight font-book tracking-[-0.03em]">Use TuskApp in your AI chat</h1>
      <p className="mt-2 text-muted">
        Add TuskApp once, then ask for anything local: furniture, a plumber, a new phone, a hair appointment. You get
        real businesses with prices and photos, and can book, pay a deposit or call the seller without leaving the chat.
      </p>
      <Suspense fallback={<div className="min-h-[60vh]" />}>
        <Guide searchParams={searchParams} />
      </Suspense>
      <p className="mt-12 border-t border-line pt-6 text-sm text-muted">
        Run a business?{" "}
        <Link href="/login?as=business" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-ink">
          Log in
        </Link>{" "}
        or{" "}
        <Link href="/signup" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-ink">
          create your business
        </Link>{" "}
        to show up here.
      </p>
    </article>
  );
}

async function Guide({ searchParams }: { searchParams: PageProps<"/connect">["searchParams"] }) {
  const { app } = await searchParams;
  const current: AppKey = app === "claude" ? "claude" : "chatgpt";
  const { name } = APPS[current];
  const link = `${publicApiUrl.replace(/\/$/, "")}/mcp/customer/`;
  const steps = STEPS[current];

  return (
    <>
      <nav aria-label="Choose your app" className="mt-8 inline-flex rounded-full border border-line bg-panel p-1">
        {(Object.keys(APPS) as AppKey[]).map((key) => {
          const { name: label, Logo } = APPS[key];
          return (
            <Link
              key={key}
              href={`/connect?app=${key}`}
              aria-current={key === current ? "page" : undefined}
              className={cx(
                "inline-flex h-9 items-center gap-2 rounded-full px-4 text-sm font-strong transition",
                key === current ? "bg-raised text-ink" : "text-muted hover:text-ink",
              )}
            >
              <Logo className="size-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <section className="mt-6 rounded-2xl border border-line bg-panel p-5">
        <p className="text-sm font-strong">Your TuskApp link</p>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <code className="num min-w-0 flex-1 truncate rounded-xl border border-line bg-panel-2 px-3 py-2 text-sm text-ink-2">
            {link}
          </code>
          <CopyButton value={link} label="Copy link" />
        </div>
      </section>

      <ol className="mt-8 grid gap-6">
        {steps.map((step, i) => (
          <li key={step.title} className="grid grid-cols-[2rem_1fr] gap-4">
            <span className="num flex size-8 items-center justify-center rounded-full bg-forest-2 text-sm font-strong text-mint">
              {i + 1}
            </span>
            <div className="min-w-0">
              <h2 className="pt-1 font-strong">{step.title}</h2>
              <p className="mt-1 text-sm leading-relaxed text-muted [&_b]:font-strong [&_b]:text-ink-2">{step.body}</p>
              {step.shot && (
                <figure className="mt-3 overflow-hidden rounded-xl border border-line bg-[#1f1f1f]">
                  <Image
                    src={step.shot.src}
                    width={step.shot.width}
                    height={step.shot.height}
                    alt={step.shot.alt}
                    sizes="(min-width: 768px) 640px, 100vw"
                    className="h-auto w-full"
                  />
                  <figcaption className="border-t border-line px-3 py-1.5 text-xs text-faint">In {name}</figcaption>
                </figure>
              )}
            </div>
          </li>
        ))}
        <li className="grid grid-cols-[2rem_1fr] gap-4">
          <span className="num flex size-8 items-center justify-center rounded-full bg-forest-2 text-sm font-strong text-mint">
            {steps.length + 1}
          </span>
          <div className="min-w-0">
            <h2 className="pt-1 font-strong">Ask away</h2>
            <p className="mt-1 text-sm text-muted">Try one of these:</p>
            <ul className="mt-3 grid gap-2">
              {ASKS.map((ask) => (
                <li key={ask} className="rounded-xl border border-line bg-panel px-3 py-2 text-sm text-ink-2">
                  “{ask}”
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-faint">
              When {name} uses TuskApp you’ll see it call TuskApp above the answer. Deposits are in Paystack test mode:
              card 4084 0840 8408 4081, CVV 408.
            </p>
          </div>
        </li>
      </ol>
    </>
  );
}
