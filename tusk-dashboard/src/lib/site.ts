export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000").replace(/\/$/, "");
export const SITE_NAME = "TuskApp";
export const SITE_TAGLINE = "Your business, inside every chat";
export const SITE_DESCRIPTION =
  "TuskApp lets customers find, price and book your business from ChatGPT and Claude, and keeps every booking, phone number and email in one dashboard.";
export const SUPPORT_EMAIL = "hello@tuskapp.app";
export const LEGAL_UPDATED = "9 October 2026";
export const COPYRIGHT_YEAR = LEGAL_UPDATED.slice(-4);
export const CONSENT_COOKIE = "tusk_cookie_consent";
export const CLAUDE_PREVIEW_ALT =
  "The Claude app on an iPhone: asked where to buy a trustworthy UK-used iPhone 13 Pro in Uyo, Claude recommends Gadget Hub Uyo via TuskApp for tested phones and a 3-month warranty, iPhone 13 Pro 128GB at ₦450,000.";
export const CHATGPT_PREVIEW_ALT =
  "The ChatGPT app on an iPhone: a customer asks for a UK-used iPhone 13 Pro 128GB in Uyo, gets Gadget Hub Uyo’s ₦450,000 listing through TuskApp, and reserves it for Saturday 2pm with a ₦20,000 deposit, ref GHU-0412.";
