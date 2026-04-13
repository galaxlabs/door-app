import { AdminPage } from "@/components/dashboard/AdminPage";

export default function OrganizationsPage() {
  return (
    <AdminPage
      eyebrow="Organizations"
      title="Org, event, and group foundations"
      description="The Phase 1 data model already supports organizations, future-flexible events, and groups from day one. This surface is prepared for membership management, role assignment, and event-linked coordination."
      stats={[
        { label: "Roles", value: "6", tone: "amber" },
        { label: "Event Scope", value: "Flexible", tone: "teal" },
      ]}
    >
      <section className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm leading-7 text-[var(--text-muted)]">
        Organization owners, admins, managers, group leaders, staff, and general users are treated as distinct operational roles. Events remain flexible enough to support organization-linked and broader future use cases without overcommitting the model now.
      </section>
    </AdminPage>
  );
}
