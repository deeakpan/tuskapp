import "server-only";
import { redirect } from "next/navigation";
import { getToken } from "./session";

const API_URL = process.env.TUSK_API_URL ?? "http://127.0.0.1:8100";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly fields: Record<string, string> = {},
  ) {
    super(message);
  }
}

type ValidationIssue = { loc?: (string | number)[]; msg?: string };

function humanize(message: string): string {
  return message.replace(/^Value error, /, "").replace(/^String should have at least (\d+) characters?$/, "Use at least $1 characters");
}

function fieldErrors(detail: unknown): Record<string, string> {
  if (!Array.isArray(detail)) return {};
  const fields: Record<string, string> = {};
  for (const issue of detail as ValidationIssue[]) {
    const field = issue.loc?.at(-1);
    if (typeof field === "string" && issue.msg && !fields[field]) fields[field] = humanize(issue.msg);
  }
  return fields;
}

function errorMessage(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown })?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) return "Some details need fixing — see the highlighted fields.";
  return `Request failed (${status})`;
}

export async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/v1${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        ...(typeof init.body === "string" ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init.headers,
      },
    });
  } catch {
    throw new ApiError("Can't reach the TuskApp server. Is tusk-mcp running?", 503);
  }
  if (response.status === 204) return undefined as T;
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = (body as { detail?: unknown })?.detail;
    throw new ApiError(errorMessage(body, response.status), response.status, fieldErrors(detail));
  }
  return body as T;
}

/** Calls the API as the signed-in owner; sends them to log in again if the session is gone. */
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await getToken();
  if (!token) redirect("/login");
  try {
    return await request<T>(path, init, token);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) redirect("/auth/logout");
    throw error;
  }
}

export const publicApiUrl = API_URL;
