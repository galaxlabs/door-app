"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import {
  BellRing,
  Building2,
  ClipboardCheck,
  LayoutDashboard,
  MessageCircleMore,
  QrCode,
  Radio,
  ScrollText,
  Ticket,
} from "lucide-react";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/organizations", label: "Organizations", icon: Building2 },
  { href: "/dashboard/qr", label: "QR Codes", icon: QrCode },
  { href: "/dashboard/queues", label: "Queues", icon: Ticket },
  { href: "/dashboard/chat", label: "Chat", icon: MessageCircleMore },
  { href: "/dashboard/broadcast", label: "Broadcast", icon: Radio },
  { href: "/dashboard/phase2", label: "Phase 2", icon: ClipboardCheck },
  { href: "/dashboard/audit", label: "Audit Logs", icon: ScrollText },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="min-h-screen bg-transparent text-[var(--text)]">
      <div className="mx-auto flex min-h-screen w-full max-w-[1600px] gap-6 px-4 py-4 md:px-6">
        <aside className="hidden w-72 shrink-0 flex-col rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] p-5 shadow-[var(--shadow)] backdrop-blur md:flex">
          <div className="mb-8 rounded-[var(--radius-lg)] border border-[var(--line-strong)] bg-[linear-gradient(145deg,rgba(246,185,74,0.16),rgba(55,214,197,0.08))] p-5">
            <p className="text-xs uppercase tracking-[0.35em] text-[var(--text-muted)]">Door App</p>
            <h2 className="mt-3 text-2xl font-semibold">Smart QR Coordination</h2>
            <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
              Phase 1 control surface for QR flows, queues, messaging, sync, and audit visibility.
            </p>
          </div>
          <nav className="flex flex-1 flex-col gap-2">
            {NAV.map((n) => {
              const Icon = n.icon;
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={clsx(
                    "flex items-center gap-3 rounded-[18px] border px-4 py-3 text-sm font-medium transition",
                    path === n.href
                      ? "border-[var(--line-strong)] bg-[var(--amber-soft)] text-[var(--text)]"
                      : "border-transparent text-[var(--text-muted)] hover:border-[var(--line)] hover:bg-[rgba(255,255,255,0.03)] hover:text-[var(--text)]"
                  )}
                >
                  <Icon size={18} />
                  <span>{n.label}</span>
                </Link>
              );
            })}
          </nav>
          <div className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Live hooks</p>
                <p className="text-xs text-[var(--text-muted)]">Queue, broadcast, notifications</p>
              </div>
              <BellRing size={18} className="text-[var(--teal)]" />
            </div>
          </div>
        </aside>
        <div className="flex min-h-screen flex-1 flex-col gap-4">
          <header className="flex flex-wrap items-center justify-between gap-3 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] px-5 py-4 shadow-[var(--shadow)] backdrop-blur">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Admin Surface</p>
              <h1 className="text-xl font-semibold">Door App Phase 1</h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="rounded-full border border-[var(--line)] bg-[var(--bg-card)] px-4 py-2 text-sm text-[var(--text-muted)]">
                Offline-first QR, queue, chat, broadcast
              </div>
            </div>
          </header>
          <div className="flex gap-3 overflow-x-auto rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] p-3 shadow-[var(--shadow)] backdrop-blur md:hidden">
            {NAV.map((n) => {
              const Icon = n.icon;
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={clsx(
                    "flex min-w-fit items-center gap-2 rounded-[16px] border px-4 py-3 text-sm font-medium transition",
                    path === n.href
                      ? "border-[var(--line-strong)] bg-[var(--amber-soft)] text-[var(--text)]"
                      : "border-[var(--line)] bg-[var(--bg-card)] text-[var(--text-muted)]"
                  )}
                >
                  <Icon size={16} />
                  <span>{n.label}</span>
                </Link>
              );
            })}
          </div>
          <main className="flex-1 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-panel)] p-5 shadow-[var(--shadow)] backdrop-blur md:p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
