import { ImageResponse } from "next/og";
import { TuskMarkImage } from "@/components/brand-image";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#16382a",
        }}
      >
        <TuskMarkImage size={120} />
      </div>
    ),
    size,
  );
}
