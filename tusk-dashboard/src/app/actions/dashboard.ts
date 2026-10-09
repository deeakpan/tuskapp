"use server";

import { refresh } from "next/cache";
import { ApiError, api } from "@/lib/api";
import type { ActionState, ImportResult, ImportState, McpToken } from "@/lib/types";

function text(form: FormData, name: string): string {
  return String(form.get(name) ?? "").trim();
}

function optionalNumber(form: FormData, name: string): number | undefined {
  const value = text(form, name).replace(/[₦,\s]/g, "");
  return value ? Number(value) : undefined;
}

async function run(call: () => Promise<unknown>, message?: string): Promise<ActionState> {
  try {
    await call();
  } catch (error) {
    if (error instanceof ApiError) return { error: error.message, fieldErrors: error.fields };
    throw error;
  }
  refresh();
  return { ok: true, message };
}

const post = (path: string, body?: unknown) =>
  api(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });
const patch = (path: string, body: unknown) => api(path, { method: "PATCH", body: JSON.stringify(body) });

// Bookings

export async function confirmBooking(ref: string): Promise<ActionState> {
  return run(() => post(`/bookings/${ref}/confirm`), "Deposit marked as paid");
}

export async function cancelBooking(ref: string): Promise<ActionState> {
  return run(() => post(`/bookings/${ref}/cancel`), "Booking cancelled");
}

// Services

export async function createService(_: ActionState, form: FormData): Promise<ActionState> {
  return run(
    () =>
      post("/services", {
        name: text(form, "name"),
        description: text(form, "description"),
        price_naira: optionalNumber(form, "price_naira"),
        duration_min: optionalNumber(form, "duration_min"),
      }),
    "Service added",
  );
}

export async function updateService(id: number, _: ActionState, form: FormData): Promise<ActionState> {
  return run(
    () =>
      patch(`/services/${id}`, {
        name: text(form, "name") || undefined,
        description: text(form, "description"),
        price_naira: optionalNumber(form, "price_naira"),
        duration_min: optionalNumber(form, "duration_min"),
      }),
    "Saved — customers in chat see this now",
  );
}

export async function setServicePublished(id: number, isPublished: boolean): Promise<ActionState> {
  return run(() => patch(`/services/${id}`, { is_published: isPublished }));
}

export async function deleteService(id: number): Promise<ActionState> {
  return run(() => api(`/services/${id}`, { method: "DELETE" }), "Service removed");
}

export async function importServices(_: ImportState, form: FormData): Promise<ImportState> {
  const file = form.get("file");
  if (!(file instanceof File) || file.size === 0) return { error: "Choose a CSV file first." };
  const body = new FormData();
  body.set("file", file);
  try {
    const result = await api<ImportResult>("/services/import", { method: "POST", body });
    refresh();
    return { result };
  } catch (error) {
    if (error instanceof ApiError) return { error: error.message };
    throw error;
  }
}

export async function uploadServicePhoto(id: number, form: FormData): Promise<ActionState> {
  const photo = form.get("photo");
  if (!(photo instanceof File) || photo.size === 0) return { error: "Choose a photo first." };
  const body = new FormData();
  body.set("photo", photo);
  return run(() => api(`/services/${id}/photos`, { method: "POST", body }), "Photo added");
}

export async function removeServicePhoto(id: number, url: string): Promise<ActionState> {
  return run(
    () => api(`/services/${id}/photos?${new URLSearchParams({ url })}`, { method: "DELETE" }),
    "Photo removed",
  );
}

// Customers

export async function addCustomer(_: ActionState, form: FormData): Promise<ActionState> {
  return run(
    () =>
      post("/customers", {
        name: text(form, "name"),
        phone: text(form, "phone"),
        email: text(form, "email") || null,
      }),
    "Customer saved",
  );
}

export async function updateCustomer(id: number, _: ActionState, form: FormData): Promise<ActionState> {
  return run(
    () =>
      patch(`/customers/${id}`, {
        name: text(form, "name"),
        phone: text(form, "phone"),
        email: text(form, "email") || null,
      }),
    "Customer updated",
  );
}

// Questions

export async function answerQuestion(id: number, _: ActionState, form: FormData): Promise<ActionState> {
  return run(
    () => post(`/enquiries/${id}/answer`, { answer: text(form, "answer"), add_to_policies: form.get("add_to_policies") === "on" }),
    "Answered",
  );
}

// Settings

export async function updateBusiness(_: ActionState, form: FormData): Promise<ActionState> {
  return run(
    () =>
      patch("/business", {
        name: text(form, "name"),
        category: text(form, "category"),
        area: text(form, "area"),
        address: text(form, "address"),
        whatsapp: text(form, "whatsapp"),
        deposit_naira: optionalNumber(form, "deposit_naira") ?? 0,
        home_service: form.get("home_service") === "on",
        home_service_fee_naira: optionalNumber(form, "home_service_fee_naira") ?? 0,
      }),
    "Business details saved",
  );
}

export async function updateAbout(_: ActionState, form: FormData): Promise<ActionState> {
  return run(() => patch("/business", { about: text(form, "about") }), "Saved — chat uses this to recommend you");
}

export async function updatePolicies(_: ActionState, form: FormData): Promise<ActionState> {
  const policies = text(form, "policies")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  return run(() => patch("/business", { policies }), "Policies saved");
}

export async function updateHours(_: ActionState, form: FormData): Promise<ActionState> {
  const hours = [0, 1, 2, 3, 4, 5, 6]
    .filter((day) => form.get(`open_${day}`) === "on")
    .map((day) => ({ weekday: day, open: text(form, `from_${day}`), close: text(form, `to_${day}`) }));
  return run(() => patch("/business", { hours }), "Opening hours saved");
}

export async function updateProfile(_: ActionState, form: FormData): Promise<ActionState> {
  return run(() => patch("/me", { name: text(form, "name"), phone: text(form, "phone") }), "Profile saved");
}

export async function createToken(_: ActionState, form: FormData): Promise<ActionState> {
  try {
    const created = await post("/mcp-tokens", { name: text(form, "token_name") || "Owner token" }) as McpToken;
    refresh();
    return { ok: true, token: created.token };
  } catch (error) {
    if (error instanceof ApiError) return { error: error.message, fieldErrors: error.fields };
    throw error;
  }
}

export async function revokeToken(id: number): Promise<ActionState> {
  return run(() => api(`/mcp-tokens/${id}`, { method: "DELETE" }), "Token revoked");
}

// Notifications

export async function markNotificationsRead(): Promise<ActionState> {
  return run(() => api("/notifications/mark-all?status=true", { method: "PATCH" }));
}
