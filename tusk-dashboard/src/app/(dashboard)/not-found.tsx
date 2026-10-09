import Link from "next/link";
import { Card, buttonStyles } from "@/components/ui";

export default function DashboardNotFound() {
  return (
    <Card className="mx-auto mt-10 max-w-lg p-8 text-center">
      <p className="num text-sm text-mint">404</p>
      <h1 className="mt-1 text-xl font-strong">We couldn’t find that</h1>
      <p className="mt-2 text-sm text-muted">It may have been removed, or the link is from another business.</p>
      <Link href="/" className={`${buttonStyles.primary} mt-6`}>
        Back to overview
      </Link>
    </Card>
  );
}
