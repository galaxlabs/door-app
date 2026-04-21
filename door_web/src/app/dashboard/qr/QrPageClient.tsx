"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, CheckCircle2, DoorOpen, Filter, QrCode, ShieldAlert, Ticket } from "lucide-react";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { useQRCodes } from "@/hooks/useApi";

type QRRecord = {
  id: string;
  label?: string;
  name?: string;
  purpose?: string;
  entity_type?: string;
  mode?: string;
  is_active?: boolean;
  organization?: string | null;
  qr_token?: string;
  scans_count?: number;
  expires_at?: string | null;
};

const modeLabel: Record<string, string> = {
  custom_action: "Door Bell",
  queue_join: "Queue Join",
  open_chat: "Visitor Chat",
  check_in: "Check In",
  subscribe_broadcast: "Broadcast",
};

export default function QrPageClient() {
  const searchParams = useSearchParams();
  const focusId = searchParams.get("focus");
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("all");
  const { data, isLoading, error } = useQRCodes();
  const qrCodes = useMemo(() => (data ?? []) as QRRecord[], [data]);

  const filtered = useMemo(() => {
    return qrCodes.filter((item) => {
      const matchesMode = mode === "all" || item.mode === mode;
      const haystack = [item.label, item.name, item.purpose, item.qr_token, item.entity_type].join(" ").toLowerCase();
      const matchesQuery = haystack.includes(query.trim().toLowerCase());
      return matchesMode && matchesQuery;
    });
  }, [mode, query, qrCodes]);

  const stats = {
    active: qrCodes.filter((item) => item.is_active).length,
    queue: qrCodes.filter((item) => item.mode === "queue_join").length,
    scans: qrCodes.reduce((sum, item) => sum + (item.scans_count ?? 0), 0),
  };

  return (
    <AdminPage
      eyebrow="QR Codes"
      title="Live QR code management"
      description="The QR codes module shows live backend records, so opening it from a door card lands on something useful instead of a placeholder panel."
      stats={[
        { label: "Active QR", value: String(stats.active), tone: "amber" },
        { label: "Queue QR", value: String(stats.queue), tone: "teal" },
        { label: "Total Scans", value: String(stats.scans), tone: "neutral" },
      ]}
    >
      <section className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Filter QR Codes</p>
              <h3 className="mt-2 text-2xl font-semibold">Find the right entry point</h3>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
              >
                <ArrowLeft size={16} /> Dashboard
              </Link>
              <Filter className="text-[var(--amber)]" size={18} />
            </div>
          </div>
          <div className="mt-5 space-y-4">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by label, token, purpose, or entity"
              className="w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)] focus:ring-2 focus:ring-[var(--amber-soft)]"
            />
            <div className="flex flex-wrap gap-2">
              {[
                ["all", "All"],
                ["custom_action", "Door Bell"],
                ["queue_join", "Queue"],
                ["check_in", "Check In"],
                ["open_chat", "Chat"],
              ].map(([value, label]) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setMode(value)}
                  className={`rounded-full px-4 py-2 text-sm transition ${mode === value ? "border border-[var(--line-strong)] bg-[var(--amber-soft)] text-[var(--text)]" : "border border-[var(--line)] bg-[var(--bg-card)] text-[var(--text-muted)] hover:text-[var(--text)]"}`}
                >
                  {label}
                </button>
              ))}
            </div>
            <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-4 text-sm text-[var(--text-muted)]">
              <p className="font-medium text-[var(--text)]">Quick actions</p>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                <Link
                  href="/dashboard/doors/create"
                  className="rounded-[16px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-3 transition hover:border-[var(--line-strong)]"
                >
                  Create new door QR
                </Link>
                <Link
                  href="/dashboard/queues"
                  className="rounded-[16px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-3 transition hover:border-[var(--line-strong)]"
                >
                  Open queue operations
                </Link>
              </div>
            </div>
          </div>
        </article>

        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">QR records</p>
              <h3 className="mt-2 text-2xl font-semibold">{filtered.length} visible entries</h3>
            </div>
            {focusId ? (
              <span className="rounded-full border border-[var(--line-strong)] bg-[var(--amber-soft)] px-4 py-2 text-sm">Focused from door</span>
            ) : null}
          </div>

          {isLoading ? (
            <div className="mt-6 rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm text-[var(--text-muted)]">
              Loading QR records…
            </div>
          ) : error ? (
            <div className="mt-6 rounded-[20px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-sm text-[var(--text-soft)]">
              Could not load QR records. Please confirm the API is reachable.
            </div>
          ) : filtered.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--line)] bg-[var(--bg-card)] p-8 text-center">
              <QrCode className="mx-auto text-[var(--text-muted)]" size={32} />
              <p className="mt-4 text-lg font-semibold">No QR entries match</p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">
                Try a different search or create a new door to generate the first QR record.
              </p>
            </div>
          ) : (
            <div className="mt-6 grid gap-3">
              {filtered.map((item) => {
                const focused = focusId === item.id;
                return (
                  <div
                    key={item.id}
                    className={`rounded-[22px] border p-4 transition ${focused ? "border-[var(--line-strong)] bg-[rgba(246,185,74,0.12)]" : "border-[var(--line)] bg-[var(--bg-card)]"}`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <h4 className="text-lg font-semibold text-[var(--text)]">{item.label || item.name || "Untitled QR"}</h4>
                          {focused ? <CheckCircle2 size={16} className="text-[var(--amber)]" /> : null}
                        </div>
                        <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--text-soft)]">
                          <span className="rounded-full border border-[var(--line)] px-3 py-1">
                            Mode: {modeLabel[item.mode || ""] ?? item.mode ?? "—"}
                          </span>
                          <span className="rounded-full border border-[var(--line)] px-3 py-1">
                            Entity: {item.entity_type || "organization"}
                          </span>
                          <span className="rounded-full border border-[var(--line)] px-3 py-1">Scans: {item.scans_count ?? 0}</span>
                        </div>
                        <p className="mt-3 text-sm text-[var(--text-muted)]">Purpose: {item.purpose || "general"}</p>
                        {item.qr_token ? <p className="mt-1 text-xs text-[var(--text-muted)]">Token: {item.qr_token}</p> : null}
                      </div>
                      <div className="flex shrink-0 items-center gap-2">
                        {item.mode === "queue_join" ? (
                          <span className="rounded-2xl bg-[var(--teal-soft)] p-2 text-[var(--teal)]">
                            <Ticket size={18} />
                          </span>
                        ) : item.purpose === "emergency" ? (
                          <span className="rounded-2xl bg-[rgba(255,109,109,0.12)] p-2 text-[var(--danger)]">
                            <ShieldAlert size={18} />
                          </span>
                        ) : (
                          <span className="rounded-2xl bg-[var(--amber-soft)] p-2 text-[var(--amber)]">
                            <DoorOpen size={18} />
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </article>
      </section>
    </AdminPage>
  );
}
