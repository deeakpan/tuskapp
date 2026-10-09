"use server";

import { redirect } from "next/navigation";
import { ApiError, request } from "@/lib/api";
import { clearSession, getToken, setSession } from "@/lib/session";
import type { ActionState } from "@/lib/types";

function field(form: FormData, name: string): string {
  return String(form.get(name) ?? "").trim();
}

async function startSession(path: string, body: string | URLSearchParams, next = "/"): Promise<ActionState> {
  try {
    const { access_token } = await request<{ access_token: string }>(path, { method: "POST", body });
    await setSession(access_token);
  } catch (error) {
    if (error instanceof ApiError) return { error: error.message, fieldErrors: error.fields };
    return { error: "Something went wrong. Try again." };
  }
  redirect(next);
}

export async function login(_: ActionState, form: FormData): Promise<ActionState> {
  return startSession(
    "/login",
    new URLSearchParams({ username: field(form, "email"), password: String(form.get("password") ?? "") }),
  );
}

export async function signup(_: ActionState, form: FormData): Promise<ActionState> {
  const password = String(form.get("password") ?? "");
  if (password.length < 8) {
    return { error: "Some details need fixing.", fieldErrors: { password: "Use at least 8 characters" } };
  }
  return startSession(
    "/auth/signup",
    JSON.stringify({
      name: field(form, "name"),
      email: field(form, "email"),
      phone: field(form, "phone"),
      password,
      business_name: field(form, "business_name"),
      category: field(form, "category"),
      area: field(form, "area"),
    }),
    "/welcome",
  );
}

export async function logout() {
  const token = await getToken();
  if (token) await request("/logout", { method: "DELETE" }, token).catch(() => undefined);
  await clearSession();
  redirect("/login");
}
