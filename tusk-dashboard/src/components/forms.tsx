"use client";

import { useActionState, useEffect, useRef } from "react";
import type { ActionState, Customer } from "@/lib/types";
import { FormMessage, SubmitButton } from "./client";
import { Field, FieldErrorsContext } from "./field";
import { inputStyles } from "./ui";

type FormAction = (state: ActionState, form: FormData) => Promise<ActionState>;

/** A form wired to a server action that shows its result and optionally clears itself on success. */
export function ActionForm({
  action,
  children,
  submitLabel,
  resetOnSuccess = false,
  className,
}: {
  action: FormAction;
  children: React.ReactNode;
  submitLabel: string;
  resetOnSuccess?: boolean;
  className?: string;
}) {
  const [state, formAction] = useActionState(action, undefined);
  const ref = useRef<HTMLFormElement>(null);
  useEffect(() => {
    if (resetOnSuccess && state?.ok) ref.current?.reset();
  }, [state, resetOnSuccess]);
  return (
    <FieldErrorsContext value={state?.fieldErrors}>
      <form ref={ref} action={formAction} className={className ?? "space-y-4"}>
        {children}
        <div className="flex flex-wrap items-center gap-3">
          <SubmitButton>{submitLabel}</SubmitButton>
          <FormMessage state={state} />
        </div>
      </form>
    </FieldErrorsContext>
  );
}

export function CustomerFields({ customer }: { customer?: Customer }) {
  return (
    <>
      <Field label="Name">
        <input name="name" required defaultValue={customer?.name} className={inputStyles} />
      </Field>
      <Field label="Phone">
        <input name="phone" type="tel" required defaultValue={customer?.phone} className={inputStyles} placeholder="0803 123 4567" />
      </Field>
      <Field label="Email">
        <input name="email" type="email" defaultValue={customer?.email ?? ""} className={inputStyles} placeholder="Optional" />
      </Field>
    </>
  );
}
