"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowRight, Clock3, DoorOpen, Search, Ticket } from "lucide-react";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { useQRCodes, useQueues } from "@/hooks/useApi";

type QueueRecord = {
  id: string;
  name: string;
  description?: string;
  queue_type?: string;
  current_serving?: number | null;
  status?: string;
  is_token_based?: boolean;
  estimated_wait_minutes?: number | null;
  waiting_count?: number;
  allow_rejoin?: boolean;
};

type QRRecord = {
  id: string;
  mode?: string;
  queue?: string | null;
};

export default function QueuesPage() {
  const [query, setQuery] = useState("");
  const { data, isLoading, error } = useQueues();
  const { data: qrData } = useQRCodes({ mode: "queue_join" });
  const queues = useMemo(() => (data ?? []) as QueueRecord[], [data]);
  const queueQrs = useMemo(() => (qrData ?? []) as QRRecord[], [qrData]);

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return queues.filter((item) => [item.name, item.description, item.queue_type, item.status].join(" ").toLowerCase().includes(normalizedQuery));
  }, [queues, query]);

  const liveCount = queues.filter((item) => item.status === "active" || item.status === "open").length;
  const waitingTotal = queues.reduce((sum, item) => sum + (item.waiting_count ?? 0), 0);
  const linkedQrCount = queueQrs.length;

  return (
    <AdminPage
      eyebrow="Queue Control"
      title="Live queue operations"
      description="Queue control reads live queue records so this module behaves like a real operations screen, not a placeholder brochure."
      stats={[
        { label: "Queues", value: String(queues.length), tone: "amber" },
        { label: "Live", value: String(liveCount), tone: "teal" },
        { label: "Waiting", value: String(waitingTotal), tone: "neutral" },
      ]}
    >
      <section className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Queue tools</p>
          <h3 className="mt-2 text-2xl font-semibold">Monitor wait flow</h3>
          <div className="mt-5 rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-3">
            <div className="flex items-center gap-3">
              <Search size={18} className="text-[var(--amber)]" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search by queue name or status"
                className="w-full bg-transparent py-2 text-[var(--text)] outline-none placeholder:text-[var(--text-muted)]"
              />
            </div>
          </div>
          <div className="mt-4 grid gap-3">
            <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Queue-linked QR records</p>
              <p className="mt-2 text-3xl font-semibold text-[var(--text)]">{linkedQrCount}</p>
              <p className="mt-1 text-sm text-[var(--text-muted)]">These are the door QR entries already using queue join mode.</p>
            </div>
            <Link href="/dashboard/doors/create" className="inline-flex items-center justify-between rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 transition hover:border-[var(--line-strong)]">
              <div>
                <p className="font-semibold text-[var(--text)]">Create queue door</p>
                <p className="mt-1 text-sm text-[var(--text-muted)]">Use the clinic or shop template to open new queue entry points.</p>
              </div>
              <ArrowRight size={18} className="text-[var(--amber)]" />
            </Link>
          </div>
        </article>

        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Live queues</p>
              <h3 className="mt-2 text-2xl font-semibold">{filtered.length} visible queues</h3>
            </div>
            <Ticket className="text-[var(--amber)]" size={18} />
          </div>

          {isLoading ? (
            <div className="mt-6 rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm text-[var(--text-muted)]">Loading queues…</div>
          ) : error ? (
            <div className="mt-6 rounded-[20px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-sm text-[var(--text-soft)]">Could not load queue records. Please confirm the API is reachable.</div>
          ) : filtered.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--line)] bg-[var(--bg-card)] p-8 text-center">
              <Ticket className="mx-auto text-[var(--text-muted)]" size={32} />
              <p className="mt-4 text-lg font-semibold">No queues yet</p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">Create queue-enabled doors first, then queue records will show up here as operations begin.</p>
            </div>
          ) : (
            <div className="mt-6 grid gap-3">
              {filtered.map((item) => (
                <div key={item.id} className="rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-4 transition hover:border-[var(--line-strong)]">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h4 className="text-lg font-semibold text-[var(--text)]">{item.name}</h4>
                        <span className="rounded-full bg-[var(--teal-soft)] px-3 py-1 text-xs font-semibold text-[var(--text)]">{item.status || "unknown"}</span>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--text-soft)]">
                        {item.queue_type ? <span className="rounded-full border border-[var(--line)] px-3 py-1">Type: {item.queue_type}</span> : null}
                        <span className="rounded-full border border-[var(--line)] px-3 py-1">Waiting: {item.waiting_count ?? 0}</span>
                        <span className="rounded-full border border-[var(--line)] px-3 py-1">Serving: {item.current_serving ?? "—"}</span>
                        {item.allow_rejoin ? <span className="rounded-full border border-[var(--line)] px-3 py-1">Rejoin enabled</span> : null}
                      </div>
                      {item.description ? <p className="mt-3 text-sm text-[var(--text-muted)]">{item.description}</p> : null}
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-2 text-xs text-[var(--text-muted)]">
                      <span className="rounded-2xl bg-[var(--amber-soft)] p-2 text-[var(--amber)]"><DoorOpen size={18} /></span>
                      <span className="inline-flex items-center gap-1"><Clock3 size={14} /> {item.estimated_wait_minutes ?? 0} min</span>
                      <span>{item.is_token_based ? "Token based" : "Manual flow"}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </AdminPage>
  );
}
