"use client";

import { cloneElement, createContext, isValidElement, useContext, useId, type ReactElement, type ReactNode } from "react";

/** Server-side validation errors for the enclosing form, keyed by input name. */
export const FieldErrorsContext = createContext<Record<string, string> | undefined>(undefined);

type InputProps = { name?: string; "aria-invalid"?: boolean; "aria-describedby"?: string };

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  const errors = useContext(FieldErrorsContext);
  const id = useId();
  const input = isValidElement<InputProps>(children) ? (children as ReactElement<InputProps>) : null;
  const error = input?.props.name ? errors?.[input.props.name] : undefined;
  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined;
  return (
    <label className="block">
      <span className="mb-1.5 block text-[13px] font-strong text-ink-2">{label}</span>
      {input ? cloneElement(input, { "aria-invalid": error ? true : undefined, "aria-describedby": describedBy }) : children}
      {error ? (
        <span id={`${id}-error`} className="mt-1 block text-xs text-coral">
          {error}
        </span>
      ) : (
        hint && (
          <span id={`${id}-hint`} className="mt-1 block text-xs text-muted">
            {hint}
          </span>
        )
      )}
    </label>
  );
}
