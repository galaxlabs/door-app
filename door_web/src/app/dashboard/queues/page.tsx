import { AdminPage } from "@/components/dashboard/AdminPage";

export default function QueuesPage() {
  return (
    <AdminPage
      eyebrow="Queue Control"
      title="Live queue monitoring and token operations"
      description="Queue join, current serving, and ticket lifecycle are now aligned with the backend contract. This page is prepared for live operational panels and websocket-fed status cards."
      stats={[
        { label: "Join Contract", value: "Fixed", tone: "amber" },
        { label: "Realtime", value: "WS Ready", tone: "teal" },
      ]}
    >
      <section className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm leading-7 text-[var(--text-muted)]">
        Canonical ticket states remain focused on Phase 1: issued, called, recalled, skipped, completed, and cancelled. Admin actions stay explicit and auditable.
      </section>
    </AdminPage>
  );
}
