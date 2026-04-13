import { AdminPage } from "@/components/dashboard/AdminPage";

export default function QrPage() {
  return (
    <AdminPage
      eyebrow="QR Engine"
      title="Mode-driven QR interactions"
      description="QR remains generic and action-routed. Queue join is only one mode. The shell is ready for doorbell, visitor log, check-in, broadcast subscription, and future custom actions without hardcoding behavior into the scanner."
      stats={[
        { label: "Entity Types", value: "4", tone: "amber" },
        { label: "Routing", value: "Generic", tone: "teal" },
      ]}
    >
      <section className="grid gap-4 md:grid-cols-2">
        {["organization", "event", "group", "queue"].map((item) => (
          <div key={item} className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-[var(--text-muted)]">{item}</p>
            <p className="mt-3 text-sm leading-6 text-[var(--text-muted)]">
              QR codes can target this entity while carrying mode and action payload metadata for the client to interpret.
            </p>
          </div>
        ))}
      </section>
    </AdminPage>
  );
}
