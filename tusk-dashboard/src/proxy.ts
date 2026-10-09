import { NextResponse, type NextRequest } from "next/server";

const SESSION_COOKIE = "tusk_session";
const AUTH_PATHS = ["/login", "/signup"];
/** Owner-only areas. Every other path (legal pages, business profiles like /glam-by-tolu) is public. */
const DASHBOARD_PREFIXES = ["/bookings", "/customers", "/services", "/questions", "/settings", "/welcome"];

const isDashboard = (pathname: string) =>
  pathname === "/" || DASHBOARD_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const signedIn = request.cookies.has(SESSION_COOKIE);

  if (!signedIn && isDashboard(pathname)) {
    return NextResponse.redirect(new URL("/login?as=business", request.url));
  }
  if (signedIn && AUTH_PATHS.includes(pathname)) {
    return NextResponse.redirect(new URL("/", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!auth/logout|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|ico|txt|xml)$).*)"],
};
