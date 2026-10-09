"use client";

import Link from "next/link";
import { useActionState } from "react";
import { login, signup } from "@/app/actions/auth";
import { FormMessage, SubmitButton } from "./client";
import { Field, FieldErrorsContext } from "./field";
import { inputStyles } from "./ui";

const linkStyles = "text-ink underline decoration-line-strong underline-offset-4 hover:decoration-ink";

export function LoginForm() {
  const [state, action] = useActionState(login, undefined);
  return (
    <FieldErrorsContext value={state?.fieldErrors}>
      <form action={action} className="mt-8 space-y-4">
        <Field label="Email">
          <input name="email" type="email" required autoComplete="email" className={inputStyles} placeholder="you@business.com" />
        </Field>
        <Field label="Password">
          <input name="password" type="password" required autoComplete="current-password" className={inputStyles} />
        </Field>
        <FormMessage state={state} />
        <SubmitButton className="h-11 w-full" pendingLabel="Logging in…">
          Log in
        </SubmitButton>
      </form>
    </FieldErrorsContext>
  );
}

export function SignupForm() {
  const [state, action] = useActionState(signup, undefined);
  return (
    <FieldErrorsContext value={state?.fieldErrors}>
      <form action={action} className="mt-8 space-y-4">
        <Field label="Business name">
          <input name="business_name" required minLength={2} className={inputStyles} placeholder="Glam by Tolu" />
        </Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Category">
            <input name="category" className={inputStyles} placeholder="Salon" />
          </Field>
          <Field label="Area">
            <input name="area" className={inputStyles} placeholder="Yaba, Lagos" />
          </Field>
        </div>
        <Field label="Your name">
          <input name="name" required minLength={2} autoComplete="name" className={inputStyles} />
        </Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Email">
            <input name="email" type="email" required autoComplete="email" className={inputStyles} />
          </Field>
          <Field label="Phone">
            <input name="phone" type="tel" required minLength={7} autoComplete="tel" className={inputStyles} placeholder="0803…" />
          </Field>
        </div>
        <Field label="Password" hint="At least 8 characters.">
          <input name="password" type="password" required minLength={8} autoComplete="new-password" className={inputStyles} />
        </Field>
        <FormMessage state={state} />
        <SubmitButton className="h-11 w-full" pendingLabel="Creating…">
          Create business
        </SubmitButton>
        <p className="text-xs leading-relaxed text-muted">
          By creating a business you agree to our{" "}
          <Link href="/terms" className={linkStyles}>
            Terms
          </Link>{" "}
          and{" "}
          <Link href="/privacy" className={linkStyles}>
            Privacy Policy
          </Link>
          .
        </p>
      </form>
    </FieldErrorsContext>
  );
}
