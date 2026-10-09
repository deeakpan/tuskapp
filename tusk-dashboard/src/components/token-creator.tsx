"use client";

import { KeyRound } from "lucide-react";
import { useActionState } from "react";
import { createToken } from "@/app/actions/dashboard";
import { CopyButton, FormMessage, SubmitButton } from "./client";
import { cx, inputStyles } from "./ui";

export function TokenCreator({ ownerUrl }: { ownerUrl: string }) {
  const [state, action] = useActionState(createToken, undefined);
  return (
    <div className="space-y-3">
      <form action={action} className="flex items-center gap-2">
        <input
          name="token_name"
          aria-label="Token name"
          placeholder="e.g. Claude Desktop"
          autoComplete="off"
          data-1p-ignore
          data-lpignore="true"
          className={cx(inputStyles, "min-w-0 flex-1")}
        />
        <SubmitButton variant="secondary" pendingLabel="Creating…" className="h-10 shrink-0 whitespace-nowrap">
          <KeyRound className="size-4" /> New token
        </SubmitButton>
      </form>
      <FormMessage state={state?.error ? state : undefined} />
      {state?.token && (
        <div className="space-y-3 rounded-xl border border-forest-3 bg-forest/60 p-4">
          <p className="text-[13px] text-ink-2">Copy it now — it won’t be shown again.</p>
          <div className="flex items-center gap-2">
            <code className="num min-w-0 flex-1 truncate rounded-lg bg-black/30 px-3 py-2 text-[12.5px]">{state.token}</code>
            <CopyButton value={state.token} />
          </div>
          <p className="text-xs text-muted">
            In Claude or Cursor, add <span className="num text-ink-2">{ownerUrl}</span> with header{" "}
            <span className="num text-ink-2">Authorization: Bearer &lt;token&gt;</span>.
          </p>
        </div>
      )}
    </div>
  );
}
