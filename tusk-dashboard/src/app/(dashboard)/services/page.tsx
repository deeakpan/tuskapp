import type { Metadata } from "next";
import { Eye, EyeOff, Trash2, X } from "lucide-react";
import { Suspense } from "react";
import {
  createService,
  deleteService,
  removeServicePhoto,
  setServicePublished,
  updateService,
  uploadServicePhoto,
} from "@/app/actions/dashboard";
import { CatalogueImport } from "@/components/catalogue-import";
import { ActionButton } from "@/components/client";
import { ActionForm } from "@/components/forms";
import { PhotoUpload } from "@/components/photo-upload";
import { Card, CardHeader, EmptyState, Field, ListSkeleton, PageHeader, StatusPill, inputStyles } from "@/components/ui";
import { api } from "@/lib/api";
import type { Service } from "@/lib/types";

export const metadata: Metadata = {
  title: "Services",
  description: "Your price list. Customers in ChatGPT and Claude only see prices and durations from here.",
};

const MAX_PHOTOS = 6;

function ServiceFields({ service }: { service?: Service }) {
  return (
    <>
      <Field label="Name">
        <input name="name" required defaultValue={service?.name} className={inputStyles} placeholder="Knotless braids (medium)" />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Price (₦)">
          <input name="price_naira" required inputMode="numeric" defaultValue={service ? service.price_kobo / 100 : ""} className={`${inputStyles} num`} placeholder="35000" />
        </Field>
        <Field label="Duration">
          <input name="duration_min" required defaultValue={service?.duration} className={inputStyles} placeholder="2 hrs, 3 days, 1 week" />
        </Field>
      </div>
      <Field label="Description">
        <input name="description" defaultValue={service?.description} className={inputStyles} placeholder="Optional" />
      </Field>
    </>
  );
}

async function ServiceList() {
  const services = await api<Service[]>("/services");
  if (services.length === 0) {
    return (
      <Card>
        <EmptyState title="No services yet">Add your price list — customers in chat only see published services.</EmptyState>
      </Card>
    );
  }
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {services.map((service) => (
        <Card key={service.id} className={service.is_published ? "" : "opacity-70"}>
          <div className="flex items-start gap-4 p-4">
            <div className="min-w-0 flex-1">
              <p className="truncate text-[15px] font-strong">{service.name}</p>
              <p className="num text-[13px] text-ink-2">
                {service.price} · {service.duration}
              </p>
              <div className="mt-1.5">
                <StatusPill status={service.is_published ? "confirmed" : "expired"} label={service.is_published ? "Live in chat" : "Hidden"} />
              </div>
            </div>
            <div className="flex flex-col items-end">
              <ActionButton action={setServicePublished.bind(null, service.id, !service.is_published)}>
                {service.is_published ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                {service.is_published ? "Hide" : "Publish"}
              </ActionButton>
              <ActionButton action={deleteService.bind(null, service.id)} variant="danger" confirm={`Remove ${service.name}?`}>
                <Trash2 className="size-3.5" /> Remove
              </ActionButton>
            </div>
          </div>
          <div className="border-b border-line px-4 pb-4">
            <div className="flex flex-wrap gap-2">
              {service.photo_urls.map((url, index) => (
                <div key={url} className="group/photo relative">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={url}
                    alt={`${service.name}, photo ${index + 1}`}
                    width={64}
                    height={64}
                    loading="lazy"
                    className="size-16 rounded-xl border border-line object-cover"
                  />
                  <div className="absolute -top-1.5 -right-1.5 opacity-0 transition group-hover/photo:opacity-100 focus-within:opacity-100">
                    <ActionButton
                      action={removeServicePhoto.bind(null, service.id, url)}
                      variant="photo"
                      label={`Remove photo ${index + 1} of ${service.name}`}
                    >
                      <X className="size-3" />
                    </ActionButton>
                  </div>
                </div>
              ))}
              {service.photo_urls.length < MAX_PHOTOS && (
                <PhotoUpload
                  action={uploadServicePhoto.bind(null, service.id)}
                  label={`Add a photo of ${service.name}`}
                />
              )}
            </div>
            {service.photo_urls.length === 0 && (
              <p className="mt-2 text-xs text-muted">Add photos so chat can show customers what they’re booking.</p>
            )}
          </div>
          <details className="group">
            <summary className="cursor-pointer list-none px-4 py-2.5 text-[13px] text-muted hover:text-ink">
              Edit details <span className="inline-block transition group-open:rotate-90">›</span>
            </summary>
            <div className="px-4 pb-4">
              <ActionForm action={updateService.bind(null, service.id)} submitLabel="Save">
                <ServiceFields service={service} />
              </ActionForm>
            </div>
          </details>
        </Card>
      ))}
    </div>
  );
}

export default function ServicesPage() {
  return (
    <>
      <PageHeader title="Services" subtitle="Your price list. Prices in chat always come from here, never from the AI." />
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <Suspense fallback={<Card><ListSkeleton rows={6} /></Card>}>
          <ServiceList />
        </Suspense>
        <div className="space-y-6">
          <Card className="h-fit">
            <CardHeader title="Add a service" subtitle="Goes live in chat immediately." />
            <div className="p-5">
              <ActionForm action={createService} submitLabel="Add service" resetOnSuccess>
                <ServiceFields />
              </ActionForm>
            </div>
          </Card>
          <Card className="h-fit">
            <CardHeader title="Import a price list" subtitle="Add or update many items at once." />
            <div className="p-5">
              <CatalogueImport />
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
