"use client";

import { Download, FileSpreadsheet } from "lucide-react";
import { useActionState } from "react";
import { importServices } from "@/app/actions/dashboard";
import { SubmitButton } from "./client";
import { buttonStyles, cx, inputStyles } from "./ui";

/** Upload a CSV price list; shows what was added, updated and which rows need fixing. */
export function CatalogueImport() {
  const [state, action] = useActionState(importServices, undefined);
  const result = state?.result;
  return (
    <form action={action} className="space-y-3">
      <p className="text-[13px] text-muted">
        Have a price list in Excel or Google Sheets? Save it as CSV with columns <b className="text-ink-2">name</b>,{" "}
        <b className="text-ink-2">price</b> and optionally duration, description and published. Items with the same
        name are updated, not duplicated.
      </p>
      <input
        type="file"
        name="file"
        required
        accept=".csv,text/csv"
        aria-label="Price list CSV"
        className={cx(
          inputStyles,
          "h-auto py-2 file:mr-3 file:rounded-full file:border-0 file:bg-raised file:px-3 file:py-1 file:text-[13px] file:text-ink",
        )}
      />
      <div className="flex flex-wrap items-center gap-2">
        <SubmitButton pendingLabel="Importing…">
          <FileSpreadsheet className="size-4" /> Import
        </SubmitButton>
        <a href="/services/template" download className={buttonStyles.ghost}>
          <Download className="size-3.5" /> Template
        </a>
      </div>
      <div aria-live="polite" className="space-y-1.5 text-[13px]">
        {state?.error && <p className="text-coral">{state.error}</p>}
        {result && (
          <p className="text-mint">
            {result.created.length} added, {result.updated.length} updated
            {result.errors.length > 0 && `, ${result.errors.length} skipped`}.
          </p>
        )}
        {result && result.errors.length > 0 && (
          <ul className="space-y-0.5 text-xs text-coral">
            {result.errors.map((error) => (
              <li key={error.row}>
                Row {error.row}
                {error.name && ` (${error.name})`}: {error.message}
              </li>
            ))}
          </ul>
        )}
      </div>
    </form>
  );
}
