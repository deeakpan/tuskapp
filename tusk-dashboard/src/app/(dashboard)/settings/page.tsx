import type { Metadata } from "next";
import { ExternalLink, Trash2 } from "lucide-react";
import { Suspense } from "react";
import {
  revokeToken,
  updateAbout,
  updateBusiness,
  updateHours,
  updatePolicies,
  updateProfile,
} from "@/app/actions/dashboard";
import { ActionButton, CopyButton, CountedTextarea, TimeAgo } from "@/components/client";
import { ActionForm } from "@/components/forms";
import { TokenCreator } from "@/components/token-creator";
import { Card, CardHeader, Field, ListSkeleton, PageHeader, Tag, buttonStyles, inputStyles } from "@/components/ui";
import { api } from "@/lib/api";
import { getMe } from "@/lib/data";
import type { McpToken } from "@/lib/types";

export const metadata: Metadata = {
  title: "Settings",
  description: "Business details, opening hours, deposit, policies and how to connect ChatGPT and Claude.",
};

const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const ABOUT_MAX = 1000;

const ABOUT_PROMPTS = [
  "What you’re best known for",
  "Who you usually serve (brides, students, offices…)",
  "What makes you different from others nearby",
  "Occasions you’re great for",
  "What it’s like to visit: parking, Wi-Fi, kids welcome",
  "Languages you speak with customers",
];

const ALERTS = [
  { event: "Booking confirmed (deposit paid)", how: "Dashboard, email and SMS" },
  { event: "Customer question chat couldn’t answer", how: "Dashboard and email" },
  { event: "Slot held, deposit not paid yet", how: "Dashboard only" },
  { event: "Customer chatting with your assistant", how: "Never — it’s saved on their customer page" },
];

const PAYMENT_MODES = {
  test: {
    label: "Test checkout",
    detail: "Deposits open TuskApp’s practice checkout. No money moves. Add a Paystack key to take real deposits.",
  },
  "paystack-test": {
    label: "Paystack · test mode",
    detail: "Deposits go through Paystack’s test checkout. Use Paystack’s test cards; no money moves.",
  },
  "paystack-live": {
    label: "Paystack · live",
    detail: "Deposits are real card, transfer and USSD payments through Paystack.",
  },
};

async function Payments() {
  const { business } = await getMe();
  const mode = PAYMENT_MODES[business.payments];
  return (
    <Card>
      <CardHeader title="Deposits" subtitle={mode.label} />
      <p className="px-5 py-4 text-[13px] text-muted">
        {mode.detail}{" "}
        {business.deposit_naira > 0
          ? `Customers pay ₦${business.deposit_naira.toLocaleString("en-NG")} to confirm a booking.`
          : "Your deposit is ₦0, so bookings confirm without payment."}
      </p>
    </Card>
  );
}

function Alerts() {
  return (
    <Card>
      <CardHeader title="How you’re notified" subtitle="Only real orders reach your phone, so it doesn’t buzz for every chat." />
      <ul className="divide-y divide-line">
        {ALERTS.map(({ event, how }) => (
          <li key={event} className="flex flex-col gap-0.5 px-5 py-3 text-[13px] sm:flex-row sm:items-center sm:justify-between sm:gap-4">
            <span>{event}</span>
            <span className="text-muted sm:text-right">{how}</span>
          </li>
        ))}
      </ul>
      <p className="border-t border-line px-5 py-3 text-xs text-muted">
        SMS goes to the phone number on your profile. Customers reach you directly on WhatsApp, never through TuskApp.
      </p>
    </Card>
  );
}

async function Connect() {
  const [{ business }, tokens] = await Promise.all([getMe(), api<McpToken[]>("/mcp-tokens")]);
  return (
    <>
      <Card>
        <CardHeader
          title="Your public page"
          subtitle="Prices, hours, location and a WhatsApp button. Put it in your bio."
          action={
            <a href={business.profile_url} target="_blank" rel="noopener noreferrer" className={buttonStyles.ghost} aria-label="Open your public page">
              <ExternalLink className="size-4" />
            </a>
          }
        />
        <div className="flex items-center gap-2 p-5">
          <code className="num min-w-0 flex-1 truncate rounded-xl bg-panel-2 px-3 py-2.5 text-[12.5px]">
            {business.profile_url.replace(/^https?:\/\//, "")}
          </code>
          <CopyButton value={business.profile_url} />
        </div>
      </Card>
      <Card className="overflow-hidden">
        <div className="bg-gradient-to-br from-forest-3 to-forest-2 px-5 py-5">
          <div className="flex items-center gap-2">
            <span className="text-[15px] font-strong">Customer chat link</span>
            <Tag>Share anywhere</Tag>
          </div>
          <p className="mt-1 text-[13px] text-ink-2/80">
            Add this as a connector in ChatGPT or Claude. Chats start already inside {business.name}.
          </p>
          <div className="mt-4 flex items-center gap-2">
            <code className="num min-w-0 flex-1 truncate rounded-xl bg-black/30 px-3 py-2.5 text-[12.5px]">
              {business.customer_mcp_url}
            </code>
            <CopyButton value={business.customer_mcp_url} variant="primary" />
          </div>
        </div>
      </Card>
      <Card>
        <CardHeader
          title="Manage your business from ChatGPT or Claude"
          subtitle="Private, for you and your staff. Add this link as a connector and sign in with your TuskApp email and password when asked. Then ask “what’s booked tomorrow?” or “raise cornrows to ₦9,000”."
        />
        <div className="space-y-4 p-5">
          <div className="flex items-center gap-2">
            <code className="num min-w-0 flex-1 truncate rounded-xl bg-panel-2 px-3 py-2.5 text-[12.5px]">
              {business.owner_mcp_url}
            </code>
            <CopyButton value={business.owner_mcp_url} />
          </div>
          <p className="text-[13px] text-ink-2/80">
            Connected apps appear below; remove one to disconnect it. For apps without a sign-in step (Cursor, Claude
            Desktop config files), make a token instead.
          </p>
          <TokenCreator ownerUrl={business.owner_mcp_url} />
          {tokens.length > 0 && (
            <ul className="divide-y divide-line rounded-xl border border-line">
              {tokens.map((token) => (
                <li key={token.id} className="flex items-center gap-3 px-4 py-3 text-[13px]">
                  <div className="min-w-0 flex-1">
                    <p>{token.name}</p>
                    <p className="num text-xs text-muted">{token.prefix}…</p>
                  </div>
                  <span className="text-xs text-muted">
                    {token.last_used_at ? (
                      <>Used <TimeAgo iso={token.last_used_at} /></>
                    ) : (
                      "Never used"
                    )}
                  </span>
                  <ActionButton
                    action={revokeToken.bind(null, token.id)}
                    variant="danger"
                    confirm={`Revoke “${token.name}”? Anything using it will lose access.`}
                    label={`Revoke ${token.name}`}
                  >
                    <Trash2 className="size-3.5" />
                  </ActionButton>
                </li>
              ))}
            </ul>
          )}
        </div>
      </Card>
    </>
  );
}

async function BusinessForms() {
  const { user, business } = await getMe();
  const hours = new Map(business.hours.map((h) => [h.weekday, h]));
  return (
    <>
      <Card id="about" className="scroll-mt-24">
        <CardHeader
          title="About your business"
          subtitle="Chat reads this to decide who you’re the right fit for. Write it like you’d describe yourself to a new customer."
        />
        <div className="space-y-4 p-5">
          <ul className="grid gap-x-6 gap-y-1.5 text-[13px] text-muted sm:grid-cols-2">
            {ABOUT_PROMPTS.map((prompt) => (
              <li key={prompt} className="flex gap-2">
                <span className="text-mint" aria-hidden>•</span>
                {prompt}
              </li>
            ))}
          </ul>
          <ActionForm action={updateAbout} submitLabel="Save description">
            <Field label="Description" hint="Plain sentences work best. Don’t list prices here — chat takes those from Services.">
              <CountedTextarea
                name="about"
                rows={6}
                maxLength={ABOUT_MAX}
                defaultValue={business.about}
                className={`${inputStyles} h-auto py-2.5 leading-relaxed`}
                placeholder="Protective styles for natural hair, done neat and on time. Known for knotless braids that last 6–8 weeks. Popular with brides and busy professionals; quiet studio 5 minutes from Yaba bus stop."
              />
            </Field>
          </ActionForm>
        </div>
      </Card>

      <Card>
        <CardHeader title="Business" subtitle="Shown to customers in chat." />
        <div className="p-5">
          <ActionForm action={updateBusiness} submitLabel="Save business">
            <Field label="Name">
              <input name="name" required defaultValue={business.name} className={inputStyles} />
            </Field>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Category">
                <input name="category" defaultValue={business.category} className={inputStyles} />
              </Field>
              <Field label="Area">
                <input name="area" defaultValue={business.area} className={inputStyles} />
              </Field>
            </div>
            <Field label="Address">
              <input name="address" defaultValue={business.address} className={inputStyles} />
            </Field>
            <Field
              label="WhatsApp number"
              hint="When a customer needs a person — a complaint, a custom request, moving a paid booking — chat hands them a link to message you here."
            >
              <input
                name="whatsapp"
                type="tel"
                inputMode="tel"
                autoComplete="tel"
                defaultValue={business.whatsapp}
                placeholder="0803 123 4567"
                className={`${inputStyles} num`}
              />
            </Field>
            <Field label="Deposit to book (₦)" hint="0 confirms bookings straight away with no payment.">
              <input name="deposit_naira" inputMode="numeric" defaultValue={business.deposit_naira} className={`${inputStyles} num`} />
            </Field>
            <div className="grid gap-3 sm:grid-cols-2 sm:items-end">
              <label className="flex h-10 items-center gap-2.5 text-[13.5px]">
                <input type="checkbox" name="home_service" defaultChecked={business.home_service} className="accent-mint" />
                We offer home service
              </label>
              <Field label="Home service fee (₦)" hint="Added to the price when a customer asks you to come to them.">
                <input
                  name="home_service_fee_naira"
                  inputMode="numeric"
                  defaultValue={business.home_service_fee_naira}
                  className={`${inputStyles} num`}
                />
              </Field>
            </div>
            {!business.located && (business.address || business.area) && (
              <p className="text-xs text-amber">
                We couldn’t find this address on the map yet, so chat can’t tell customers how far you are. Try adding a
                landmark or street name.
              </p>
            )}
          </ActionForm>
        </div>
      </Card>

      <Card>
        <CardHeader title="Opening hours" subtitle="Chat only offers times inside these hours." />
        <div className="p-5">
          <ActionForm action={updateHours} submitLabel="Save hours">
            <div className="space-y-2">
              {WEEKDAYS.map((day, index) => {
                const h = hours.get(index);
                return (
                  <div key={day} className="grid grid-cols-[minmax(84px,110px)_1fr_1fr] items-center gap-2 text-[13.5px] sm:gap-3">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" name={`open_${index}`} defaultChecked={Boolean(h)} className="accent-mint" />
                      <span className="sm:hidden">{day.slice(0, 3)}</span>
                      <span className="hidden sm:inline">{day}</span>
                    </label>
                    <input type="time" name={`from_${index}`} aria-label={`${day} opens`} defaultValue={h?.open ?? "09:00"} className={`${inputStyles} num h-9 px-2 sm:px-3`} />
                    <input type="time" name={`to_${index}`} aria-label={`${day} closes`} defaultValue={h?.close ?? "18:00"} className={`${inputStyles} num h-9 px-2 sm:px-3`} />
                  </div>
                );
              })}
            </div>
          </ActionForm>
        </div>
      </Card>

      <Card>
        <CardHeader title="Policies & FAQs" subtitle="One per line. Chat answers questions only from these and your price list." />
        <div className="p-5">
          <ActionForm action={updatePolicies} submitLabel="Save policies">
            <textarea
              name="policies"
              rows={6}
              defaultValue={business.policies.join("\n")}
              className={`${inputStyles} h-auto py-2.5 leading-relaxed`}
              placeholder={"Home service in Yaba and Surulere only, +₦7,000.\nNo refunds for no-shows."}
            />
          </ActionForm>
        </div>
      </Card>

      <Card>
        <CardHeader title="Your profile" subtitle={user.email} />
        <div className="p-5">
          <ActionForm action={updateProfile} submitLabel="Save profile">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Name">
                <input name="name" required defaultValue={user.name} className={inputStyles} />
              </Field>
              <Field label="Phone">
                <input name="phone" required defaultValue={user.phone} className={`${inputStyles} num`} />
              </Field>
            </div>
          </ActionForm>
        </div>
      </Card>
    </>
  );
}

export default function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" subtitle="Your business details, hours and how chat apps connect to you." />
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_420px]">
        <div className="space-y-6">
          <Suspense fallback={<Card><ListSkeleton rows={6} /></Card>}>
            <BusinessForms />
          </Suspense>
        </div>
        <div className="space-y-6">
          <Suspense fallback={<Card><ListSkeleton rows={4} /></Card>}>
            <Connect />
          </Suspense>
          <Suspense fallback={<Card><ListSkeleton rows={2} /></Card>}>
            <Payments />
          </Suspense>
          <Alerts />
        </div>
      </div>
    </>
  );
}
