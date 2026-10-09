import Link from "next/link";
import { COPYRIGHT_YEAR, SUPPORT_EMAIL } from "@/lib/site";
import { cx } from "./ui";

export function SiteFooter({ className }: { className?: string }) {
  return (
    <footer className={cx("border-t border-line", className)}>
      <div className="mx-auto flex max-w-3xl flex-wrap items-center gap-x-5 gap-y-2 px-5 py-6 text-[13px] text-muted">
        <span>© {COPYRIGHT_YEAR} TuskApp</span>
        <Link href="/privacy" className="hover:text-ink">
          Privacy
        </Link>
        <Link href="/terms" className="hover:text-ink">
          Terms
        </Link>
        <a href={`mailto:${SUPPORT_EMAIL}`} className="hover:text-ink">
          {SUPPORT_EMAIL}
        </a>
      </div>
    </footer>
  );
}
