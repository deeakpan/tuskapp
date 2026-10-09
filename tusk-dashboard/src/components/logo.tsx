import { cx } from "./ui";

export function TuskMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="none" className={cx("size-7", className)} aria-hidden>
      <path
        d="M8 5c0 11 4.5 19 16 22-2.5-4-3.5-8.5-3.5-13.5V5"
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="13" cy="9" r="1.6" fill="currentColor" />
    </svg>
  );
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cx("inline-flex items-center gap-1.5 text-[17px] font-strong tracking-[-0.02em]", className)}>
      <TuskMark className="size-5 text-mint" />
      TUSKAPP
    </span>
  );
}
