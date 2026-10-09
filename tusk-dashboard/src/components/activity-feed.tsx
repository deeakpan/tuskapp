"use client";

import { CalendarCheck2, MessageCircleQuestion, Sparkles } from "lucide-react";
import { useState } from "react";
import type { Activity } from "@/lib/types";
import { TimeAgo } from "./client";
import { EmptyState, StatusPill, cx } from "./ui";

const FILTERS = [
  { key: "all", label: "Feed" },
  { key: "booking", label: "Bookings" },
  { key: "question", label: "Questions" },
  { key: "chat", label: "Chat" },
] as const;

const ICONS = { booking: CalendarCheck2, question: MessageCircleQuestion, chat: Sparkles };

export function ActivityFeed({ items }: { items: Activity[] }) {
  const [filter, setFilter] = useState<(typeof FILTERS)[number]["key"]>("all");
  const shown = filter === "all" ? items : items.filter((item) => item.kind === filter);
  return (
    <>
      <div className="flex gap-1.5 px-4 pt-3 pb-2">
        {FILTERS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={cx(
              "h-7 rounded-lg px-2.5 text-[12.5px] font-strong transition",
              filter === key ? "bg-ink text-bg" : "bg-panel-2 text-ink-2 hover:bg-raised",
            )}
          >
            {label}
          </button>
        ))}
      </div>
      {shown.length === 0 ? (
        <EmptyState title="Nothing yet">Share your chat link — customer activity shows up here live.</EmptyState>
      ) : (
        <ul className="divide-y divide-line">
          {shown.map((item) => {
            const Icon = ICONS[item.kind];
            return (
              <li key={item.id} className="flex items-start gap-3 px-4 py-3">
                <div
                  className={cx(
                    "mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg",
                    item.kind === "booking" ? "bg-forest-2 text-mint" : item.kind === "question" ? "bg-amber/10 text-amber" : "bg-sky/10 text-sky",
                  )}
                >
                  <Icon className="size-4" strokeWidth={1.8} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[13.5px] text-ink">{item.title}</p>
                  <p className="truncate text-xs text-muted">{item.subtitle}</p>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1">
                  {item.amount ? <span className="num text-[13px] text-ink">{item.amount}</span> : null}
                  {item.kind !== "chat" ? <StatusPill status={item.status} /> : null}
                  <TimeAgo iso={item.at} className="text-[11px] text-faint" />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
