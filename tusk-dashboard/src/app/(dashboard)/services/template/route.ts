import { publicApiUrl } from "@/lib/api";

export async function GET() {
  const response = await fetch(`${publicApiUrl}/api/v1/services/import/template`, { cache: "no-store" });
  return new Response(await response.text(), {
    status: response.status,
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="tuskapp-price-list.csv"',
    },
  });
}
