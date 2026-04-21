import { AdminPage } from "@/components/dashboard/AdminPage";

const pillars = [
  {
    title: "Attendance control",
    summary: "Run roll calls, QR check-ins, and group presence tracking from one place.",
    accent: "amber",
    metrics: ["24 active sessions", "312 records today", "8 flagged absences"],
  },
  {
    title: "Visitor and movement log",
    summary: "Track arrivals, departures, checkpoints, and supervised trip progress.",
    accent: "teal",
    metrics: ["18 live visitors", "7 checkpoints", "3 active trips"],
  },
  {
    title: "Family and Hajj safety",
    summary: "Support households, gather mode, emergency cards, and missing-person escalation.",
    accent: "neutral",
    metrics: ["56 households", "14 gather groups", "2 open cases"],
  },
];

const workflows = [
  {
    label: "Attendance",
    detail: "Session setup, check-in records, present/late/absent state, and missing-member review.",
  },
  {
    label: "Visitor log",
    detail: "Host ownership, visit purpose, arrival and departure state, and traceable history.",
  },
  {
    label: "Checkpoint and trip",
    detail: "Checkpoint publishing, trip creation, movement logs, and route-style follow-up.",
  },
  {
    label: "Households",
    detail: "Family hierarchy, guardianship, relation labels, and grouped supervision.",
  },
  {
    label: "Gather mode",
    detail: "Fast headcount sessions with safe, delayed, and missing participant status.",
  },
  {
    label: "Emergency and missing",
    detail: "Emergency cards, Hajj tracker data, missing-person cases, and sighting reports.",
  },
];

const actionBoard = [
  { title: "Open attendance session", note: "Start QR or manual check-in for an event or group." },
  { title: "Register visitor", note: "Create a traceable visit record with host and purpose." },
  { title: "Launch gather mode", note: "Move a family or Hajj group into active regrouping mode." },
  { title: "Open missing case", note: "Escalate a safety issue with last-seen details and sightings." },
];

export default function Phase2Page() {
  return (
    <AdminPage
      eyebrow="Phase 2"
      title="Field coordination, attendance, and safety"
      description="Door App now stretches beyond QR entry and queues into supervised movement, household coordination, and safety-first group operations."
      stats={[
        { label: "Domains", value: "6", tone: "amber" },
        { label: "Records", value: "Live-ready", tone: "teal" },
        { label: "Priority", value: "Field Ops", tone: "neutral" },
      ]}
    >
      <section className="grid gap-4 xl:grid-cols-3">
        {pillars.map((pillar) => (
          <article
            key={pillar.title}
            className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]"
          >
            <span
              className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                pillar.accent === "amber"
                  ? "bg-amber-400/15 text-amber-200"
                  : pillar.accent === "teal"
                    ? "bg-teal-400/15 text-teal-200"
                    : "bg-white/8 text-slate-200"
              }`}
            >
              Phase 2 pillar
            </span>
            <h3 className="mt-4 text-xl font-semibold text-white">{pillar.title}</h3>
            <p className="mt-3 text-sm leading-6 text-[var(--text-muted)]">{pillar.summary}</p>
            <div className="mt-5 space-y-2">
              {pillar.metrics.map((metric) => (
                <div
                  key={metric}
                  className="rounded-2xl border border-white/6 bg-white/3 px-3 py-2 text-sm text-slate-100"
                >
                  {metric}
                </div>
              ))}
            </div>
          </article>
        ))}
      </section>

      <section className="mt-6 grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <article className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--text-soft)]">
                Workflow coverage
              </p>
              <h3 className="mt-2 text-xl font-semibold text-white">Operational modules</h3>
            </div>
            <div className="rounded-2xl border border-teal-400/20 bg-teal-400/10 px-3 py-2 text-sm text-teal-100">
              Built on the same org-event-group model
            </div>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {workflows.map((workflow) => (
              <div
                key={workflow.label}
                className="rounded-3xl border border-white/6 bg-[#0f1522] p-4"
              >
                <h4 className="text-base font-semibold text-white">{workflow.label}</h4>
                <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">{workflow.detail}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[linear-gradient(180deg,rgba(246,185,74,0.12),rgba(8,10,16,0.96))] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-200">
            Quick actions
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">Launch board</h3>
          <div className="mt-5 space-y-3">
            {actionBoard.map((action) => (
              <div
                key={action.title}
                className="rounded-3xl border border-amber-300/10 bg-black/20 p-4"
              >
                <p className="text-sm font-semibold text-white">{action.title}</p>
                <p className="mt-2 text-sm leading-6 text-slate-200/75">{action.note}</p>
              </div>
            ))}
          </div>
        </article>
      </section>
    </AdminPage>
  );
}
