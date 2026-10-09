import "server-only";
import { notFound } from "next/navigation";
import { cache } from "react";
import { ApiError, request } from "./api";
import type { PublicBusiness, PublicBusinessSummary } from "./types";

const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export const getPublicBusiness = cache(async (slug: string): Promise<PublicBusiness> => {
  if (!SLUG.test(slug)) notFound();
  try {
    return await request<PublicBusiness>(`/public/businesses/${slug}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
});

/** Every public profile, or none when the API is unreachable (e.g. while building the sitemap). */
export async function listPublicBusinesses(): Promise<PublicBusinessSummary[]> {
  try {
    return await request<PublicBusinessSummary[]>("/public/businesses");
  } catch {
    return [];
  }
}
