import { Card, ListSkeleton, Skeleton } from "@/components/ui";

export default function ProfileLoading() {
  return (
    <div aria-busy="true" aria-label="Loading" className="space-y-6">
      <div className="flex gap-5">
        <Skeleton className="size-16 rounded-2xl" />
        <div className="flex-1">
          <Skeleton className="h-7 w-56" />
          <Skeleton className="mt-3 h-3.5 w-40" />
          <Skeleton className="mt-5 h-3.5 w-full max-w-lg" />
        </div>
      </div>
      <Card>
        <ListSkeleton rows={4} />
      </Card>
    </div>
  );
}
