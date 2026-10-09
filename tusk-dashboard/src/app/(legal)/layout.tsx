import Link from "next/link";
import { Wordmark } from "@/components/logo";
import { SiteFooter } from "@/components/site-footer";

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-line">
        <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-5">
          <Link href="/" aria-label="TuskApp home">
            <Wordmark />
          </Link>
          <Link href="/login" className="text-sm text-muted hover:text-ink">
            Log in
          </Link>
        </div>
      </header>
      <main className="mx-auto w-full max-w-3xl flex-1 px-5 py-10 sm:py-14">{children}</main>
      <SiteFooter />
    </div>
  );
}
