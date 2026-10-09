import type { ReactNode } from "react";
import { LEGAL_UPDATED } from "@/lib/site";

export function LegalPage({ title, intro, children }: { title: string; intro: ReactNode; children: ReactNode }) {
  return (
    <article className="text-[15px] leading-relaxed text-ink-2">
      <p className="text-[13px] text-muted">Last updated {LEGAL_UPDATED}</p>
      <h1 className="mt-2 text-[34px] leading-tight font-book tracking-[-0.035em] text-ink sm:text-[40px]">{title}</h1>
      <div className="mt-4 text-[16px] text-ink-2">{intro}</div>
      <div className="mt-10 space-y-10">{children}</div>
    </article>
  );
}

export function LegalSection({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section id={id} className="scroll-mt-20 space-y-3">
      <h2 className="text-[19px] font-strong tracking-[-0.02em] text-ink">{title}</h2>
      {children}
    </section>
  );
}

export function LegalList({ items }: { items: ReactNode[] }) {
  return (
    <ul className="list-disc space-y-1.5 pl-5 marker:text-faint">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}
