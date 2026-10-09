import type { MetadataRoute } from "next";
import { listPublicBusinesses } from "@/lib/public";
import { SITE_URL } from "@/lib/site";

const UPDATED = new Date("2026-10-09");

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages = [
    { path: "/signup", priority: 1, changeFrequency: "monthly" as const },
    { path: "/login", priority: 0.6, changeFrequency: "monthly" as const },
    { path: "/privacy", priority: 0.3, changeFrequency: "yearly" as const },
    { path: "/terms", priority: 0.3, changeFrequency: "yearly" as const },
  ].map(({ path, ...rest }) => ({ url: `${SITE_URL}${path}`, lastModified: UPDATED, ...rest }));
  const businesses = (await listPublicBusinesses()).map((business) => ({
    url: `${SITE_URL}/${business.slug}`,
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }));
  return [...pages, ...businesses];
}
