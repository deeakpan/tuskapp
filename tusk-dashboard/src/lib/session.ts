import "server-only";
import { cookies } from "next/headers";

const COOKIE = "tusk_session";
const MAX_AGE = 60 * 60 * 24 * 7;

export async function getToken(): Promise<string | undefined> {
  return (await cookies()).get(COOKIE)?.value;
}

export async function setSession(token: string) {
  (await cookies()).set(COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: MAX_AGE,
  });
}

export async function clearSession() {
  (await cookies()).delete(COOKIE);
}

export const SESSION_COOKIE = COOKIE;
