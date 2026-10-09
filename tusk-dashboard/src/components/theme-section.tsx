"use client";

import { Moon, Sun } from "lucide-react";
import { useSyncExternalStore, type ComponentProps } from "react";
import { cx } from "./ui";

type Theme = "dark" | "light";

const STORAGE_KEY = "tusk-auth-theme";
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  window.addEventListener("storage", listener);
  return () => {
    listeners.delete(listener);
    window.removeEventListener("storage", listener);
  };
}

const readTheme = (): Theme => (localStorage.getItem(STORAGE_KEY) === "light" ? "light" : "dark");

function setTheme(theme: Theme) {
  localStorage.setItem(STORAGE_KEY, theme);
  listeners.forEach((listener) => listener());
}

/** A section with its own light/dark switch, remembered on this device. */
export function ThemeSection({ className, children, ...props }: ComponentProps<"section">) {
  const theme = useSyncExternalStore(subscribe, readTheme, () => "dark" as const);
  const next = theme === "dark" ? "light" : "dark";
  const Icon = theme === "dark" ? Sun : Moon;
  return (
    <section data-theme={theme} className={cx("relative transition-colors", className)} {...props}>
      <button
        type="button"
        onClick={() => setTheme(next)}
        aria-label={`Switch to ${next} mode`}
        title={`Switch to ${next} mode`}
        className="absolute top-5 right-5 rounded-md p-1.5 text-muted transition hover:text-ink focus-visible:ring-2 focus-visible:ring-forest-3 focus-visible:outline-none sm:top-8 sm:right-8"
      >
        <Icon className="size-[18px]" strokeWidth={1.75} aria-hidden />
      </button>
      {children}
    </section>
  );
}
