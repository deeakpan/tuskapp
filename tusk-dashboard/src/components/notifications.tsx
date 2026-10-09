import { Bell } from "lucide-react";
import { markNotificationsRead } from "@/app/actions/dashboard";
import { ActionButton, TimeAgo } from "@/components/client";
import { cx } from "@/components/ui";
import { api } from "@/lib/api";
import { utc } from "@/lib/time";
import type { Notification } from "@/lib/types";

export async function Notifications() {
  const items = (await api<Notification[]>("/notifications/?limit=50")).sort((a, b) => b.id - a.id);
  const unread = items.filter((n) => !n.is_read).length;
  return (
    <details className="group relative">
      <summary
        className="relative flex size-9 cursor-pointer list-none items-center justify-center rounded-full border border-line bg-panel text-muted hover:text-ink [&::-webkit-details-marker]:hidden"
        title="Notifications"
        aria-label={unread > 0 ? `Notifications, ${unread} unread` : "Notifications"}
      >
        <Bell className="size-4" aria-hidden />
        {unread > 0 && (
          <span className="num absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-mint px-1 text-[10px] text-forest-3">
            {unread}
          </span>
        )}
      </summary>
      <div className="fixed inset-x-3 top-16 z-30 overflow-hidden rounded-2xl border border-line bg-panel shadow-2xl sm:absolute sm:inset-x-auto sm:top-auto sm:right-0 sm:mt-2 sm:w-[360px]">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <p className="text-[13px] font-strong">Notifications</p>
          {unread > 0 && <ActionButton action={markNotificationsRead}>Mark all read</ActionButton>}
        </div>
        {items.length === 0 ? (
          <p className="px-4 py-8 text-center text-[13px] text-muted">New bookings, deposits and questions show up here.</p>
        ) : (
          <ul className="max-h-[420px] divide-y divide-line overflow-y-auto">
            {items.map((n) => (
              <li key={n.id} className={cx("px-4 py-3 text-[13px]", !n.is_read && "bg-white/[0.03]")}>
                <div className="flex items-center justify-between gap-3">
                  <span className={cx("font-strong", n.is_read && "text-ink-2")}>{n.notification.title}</span>
                  <TimeAgo iso={utc(n.notification.created_at)} className="shrink-0 text-[11px] text-faint" />
                </div>
                <p className="mt-0.5 text-muted">{n.notification.message}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </details>
  );
}
