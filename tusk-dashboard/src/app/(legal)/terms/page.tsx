import type { Metadata } from "next";
import Link from "next/link";
import { LegalList, LegalPage, LegalSection } from "@/components/legal";
import { SUPPORT_EMAIL } from "@/lib/site";

export const metadata: Metadata = {
  title: "Terms and Conditions",
  description:
    "The terms for using TuskApp: business accounts, bookings and deposits taken through chat apps, acceptable use and liability.",
  alternates: { canonical: "/terms" },
};

const link = "text-ink underline underline-offset-4";

export default function TermsPage() {
  return (
    <LegalPage
      title="Terms and Conditions"
      intro={
        <p>
          These terms apply when you create a TuskApp business account or book a business through TuskApp from a chat
          app. By using TuskApp you agree to them. If you don’t agree, please don’t use the service.
        </p>
      }
    >
      <LegalSection id="service" title="The service">
        <p>
          TuskApp connects businesses to AI chat apps such as ChatGPT and Claude. Customers can see a business’s
          services and prices, check availability, ask questions and make bookings. Businesses manage all of this in
          the TuskApp dashboard. Chat apps are run by third parties under their own terms.
        </p>
      </LegalSection>

      <LegalSection id="accounts" title="Business accounts">
        <LegalList
          items={[
            "You must give accurate details and keep your password and owner MCP tokens secret. Revoke any token you think is exposed.",
            "You’re responsible for activity on your account, including by staff you give access to.",
            "You must be at least 18 and allowed to act for the business.",
          ]}
        />
      </LegalSection>

      <LegalSection id="listings" title="Your prices, policies and answers">
        <p>
          Chat answers customers using only the prices, hours and policies you enter. You are responsible for keeping
          them accurate and lawful. Bookings are a contract between the business and the customer; TuskApp is not a
          party to that contract and doesn’t provide the services booked.
        </p>
      </LegalSection>

      <LegalSection id="deposits" title="Bookings and deposits">
        <LegalList
          items={[
            "When a business asks for a deposit, the slot is held for a limited time (usually 30 minutes) and confirmed once the deposit is paid.",
            "Deposits are processed by Paystack and subject to Paystack’s terms. TuskApp never stores card details.",
            "Refunds, cancellations and no-shows follow the business’s own policy, which chat shows before booking. Raise disputes with the business first.",
          ]}
        />
      </LegalSection>

      <LegalSection id="customers" title="Customer data">
        <p>
          You may use customer details from TuskApp only to deliver bookings, answer questions and run your business,
          in line with the Nigeria Data Protection Act 2023 and our{" "}
          <Link href="/privacy" className={link}>Privacy Policy</Link>. Don’t send marketing to customers who haven’t
          agreed to it.
        </p>
      </LegalSection>

      <LegalSection id="use" title="Acceptable use">
        <LegalList
          items={[
            "No illegal, misleading or harmful services, prices or content.",
            "No attempts to access other businesses’ data, overload the service, or misuse the MCP endpoints.",
            "No reselling or copying the service without our written permission.",
          ]}
        />
        <p>We may suspend accounts that break these rules, with notice where reasonable.</p>
      </LegalSection>

      <LegalSection id="fees" title="Fees">
        <p>
          TuskApp is free during early access. If we introduce paid plans we’ll give at least 30 days’ notice, and
          you can close your account before they apply.
        </p>
      </LegalSection>

      <LegalSection id="liability" title="Availability and liability">
        <p>
          We work to keep TuskApp running but can’t promise it will be uninterrupted, or that chat apps will always
          connect. To the extent the law allows, TuskApp isn’t liable for indirect or consequential losses, and our
          total liability is limited to the fees you paid us in the 12 months before the claim. Nothing here limits
          rights you have under Nigerian consumer protection law.
        </p>
      </LegalSection>

      <LegalSection id="ending" title="Ending your account">
        <p>
          You can close your account at any time by emailing{" "}
          <a href={`mailto:${SUPPORT_EMAIL}`} className={link}>{SUPPORT_EMAIL}</a>. We keep some records afterwards as
          described in the Privacy Policy.
        </p>
      </LegalSection>

      <LegalSection id="law" title="Changes and governing law">
        <p>
          We may update these terms and will tell account holders about material changes. These terms are governed
          by the laws of the Federal Republic of Nigeria, and disputes go to the courts of Lagos State.
        </p>
      </LegalSection>
    </LegalPage>
  );
}
