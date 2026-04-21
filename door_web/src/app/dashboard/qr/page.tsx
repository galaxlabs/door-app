import { Suspense } from "react";
import QrPageClient from "./QrPageClient";

export default function QrPage() {
  return (
    <Suspense
      fallback={
        <div className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-6 text-sm text-[var(--text-muted)]">
          Loading QR module…
        </div>
      }
    >
      <QrPageClient />
    </Suspense>
  );
}
