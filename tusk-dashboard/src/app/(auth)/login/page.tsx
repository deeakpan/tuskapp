import type { Metadata } from "next";
import { ArrowLeft, ChevronRight, MessageCircle, Store } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { AiLogos } from "@/components/ai-logos";
import { LoginForm } from "@/components/auth-forms";

export const metadata: Metadata = {
  title: "Log in",
  description: "Log in to TuskApp to see bookings, customers and questions from ChatGPT and Claude.",
  alternates: { canonical: "/login" },
};

async function LoginView({ searchParams }: { searchParams: PageProps<"/login">["searchParams"] }) {
  const { as } = await searchParams;
  return as === "business" ? <BusinessLogin /> : <ChooseRole />;
}

export default function LoginPage({ searchParams }: PageProps<"/login">) {
  return (
    <Suspense fallback={<div className="min-h-80" />}>
      <LoginView searchParams={searchParams} />
    </Suspense>
  );
}

function ChooseRole() {
  return (
    <>
      <h1 className="text-[26px] font-book tracking-[-0.03em]">Welcome to TuskApp</h1>
      <p className="mt-1 text-sm text-muted">How are you using TuskApp?</p>
      <div className="mt-8 grid gap-3">
        <RoleCard
          href="/connect"
          icon={<MessageCircle className="size-5" aria-hidden />}
          title="I’m a customer"
          body={
            <>
              Find and book local businesses from <AiLogos className="mx-0.5 -mt-0.5" /> ChatGPT or Claude.
            </>
          }
        />
        <RoleCard
          href="/login?as=business"
          icon={<Store className="size-5" aria-hidden />}
          title="I run a business"
          body="Log in to your dashboard, or create your business."
        />
      </div>
    </>
  );
}

function RoleCard({ href, icon, title, body }: { href: string; icon: React.ReactNode; title: string; body: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="group flex items-center gap-4 rounded-2xl border border-line bg-panel px-4 py-4 transition hover:border-forest-3 hover:bg-raised"
    >
      <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-forest-2 text-mint">{icon}</span>
      <span className="min-w-0 flex-1">
        <span className="block font-strong">{title}</span>
        <span className="mt-0.5 block text-sm text-muted">{body}</span>
      </span>
      <ChevronRight className="size-4 shrink-0 text-faint transition group-hover:translate-x-0.5 group-hover:text-ink" aria-hidden />
    </Link>
  );
}

function BusinessLogin() {
  return (
    <>
      <Link href="/login" className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink">
        <ArrowLeft className="size-4" aria-hidden /> Back
      </Link>
      <h1 className="text-[26px] font-book tracking-[-0.03em]">Welcome back</h1>
      <p className="mt-1 text-sm text-muted">Log in to manage your bookings and customers.</p>
      <LoginForm />
      <p className="mt-6 text-sm text-muted">
        New to TuskApp?{" "}
        <Link href="/signup" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-ink">
          Create your business
        </Link>
      </p>
      <p className="mt-10 rounded-xl border border-line bg-panel px-4 py-3 text-xs text-muted">
        Demo: <span className="num text-ink-2">tolu@tuskapp.demo</span> / <span className="num text-ink-2">tusk-demo-123</span>
      </p>
    </>
  );
}
