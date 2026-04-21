import { AdminPage } from "@/components/dashboard/AdminPage";
import Link from "next/link";
import { BellRing, Building2, DoorOpen, PlusSquare, QrCode, Radio, Ticket, User } from "lucide-react";

const cards = [
  {
    title: "Doors",
    body: "Browse active doors, see their current purpose and routing mode, and manage the entries that behave like the original D-App door list.",
    href: "/dashboard/doors",
    icon: DoorOpen,
  },
  {
    title: "Create Door",
    body: "Create a doorbell, clinic queue, checkpoint, or emergency door on top of the QR engine.",
    href: "/dashboard/doors/create",
    icon: PlusSquare,
  },
  {
    title: "Queue Control",
    body: "Monitor live serving state, issue tokens from QR scans, and keep admin actions separate from scan routing.",
    href: "/dashboard/queues",
    icon: Ticket,
  },
  {
    title: "QR Management",
    body: "Publish generic, mode-driven QR codes for organization, event, group, and queue entry points.",
    href: "/dashboard/qr",
    icon: QrCode,
  },
  {
    title: "Broadcast + Chat",
    body: "Keep urgent one-way announcements separate from conversational messaging and delivery receipts.",
    href: "/dashboard/broadcast",
    icon: Radio,
  },
  {
    title: "Profile",
    body: "Update your profile, visitor card, privacy controls, and meeting points.",
    href: "/dashboard/profile",
    icon: User,
  },
];

const ops = [
  { label: "Organizations", value: "Org, event, and group structure", icon: Building2 },
  { label: "Queues", value: "Live status, call-next, and token handling", icon: Ticket },
  { label: "QR Codes", value: "Mode-driven routing and reusable payloads", icon: QrCode },
  { label: "Notifications", value: "In-app hooks for queue and broadcast events", icon: BellRing },
];

export default function DashboardPage() {
  return (
    <AdminPage
      eyebrow="Overview"
      title="Phase 1 command surface"
      description="This admin shell is centered on the locked MVP: identity, organizations, QR flows, queue control, chat, broadcast, sync awareness, audit traces, and notification hooks."
      stats={[
        { label: "Scope", value: "Phase 1", tone: "amber" },
        { label: "Mode", value: "Offline-first", tone: "teal" },
        { label: "Stack", value: "Backend + Web", tone: "neutral" },
      ]}
    >
      <section className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Today’s focus</p>
              <h3 className="mt-2 text-2xl font-semibold">Operational control without clutter</h3>
            </div>
            <div className="rounded-full border border-[var(--line-strong)] bg-[var(--amber-soft)] px-4 py-2 text-sm">
              Keep QR routing generic
            </div>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {ops.map(({ label, value, icon: Icon }) => (
              <div key={label} className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] p-4">
                <Icon size={18} className="text-[var(--teal)]" />
                <h4 className="mt-3 text-base font-semibold">{label}</h4>
                <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">{value}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-6">
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Phase 1 boundary</p>
          <h3 className="mt-2 text-2xl font-semibold">What belongs now</h3>
          <div className="mt-5 space-y-4 text-sm leading-6 text-[var(--text-muted)]">
            <p>Identity, organizations, QR, queue, basic chat, broadcast, sync, audit, and notifications.</p>
            <p>Marketplace, payments, trust engine, and discovery remain outside this implementation layer.</p>
            <p>The admin shell should help you manage what is real now, not preview five future products at once.</p>
          </div>
        </div>
      </section>
      <section className="grid gap-4 lg:grid-cols-3">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <Link
              key={card.title}
              href={card.href}
              className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5 transition hover:border-[var(--line-strong)] hover:bg-[rgba(255,255,255,0.03)]"
            >
              <Icon size={18} className="text-[var(--amber)]" />
              <h3 className="mt-4 text-lg font-medium">{card.title}</h3>
              <p className="mt-3 text-sm leading-6 text-[var(--text-muted)]">{card.body}</p>
              <p className="mt-4 text-sm text-[var(--teal)]">Open module</p>
            </Link>
          );
        })}
      </section>
    </AdminPage>
  );
}
