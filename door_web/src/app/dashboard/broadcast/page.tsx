import { AdminPage } from "@/components/dashboard/AdminPage";

export default function BroadcastPage() {
  return (
    <AdminPage
      eyebrow="Broadcast"
      title="One-way operational messaging"
      description="Broadcast channels, messages, and deliveries are modeled independently from chat. This keeps queue calls, alerts, and organizational notices operationally clean."
      stats={[
        { label: "Target Modes", value: "3", tone: "amber" },
        { label: "Deliveries", value: "Tracked", tone: "teal" },
      ]}
    >
      <section className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm leading-7 text-[var(--text-muted)]">
        Organization-wide, group-based, and selected-member targeting are all supported without collapsing broadcast into chat rooms.
      </section>
    </AdminPage>
  );
}
