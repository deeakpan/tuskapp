import type { Metadata } from "next";
import Link from "next/link";
import { SignupForm } from "@/components/auth-forms";

export const metadata: Metadata = {
  title: "Create your business",
  description:
    "Put your salon, restaurant or clinic inside ChatGPT and Claude. Customers see your prices and book with a deposit — free to start.",
  alternates: { canonical: "/signup" },
};

export default function SignupPage() {
  return (
    <>
      <h1 className="text-[26px] font-book tracking-[-0.03em]">Create your business</h1>
      <p className="mt-1 text-sm text-muted">Five minutes from now, customers can book you from ChatGPT.</p>
      <SignupForm />
      <p className="mt-6 text-sm text-muted">
        Already on TuskApp?{" "}
        <Link href="/login?as=business" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-ink">
          Log in
        </Link>
      </p>
    </>
  );
}
