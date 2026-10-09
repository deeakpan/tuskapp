/** The tusk mark for `ImageResponse` images (inline styles only). */
export function TuskMarkImage({ size, color = "#5fd39a" }: { size: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
      <path
        d="M8 5c0 11 4.5 19 16 22-2.5-4-3.5-8.5-3.5-13.5V5"
        stroke={color}
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="13" cy="9" r="1.6" fill={color} />
    </svg>
  );
}
