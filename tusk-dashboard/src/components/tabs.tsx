import Link from "next/link";
import { cx } from "./ui";

export function LinkTabs({ tabs, active }: { tabs: { href: string; label: string; key: string }[]; active: string }) {
  return (
    <div className="flex max-w-full gap-1 overflow-x-auto rounded-xl border border-line bg-panel p-1 sm:inline-flex">
      {tabs.map((tab) => (
        <Link
          key={tab.key}
          href={tab.href}
          aria-current={active === tab.key ? "page" : undefined}
          className={cx(
            "shrink-0 rounded-lg px-3 py-1.5 text-[13px] font-strong whitespace-nowrap transition",
            active === tab.key ? "bg-panel-2 text-ink" : "text-muted hover:text-ink",
          )}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );
}
