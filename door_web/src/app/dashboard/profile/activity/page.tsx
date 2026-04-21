"use client";

import Link from "next/link";
import { useMemo } from "react";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { useAuditLogs } from "@/hooks/useApi";
import { ArrowLeft, ScrollText } from "lucide-react";

type AuditRecord = {
  id?: string;
  action?: string;
  entity_type?: string;
  entity_id?: string;
  created_at_server?: string;
  created_at?: string;
  payload?: any;
};

export default function ActivityPage() {
  const { data, isLoading, error } = useAuditLogs();
  const records = useMemo(() => (data ?? []) as AuditRecord[], [data]);

  return (
    <AdminPage
      eyebrow="Profile"
      title="Activity history"
      description="Recent activity records. This is a lightweight view over the audit stream."
      stats={[
        { label: "Records", value: String(records.length), tone: "amber" },
        { label: "Scope", value: "Recent", tone: "teal" },
        { label: "Source", value: "Audit", tone: "neutral" },
      ]}
    >
      <div className="flex items-center justify-between gap-3">
        <Link
          href="/dashboard/profile"
          className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
        >
          <ArrowLeft size={16} /> Back to profile
        </Link>
      </div>

      <section className="mt-4 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">All activity</p>
            <h3 className="mt-2 text-2xl font-semibold">History records</h3>
          </div>
          <ScrollText size={18} className="text-[var(--amber)]" />
        </div>

        {isLoading ? (
          <div className="mt-6 rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-5 text-sm text-[var(--text-muted)]">
            Loading…
          </div>
        ) : error ? (
          <div className="mt-6 rounded-[20px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-sm text-[var(--text-soft)]">
            Could not load activity records.
          </div>
        ) : records.length === 0 ? (
          <div className="mt-6 rounded-[24px] border border-dashed border-[var(--line)] bg-[var(--bg-panel)] p-8 text-center text-sm text-[var(--text-muted)]">
            No records yet.
          </div>
        ) : (
          <div className="mt-6 grid gap-3">
            {records.slice(0, 50).map((r, idx) => (
              <div key={r.id ?? idx} className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                <p className="text-sm font-semibold">{r.action ?? "activity"}</p>
                <p className="mt-1 text-xs text-[var(--text-muted)]">
                  {r.entity_type ?? "entity"} • {r.entity_id ?? "—"}
                </p>
                <p className="mt-2 text-xs text-[var(--text-muted)]">{r.created_at_server ?? r.created_at ?? ""}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </AdminPage>
  );
}

