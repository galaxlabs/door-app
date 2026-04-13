import { AdminPage } from "@/components/dashboard/AdminPage";

export default function AuditPage() {
  return (
    <AdminPage
      eyebrow="Audit"
      title="Operational traceability"
      description="Audit logging is already a backend concern, and this page gives the admin shell a place to surface actor, device, entity, and before/after state visibility."
      stats={[
        { label: "Actor Sources", value: "User + Device", tone: "amber" },
        { label: "Snapshots", value: "Before / After", tone: "teal" },
      ]}
    >
      <section className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm leading-7 text-[var(--text-muted)]">
        The current backend already stores request metadata, entity identifiers, context JSON, and state snapshots that can later power admin filters and investigations.
      </section>
    </AdminPage>
  );
}
