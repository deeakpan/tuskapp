import { ImageResponse } from "next/og";
import { TuskMarkImage } from "@/components/brand-image";
import { SITE_NAME, SITE_TAGLINE } from "@/lib/site";

export const alt = `${SITE_NAME}: ${SITE_TAGLINE}. A customer books a salon appointment from a chat.`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const CHAT = [
  { from: "customer", text: "Knotless braids in Yaba this Saturday?" },
  { from: "assistant", text: "Glam by Tolu has 9:00am free. N35,000 · about 5 hrs." },
  { from: "customer", text: "Book 9am. I'm Ada, 0803 123 4567." },
  { from: "assistant", text: "Held — pay the N5,000 deposit to confirm. Ref GBT-0412." },
];

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          padding: 72,
          gap: 64,
          color: "#f2f2f2",
          background: "linear-gradient(135deg, #16382a 0%, #0f2a1e 55%, #0b1d15 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14, fontSize: 30, letterSpacing: -0.5 }}>
            <TuskMarkImage size={40} />
            TUSKAPP
          </div>
          <div style={{ marginTop: "auto", fontSize: 76, lineHeight: 1.02, letterSpacing: -3 }}>
            Your business, inside every chat.
          </div>
          <div style={{ marginTop: 24, fontSize: 28, color: "rgba(242,242,242,0.75)" }}>
            Bookings from ChatGPT and Claude, in one dashboard.
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 14, width: 420 }}>
          {CHAT.map((message, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignSelf: message.from === "customer" ? "flex-end" : "flex-start",
                maxWidth: 360,
                padding: "14px 20px",
                borderRadius: 22,
                fontSize: 22,
                lineHeight: 1.3,
                background: message.from === "customer" ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.3)",
                color: message.from === "customer" ? "#f2f2f2" : "#c9c9c9",
              }}
            >
              {message.text}
            </div>
          ))}
        </div>
      </div>
    ),
    size,
  );
}
