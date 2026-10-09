import { Clock, Home, MapPin, MessageCircle, ShieldCheck } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { AiLogos } from "@/components/ai-logos";
import { CopyButton } from "@/components/client";
import { Avatar, Card, CardHeader, buttonStyles } from "@/components/ui";
import { getPublicBusiness } from "@/lib/public";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const business = await getPublicBusiness(slug);
  const place = [business.category, business.area].filter(Boolean).join(" in ");
  const description =
    business.about.slice(0, 155) || `${business.name}${place ? `, ${place}` : ""}. See prices and book on TuskApp.`;
  return {
    title: place ? `${business.name} · ${place}` : business.name,
    description,
    alternates: { canonical: business.profile_url },
    openGraph: { title: business.name, description, url: business.profile_url, type: "profile" },
  };
}

export default async function BusinessProfilePage({ params }: Props) {
  const { slug } = await params;
  const business = await getPublicBusiness(slug);
  const place = [business.category, business.area].filter(Boolean).join(" · ");
  const address =
    business.area && !business.address.toLowerCase().includes(business.area.toLowerCase())
      ? [business.address, business.area].filter(Boolean).join(", ")
      : business.address;

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-5 sm:flex-row sm:items-start">
        <Avatar name={business.name} className="size-16 rounded-2xl text-lg" />
        <div className="min-w-0 flex-1">
          <h1 className="text-[28px] leading-tight font-strong tracking-[-0.03em]">{business.name}</h1>
          {place && <p className="mt-1 text-sm text-muted capitalize">{place}</p>}
          {business.about && <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-ink-2">{business.about}</p>}
          <div className="mt-5 flex flex-wrap gap-2">
            {business.whatsapp_url && (
              <a href={business.whatsapp_url} target="_blank" rel="noopener noreferrer" className={buttonStyles.primary}>
                <MessageCircle className="size-4" aria-hidden />
                Chat on WhatsApp
              </a>
            )}
            {address && (
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`}
                target="_blank"
                rel="noopener noreferrer"
                className={buttonStyles.secondary}
              >
                <MapPin className="size-4" aria-hidden />
                Directions
              </a>
            )}
          </div>
        </div>
      </section>

      <Card>
        <CardHeader title="Services and prices" subtitle={`${business.services.length} available`} />
        {business.services.length === 0 ? (
          <p className="px-5 py-8 text-sm text-muted">No services listed yet.</p>
        ) : (
          <ul className="divide-y divide-line">
            {business.services.map((service) => (
              <li key={service.id} className="flex items-start gap-4 px-5 py-4">
                {service.photo_urls[0] && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={service.photo_urls[0]}
                    alt={service.name}
                    width={56}
                    height={56}
                    loading="lazy"
                    className="size-14 shrink-0 rounded-xl border border-line object-cover"
                  />
                )}
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-strong text-ink">{service.name}</p>
                  {service.description && <p className="mt-0.5 text-[13px] text-muted">{service.description}</p>}
                  <p className="mt-1 text-xs text-faint">{service.duration}</p>
                </div>
                <p className="num shrink-0 text-sm text-ink">{service.price}</p>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader title="Visit or get it delivered" />
          <dl className="space-y-4 px-5 py-4 text-sm">
            {address && (
              <Detail icon={MapPin} label="Address">
                {address}
              </Detail>
            )}
            <Detail icon={Home} label="Home service">
              {business.home_service.offered
                ? `Available${business.home_service.fee ? `, ${business.home_service.fee} extra` : ""}`
                : "Not offered, visit in person"}
            </Detail>
            {business.opening_hours.length > 0 && (
              <Detail icon={Clock} label="Opening hours">
                <ul className="space-y-0.5">
                  {business.opening_hours.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </Detail>
            )}
          </dl>
        </Card>

        <Card>
          <CardHeader title="Booking" />
          <dl className="space-y-4 px-5 py-4 text-sm">
            <Detail icon={ShieldCheck} label="Deposit">
              {business.deposit_to_book ? `${business.deposit_to_book} to hold your booking` : "No deposit needed"}
            </Detail>
            {business.policies.length > 0 && (
              <Detail icon={ShieldCheck} label="Policies">
                <ul className="list-disc space-y-1 pl-4">
                  {business.policies.map((policy) => (
                    <li key={policy}>{policy}</li>
                  ))}
                </ul>
              </Detail>
            )}
          </dl>
        </Card>
      </div>

      <Card className="px-5 py-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="flex items-center gap-2 text-[15px] font-strong text-ink">
              <AiLogos /> Book from ChatGPT or Claude
            </p>
            <p className="mt-1 max-w-md text-[13px] text-muted">
              Add TuskApp as a connector, then ask for {business.name}. Your assistant checks live prices and free
              times, and holds your slot.
            </p>
          </div>
          <CopyButton value={business.customer_mcp_url} label="Copy connector link" />
        </div>
      </Card>

      <p className="text-center text-[13px] text-muted">
        Run a business?{" "}
        <Link href="/signup" className="text-ink underline underline-offset-4">
          Get your own TuskApp page
        </Link>
      </p>
    </div>
  );
}

function Detail({
  icon: Icon,
  label,
  children,
}: {
  icon: typeof MapPin;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex gap-3">
      <Icon className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />
      <div>
        <dt className="text-xs text-muted">{label}</dt>
        <dd className="mt-0.5 text-ink-2">{children}</dd>
      </div>
    </div>
  );
}
