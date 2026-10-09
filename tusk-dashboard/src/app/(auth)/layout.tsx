import Link from "next/link";
import { AiLogos } from "@/components/ai-logos";
import { ChatPhone } from "@/components/chat-phones";
import { Wordmark } from "@/components/logo";
import { ThemeSection } from "@/components/theme-section";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.15fr_1fr]">
      <section className="relative hidden overflow-hidden border-r border-line bg-[#0d120f] lg:flex lg:flex-col">
        <div
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(70%_55%_at_15%_0%,rgba(46,110,78,0.45),transparent_70%),radial-gradient(60%_50%_at_100%_100%,rgba(22,56,42,0.6),transparent_70%)]"
          aria-hidden
        />
        <div className="relative flex flex-1 flex-col px-12 pt-10">
          <Wordmark />
          <div className="mt-12 max-w-xl">
            <p className="text-[34px] leading-[1.06] font-book tracking-[-0.035em] xl:text-[38px]">
              Bring your business to any AI chat.
            </p>
            <p className="mt-3 text-[15px] leading-relaxed text-ink-2/75">
              Get recommended by <AiLogos className="mx-0.5 -mt-0.5" /> ChatGPT and Claude the moment customers ask, and
              booked before they leave the chat.
            </p>
          </div>
          {/* Sized from the area's height so ~90% of the phone shows and its bottom edge runs off the section. */}
          <div className="relative mt-10 min-h-[320px] flex-1 [container-type:size]">
            <ChatPhone
              priority
              className="absolute bottom-0 left-1/2 w-[min(340px,52cqh)] -translate-x-1/2 translate-y-[10%]"
            />
          </div>
        </div>
      </section>
      <ThemeSection className="flex flex-col bg-bg p-6 text-ink sm:p-12">
        <div className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center">
          <div className="mb-10 lg:hidden">
            <Wordmark />
          </div>
          {children}
        </div>
        <nav aria-label="Legal" className="mx-auto mt-10 flex gap-5 text-xs text-faint">
          <Link href="/privacy" className="hover:text-ink">
            Privacy
          </Link>
          <Link href="/terms" className="hover:text-ink">
            Terms
          </Link>
        </nav>
      </ThemeSection>
    </div>
  );
}
