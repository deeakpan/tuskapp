/** A wa.me click-to-chat link for a Nigerian number (0803…, +234 803…), with `text` already typed. */
export function whatsappLink(phone: string, text = ""): string | null {
  const local = phone.replace(/\D/g, "").slice(-10);
  if (local.length < 10) return null;
  return `https://wa.me/234${local}${text ? `?text=${encodeURIComponent(text)}` : ""}`;
}
