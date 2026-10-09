import type { Metadata } from "next";
import Link from "next/link";
import { LegalList, LegalPage, LegalSection } from "@/components/legal";
import { CONSENT_COOKIE, SUPPORT_EMAIL } from "@/lib/site";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description:
    "What TuskApp collects from business owners and their customers, why, who we share it with, and your rights under the Nigeria Data Protection Act 2023.",
  alternates: { canonical: "/privacy" },
};

const mail = <a href={`mailto:${SUPPORT_EMAIL}`} className="text-ink underline underline-offset-4">{SUPPORT_EMAIL}</a>;

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Privacy Policy"
      intro={
        <p>
          TuskApp lets customers find and book businesses from AI chat apps such as ChatGPT and Claude, and gives
          businesses a dashboard to manage those bookings. This policy explains what personal data we handle, why, and
          the choices you have. It follows the Nigeria Data Protection Act 2023 (NDPA).
        </p>
      }
    >
      <LegalSection id="who" title="Who we are and our roles">
        <p>
          For business owner and staff accounts, TuskApp is the data controller. For the customers of a business,
          the business is the controller and TuskApp processes that data on its behalf to run bookings, payments
          and messages. Questions about either can go to {mail}.
        </p>
      </LegalSection>

      <LegalSection id="collect" title="What we collect">
        <p>From business owners and staff:</p>
        <LegalList
          items={[
            "Name, email address, phone number and a hashed password.",
            "Business details: name, category, area, address, opening hours, deposit amount, policies and price list.",
            "Owner MCP tokens you create, and when they were last used.",
          ]}
        />
        <p>From customers who use a business through a chat app:</p>
        <LegalList
          items={[
            "Name, phone number and (optionally) email address, given in order to book or get a reply.",
            "Bookings: service, time, notes such as a home-service address, amounts and status.",
            "The messages exchanged with the TuskApp assistant about that business, and questions sent to the owner.",
            "Payment records from our payment provider (reference, amount, status). We never see or store card details.",
          ]}
        />
        <p>
          We also log which TuskApp tools a chat app called and when, to show businesses demand insights and to keep
          the service secure. We don’t receive the rest of your conversation with the chat app.
        </p>
      </LegalSection>

      <LegalSection id="use" title="Why we use it">
        <LegalList
          items={[
            "To create and hold bookings, take deposits and confirm them (performance of a contract).",
            "To let a business see and contact its customers, and answer their questions (on the business’s behalf).",
            "To send owners booking, payment and question notifications in the app and, if enabled, by email or SMS.",
            "To keep accounts secure, prevent fraud and fix problems (legitimate interests).",
            "To meet legal, tax and accounting obligations.",
          ]}
        />
        <p>We do not sell personal data, and we don’t use it for advertising.</p>
      </LegalSection>

      <LegalSection id="sharing" title="Who we share it with">
        <LegalList
          items={[
            "The business you book with, which sees your details, bookings and messages.",
            "Paystack, to process deposits.",
            "Email and SMS providers, only when a business turns those notifications on.",
            "Hosting and infrastructure providers that store data for us under contract.",
            "Authorities, where the law requires it.",
          ]}
        />
        <p>
          Chat apps such as ChatGPT and Claude receive what TuskApp’s tools return (for example a business’s prices or
          your booking status) and are covered by their own privacy policies.
        </p>
      </LegalSection>

      <LegalSection id="retention" title="How long we keep it">
        <p>
          Account and business data is kept while the account is open. Bookings, payment records and messages are kept
          for up to six years for accounting and dispute purposes, then deleted or anonymised. Logs used for security
          are kept for up to 12 months.
        </p>
      </LegalSection>

      <LegalSection id="rights" title="Your rights">
        <p>
          Under the NDPA you can ask to access, correct, delete or receive a copy of your data, object to or restrict
          some uses, and withdraw consent where we rely on it. Customers can also ask the business directly. Email{" "}
          {mail} and we’ll respond within 30 days. You can complain to the Nigeria Data Protection Commission.
        </p>
      </LegalSection>

      <LegalSection id="cookies" title="Cookies">
        <p>The dashboard uses only essential cookies:</p>
        <LegalList
          items={[
            <><span className="num text-ink">tusk_session</span> keeps you signed in. It lasts up to 7 days and is cleared when you log out.</>,
            <><span className="num text-ink">{CONSENT_COOKIE}</span> remembers your cookie choice for a year.</>,
          ]}
        />
        <p>We don’t use advertising or cross-site tracking cookies. If we ever add analytics, we’ll ask first.</p>
      </LegalSection>

      <LegalSection id="security" title="Security and transfers">
        <p>
          Passwords are hashed, access tokens can be revoked, and traffic is encrypted in transit. Some providers may
          process data outside Nigeria; where they do, we rely on safeguards permitted by the NDPA.
        </p>
      </LegalSection>

      <LegalSection id="changes" title="Changes">
        <p>
          We’ll update this page when our practices change and tell account holders about significant changes. See
          also our <Link href="/terms" className="text-ink underline underline-offset-4">Terms and Conditions</Link>.
        </p>
      </LegalSection>
    </LegalPage>
  );
}
