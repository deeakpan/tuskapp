import type { Metadata } from "next";
import Link from "next/link";
import { LoginForm } from "@/components/auth-forms";

export const metadata: Metadata = {
  title: "Log in",
  description: "Log in to TuskApp to see bookings, customers and questions from ChatGPT and Claude.",
  alternates: { canonical: "/login" },
};

export default function LoginPage() {
  return (
    <>
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
