import { Skeleton } from "@/components/ui";

export default function AuthLoading() {
  return (
    <div aria-busy="true" aria-label="Loading" className="space-y-4">
      <Skeleton className="h-7 w-48" />
      <Skeleton className="h-3.5 w-64" />
      <Skeleton className="mt-8 h-10 w-full rounded-xl" />
      <Skeleton className="h-10 w-full rounded-xl" />
      <Skeleton className="h-11 w-full rounded-full" />
    </div>
  );
}
