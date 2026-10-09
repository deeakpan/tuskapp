"use client";

import { ImagePlus } from "lucide-react";
import { useId, useState, useTransition } from "react";
import type { ActionState } from "@/lib/types";
import { cx } from "./ui";

const MAX_BYTES = 5 * 1024 * 1024;
const TYPES = ["image/jpeg", "image/png", "image/webp"];

/** A square "add photo" tile that uploads the chosen image straight away. */
export function PhotoUpload({
  action,
  label,
  className,
}: {
  action: (form: FormData) => Promise<ActionState>;
  label: string;
  className?: string;
}) {
  const id = useId();
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string>();

  function upload(file: File | undefined) {
    if (!file) return;
    if (!TYPES.includes(file.type)) return setError("Use a JPG, PNG or WebP photo.");
    if (file.size > MAX_BYTES) return setError("Photos can be up to 5MB.");
    const form = new FormData();
    form.set("photo", file);
    setError(undefined);
    startTransition(async () => setError((await action(form))?.error));
  }

  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor={id}
        aria-busy={pending || undefined}
        title={label}
        className={cx(
          "flex size-16 shrink-0 cursor-pointer items-center justify-center rounded-xl border border-dashed border-line-strong text-muted transition hover:border-faint hover:text-ink",
          pending && "animate-pulse cursor-wait",
          className,
        )}
      >
        <ImagePlus className="size-5" aria-hidden />
        <span className="sr-only">{label}</span>
      </label>
      <input
        id={id}
        type="file"
        accept={TYPES.join(",")}
        disabled={pending}
        className="sr-only"
        onChange={(event) => {
          upload(event.target.files?.[0]);
          event.target.value = "";
        }}
      />
      {error && (
        <span role="alert" className="max-w-40 text-xs text-coral">
          {error}
        </span>
      )}
    </div>
  );
}
