import Image, { type StaticImageData } from "next/image";
import chatgptScreen from "@/assets/chatgpt-uyo.jpg";
import claudeScreen from "@/assets/claude-uyo.jpg";
import { CHATGPT_PREVIEW_ALT, CLAUDE_PREVIEW_ALT } from "@/lib/site";
import { cx } from "./ui";

/** An iPhone 13 Pro shell (graphite frame, notch) around a 9:16 screen image. Position it via `className`. */
function Phone({
  screen,
  alt,
  className,
  priority,
  sizes,
}: {
  screen: StaticImageData;
  alt: string;
  className?: string;
  priority?: boolean;
  sizes: string;
}) {
  return (
    <div
      className={cx(
        "rounded-[44px] bg-gradient-to-b from-[#4a4d52] via-[#2b2d30] to-[#3a3c40] p-[3px] shadow-[0_40px_90px_-25px_rgba(0,0,0,0.9)]",
        className,
      )}
    >
      <span className="absolute top-[22%] -left-[2px] h-[7%] w-[3px] rounded-l bg-[#3a3c40]" aria-hidden />
      <span className="absolute top-[31%] -left-[2px] h-[7%] w-[3px] rounded-l bg-[#3a3c40]" aria-hidden />
      <span className="absolute top-[26%] -right-[2px] h-[11%] w-[3px] rounded-r bg-[#3a3c40]" aria-hidden />
      <div className="rounded-[41px] bg-black p-[9px]">
        <div className="relative overflow-hidden rounded-[33px] bg-white">
          <Image src={screen} alt={alt} priority={priority} placeholder="blur" sizes={sizes} className="h-auto w-full" />
          <span
            className="absolute top-0 left-1/2 h-[3.4%] w-[36%] -translate-x-1/2 rounded-b-[14px] bg-black"
            aria-hidden
          />
        </div>
      </div>
    </div>
  );
}

/** ChatGPT booking a business, in one upright phone. Position it via `className`. */
export function ChatPhone({ className, priority = false }: { className?: string; priority?: boolean }) {
  return (
    <Phone screen={chatgptScreen} alt={CHATGPT_PREVIEW_ALT} priority={priority} sizes="340px" className={className} />
  );
}

/** Claude recommending a business and ChatGPT booking it, as two overlapping phones. */
export function ChatPhones({ className, priority = false }: { className?: string; priority?: boolean }) {
  return (
    <div className={cx("relative mx-auto aspect-[20/19] w-full max-w-[540px]", className)}>
      <Phone
        screen={claudeScreen}
        alt={CLAUDE_PREVIEW_ALT}
        priority={priority}
        sizes="(min-width: 1024px) 260px, 45vw"
        className="absolute top-0 right-[2%] w-[46%] rotate-[4deg]"
      />
      <Phone
        screen={chatgptScreen}
        alt={CHATGPT_PREVIEW_ALT}
        priority={priority}
        sizes="(min-width: 1024px) 260px, 45vw"
        className="absolute top-[8%] left-[6%] z-10 w-[46%] -rotate-[3deg]"
      />
    </div>
  );
}
