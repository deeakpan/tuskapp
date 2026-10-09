import { Card, ListSkeleton, Skeleton } from "@/components/ui";

export default function DashboardLoading() {
  return (
    <div aria-busy="true" aria-label="Loading">
      <Skeleton className="h-8 w-56" />
      <Skeleton className="mt-3 mb-6 h-3.5 w-80 max-w-full" />
      <Card>
        <ListSkeleton rows={7} />
      </Card>
    </div>
  );
}
