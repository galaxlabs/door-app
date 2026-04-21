"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { ArrowLeft, Copy, DoorOpen, Loader2, QrCode, Save } from "lucide-react";

type DoorRecord = {
  id: string;
  name?: string;
  label?: string;
  purpose?: string;
  mode?: string;
  is_active?: boolean;
  status?: string;
  qr_token?: string;
  image_url?: string | null;
  scans_count?: number;
  expires_at?: string | null;
};

export default function DoorDetailsPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const [door, setDoor] = useState<DoorRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [purpose, setPurpose] = useState("");
  const [isActive, setIsActive] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const res = await api.get(`qr/codes/${id}/`);
        if (!mounted) return;
        const record = res.data as DoorRecord;
        setDoor(record);
        setName(String(record.name ?? record.label ?? ""));
        setPurpose(String(record.purpose ?? ""));
        setIsActive(Boolean(record.is_active ?? true));
      } catch (err: any) {
        if (!mounted) return;
        const detail = err?.response?.data?.detail;
        setError(typeof detail === "string" ? detail : "Could not load this door.");
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [id]);

  const token = useMemo(() => String(door?.qr_token ?? ""), [door?.qr_token]);
  const scans = useMemo(() => String(door?.scans_count ?? 0), [door?.scans_count]);

  async function save() {
    if (!id) return;
    setSaving(true);
    setError(null);
    try {
      const res = await api.patch(`qr/codes/${id}/`, {
        name: name.trim() || "Untitled door",
        purpose: purpose.trim(),
        is_active: isActive,
        status: isActive ? "active" : "inactive",
      });
      const record = res.data as DoorRecord;
      setDoor(record);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Could not save door.");
    } finally {
      setSaving(false);
    }
  }

  async function copyToken() {
    if (!token) return;
    try {
      await navigator.clipboard.writeText(token);
    } catch {
      // ignore
    }
  }

  return (
    <AdminPage
      eyebrow="Doors"
      title={door?.label || door?.name || "Door settings"}
      description="Edit door basics and copy the QR token for printing/sharing."
      stats={[
        { label: "Scans", value: scans, tone: "amber" },
        { label: "Active", value: isActive ? "Yes" : "No", tone: "teal" },
        { label: "Type", value: door?.purpose ? String(door.purpose) : "—", tone: "neutral" },
      ]}
    >
      <div className="flex items-center justify-between gap-3">
        <Link
          href="/dashboard/doors"
          className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
        >
          <ArrowLeft size={16} /> Back to doors
        </Link>
        <Link
          href={`/dashboard/qr?focus=${id}`}
          className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-panel)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:border-[var(--line-strong)] hover:text-[var(--text)]"
        >
          <QrCode size={16} /> Open in QR
        </Link>
      </div>

      <section className="mt-4 grid gap-4 xl:grid-cols-[1fr_0.9fr]">
        <article className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Settings</p>
              <h3 className="mt-2 text-2xl font-semibold">Door details</h3>
            </div>
            <DoorOpen size={18} className="text-[var(--amber)]" />
          </div>

          {loading ? (
            <div className="mt-6 rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-5 text-sm text-[var(--text-muted)]">
              Loading…
            </div>
          ) : error ? (
            <div className="mt-6 rounded-[20px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-sm text-[var(--text-soft)]">
              {error}
            </div>
          ) : !door ? (
            <div className="mt-6 rounded-[20px] border border-dashed border-[var(--line)] bg-[var(--bg-panel)] p-8 text-center text-sm text-[var(--text-muted)]">
              Door not found.
            </div>
          ) : (
            <div className="mt-6 space-y-4">
              <div>
                <label className="block text-sm text-[var(--text-muted)]">Door name</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                />
              </div>
              <div>
                <label className="block text-sm text-[var(--text-muted)]">Purpose (optional)</label>
                <input
                  value={purpose}
                  onChange={(e) => setPurpose(e.target.value)}
                  className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                />
              </div>

              <label className="flex items-center justify-between gap-3 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-sm">
                <span className="font-semibold text-[var(--text)]">Active</span>
                <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} className="h-4 w-4" />
              </label>

              <button
                type="button"
                onClick={save}
                disabled={saving}
                className="inline-flex w-full items-center justify-center gap-2 rounded-[18px] bg-[linear-gradient(135deg,#37d6c5,#239e91)] px-4 py-4 text-sm font-semibold text-[#041412] transition hover:brightness-105 disabled:opacity-70"
              >
                {saving ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                Save
              </button>
            </div>
          )}
        </article>

        <article className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">QR</p>
          <h3 className="mt-2 text-2xl font-semibold">Share token</h3>

          {token ? (
            <div className="mt-6 space-y-3">
              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">Token</p>
                <p className="mt-2 break-all font-semibold text-[var(--text)]">{token}</p>
                <button
                  type="button"
                  onClick={copyToken}
                  className="mt-4 inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
                >
                  <Copy size={16} /> Copy token
                </button>
              </div>
              {door?.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  alt=""
                  src={String(door.image_url)}
                  className="w-full rounded-[20px] border border-[var(--line)] bg-white p-4"
                />
              ) : (
                <div className="rounded-[20px] border border-dashed border-[var(--line)] bg-[var(--bg-panel)] p-8 text-center text-sm text-[var(--text-muted)]">
                  QR image not available yet.
                </div>
              )}
            </div>
          ) : (
            <div className="mt-6 rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-5 text-sm text-[var(--text-muted)]">
              Token not available.
            </div>
          )}
        </article>
      </section>
    </AdminPage>
  );
}

