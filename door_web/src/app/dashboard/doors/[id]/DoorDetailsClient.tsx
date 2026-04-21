"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import QRCodeSvg from "react-qr-code";
import api from "@/lib/api";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { useQRCode } from "@/hooks/useApi";
import { ArrowLeft, Copy, DoorOpen, Loader2, Save, Shield, ToggleLeft, ToggleRight } from "lucide-react";

type QRRecord = {
  id: string;
  name?: string;
  label?: string;
  purpose?: string;
  mode?: string;
  entity_type?: string;
  qr_token?: string;
  is_active?: boolean;
  status?: string;
  scans_count?: number;
  expires_at?: string | null;
};

type DoorForm = {
  name: string;
  purpose: string;
  mode: "custom_action" | "queue_join" | "check_in" | "open_chat" | "subscribe_broadcast";
  is_active: boolean;
};

function safeString(value: unknown) {
  return typeof value === "string" ? value : String(value ?? "");
}

export function DoorDetailsClient({ id }: { id: string }) {
  const { data, isLoading, error, refetch } = useQRCode(id);
  const door = useMemo(() => (data ?? null) as QRRecord | null, [data]);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const { register, handleSubmit, reset, watch } = useForm<DoorForm>({
    defaultValues: { name: "", purpose: "", mode: "custom_action", is_active: true },
  });

  useEffect(() => {
    if (!door) return;
    reset({
      name: safeString(door.name ?? door.label ?? ""),
      purpose: safeString(door.purpose ?? ""),
      mode: (door.mode ?? "custom_action") as DoorForm["mode"],
      is_active: Boolean(door.is_active ?? true),
    });
  }, [door, reset]);

  const token = door?.qr_token ?? "";
  const qrValue = token || door?.id || "";
  const mode = watch("mode");
  const isActive = watch("is_active");

  async function copy(value: string) {
    try {
      await navigator.clipboard.writeText(value);
      setNotice("Copied.");
      setTimeout(() => setNotice(null), 1400);
    } catch {
      setNotice("Copy blocked by browser.");
      setTimeout(() => setNotice(null), 1600);
    }
  }

  async function onSubmit(values: DoorForm) {
    if (!door) return;
    setSaving(true);
    setSaveError(null);
    setNotice(null);
    try {
      await api.patch(`/qr/codes/${door.id}/`, {
        name: values.name,
        purpose: values.purpose,
        mode: values.mode,
        is_active: values.is_active,
        status: values.is_active ? "active" : "inactive",
      });
      await refetch();
      setNotice("Saved.");
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setSaveError(typeof detail === "string" ? detail : "Could not save door.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AdminPage
      eyebrow="Doors"
      title={door?.name || door?.label || "Door settings"}
      description="Door settings mirror the mobile-style D-App flow: keep the essentials close, and extend settings as modes mature."
      stats={[
        { label: "Mode", value: door?.mode ?? "—", tone: "amber" },
        { label: "Status", value: door?.is_active ? "Active" : "Inactive", tone: "teal" },
        { label: "Scans", value: String(door?.scans_count ?? 0), tone: "neutral" },
      ]}
    >
      <div className="flex items-center justify-between gap-3">
        <Link
          href="/dashboard/doors"
          className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
        >
          <ArrowLeft size={16} /> Back to doors
        </Link>
        <div className="flex items-center gap-2">
          <Link
            href={`/dashboard/qr?focus=${id}`}
            className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-panel)] px-3 py-2 text-sm font-semibold text-[var(--text)] transition hover:border-[var(--line-strong)]"
          >
            <DoorOpen size={16} /> Open QR
          </Link>
        </div>
      </div>

      {notice ? (
        <div className="mt-4 rounded-[18px] border border-[rgba(55,214,197,0.22)] bg-[rgba(55,214,197,0.08)] px-4 py-3 text-sm text-[var(--text)]">
          {notice}
        </div>
      ) : null}

      {saveError ? (
        <div className="mt-4 rounded-[18px] border border-[rgba(255,109,109,0.25)] bg-[rgba(255,109,109,0.10)] px-4 py-3 text-sm text-[var(--text-soft)]">
          {saveError}
        </div>
      ) : null}

      <section className="mt-4 grid gap-4 xl:grid-cols-[1fr_0.95fr]">
        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Settings</p>
          <h3 className="mt-2 text-2xl font-semibold">Door setup</h3>

          {isLoading ? (
            <div className="mt-6 rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm text-[var(--text-muted)]">
              Loading…
            </div>
          ) : error || !door ? (
            <div className="mt-6 rounded-[20px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-sm text-[var(--text-soft)]">
              Could not load door settings.
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
              <div>
                <label className="block text-sm text-[var(--text-muted)]">Door name</label>
                <input
                  {...register("name", { required: true })}
                  className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                />
              </div>

              <div>
                <label className="block text-sm text-[var(--text-muted)]">Purpose</label>
                <input
                  {...register("purpose")}
                  placeholder="bell, clinic, reception, check-in"
                  className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm text-[var(--text-muted)]">Mode</label>
                  <select
                    {...register("mode")}
                    className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                  >
                    <option value="custom_action">Door bell</option>
                    <option value="queue_join">Queue join</option>
                    <option value="check_in">Check in</option>
                    <option value="open_chat">Visitor chat</option>
                    <option value="subscribe_broadcast">Broadcast</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-[var(--text-muted)]">Active</label>
                  <button
                    type="button"
                    onClick={() => reset({ ...watch(), is_active: !isActive })}
                    className="mt-2 flex w-full items-center justify-between rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-sm font-semibold transition hover:border-[var(--line-strong)]"
                  >
                    <span className="text-[var(--text)]">{isActive ? "Scan allowed" : "Scan disabled"}</span>
                    {isActive ? <ToggleRight className="text-[var(--teal)]" size={20} /> : <ToggleLeft className="text-[var(--text-muted)]" size={20} />}
                  </button>
                </div>
              </div>

              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 text-sm text-[var(--text-muted)]">
                <p className="font-semibold text-[var(--text)]">Mode hint</p>
                <p className="mt-2 leading-6">
                  {mode === "queue_join"
                    ? "Queue doors issue tickets on scan and show up in queue operations."
                    : mode === "check_in"
                      ? "Check-in doors are used for attendance / checkpoint style flows."
                      : mode === "open_chat"
                        ? "Chat doors open visitor conversation flows."
                        : "Door bell is the default entry point for notifications and visitor alerts."}
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <button
                  disabled={saving}
                  className="inline-flex items-center justify-center gap-2 rounded-[18px] bg-[linear-gradient(135deg,#f6b94a,#f39c28)] px-4 py-4 text-sm font-semibold text-[#1a1204] transition hover:brightness-105 disabled:opacity-70"
                >
                  {saving ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                  Save
                </button>
                <button
                  type="button"
                  disabled={!token}
                  onClick={() => copy(token)}
                  className="inline-flex items-center justify-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] px-4 py-4 text-sm font-semibold transition hover:border-[var(--line-strong)] disabled:opacity-60"
                >
                  <Copy size={18} className="text-[var(--teal)]" /> Copy token
                </button>
              </div>
            </form>
          )}
        </article>

        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Door QR</p>
          <h3 className="mt-2 text-2xl font-semibold">Scan preview</h3>

          {!qrValue ? (
            <div className="mt-6 rounded-[20px] border border-dashed border-[var(--line)] bg-[var(--bg-card)] p-8 text-center text-sm text-[var(--text-muted)]">
              QR will appear after the door is created.
            </div>
          ) : (
            <div className="mt-6 space-y-4">
              <div className="rounded-[24px] border border-[var(--line)] bg-[rgba(246,185,74,0.08)] p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-[var(--text)]">{token ? "QR token" : "QR value"}</p>
                    <p className="mt-1 text-xs text-[var(--text-muted)]">This is what the QR encodes right now.</p>
                  </div>
                  <span className="rounded-2xl bg-[var(--amber-soft)] p-2 text-[var(--amber)]">
                    <Shield size={18} />
                  </span>
                </div>
                <div className="mt-4 rounded-[20px] bg-white p-6">
                  <QRCodeSvg value={qrValue} size={180} />
                </div>
                <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                  <p className="text-xs text-[var(--text-muted)] break-all">{qrValue}</p>
                  <button
                    type="button"
                    onClick={() => copy(qrValue)}
                    className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-panel)] px-3 py-2 text-sm font-semibold transition hover:border-[var(--line-strong)]"
                  >
                    <Copy size={16} className="text-[var(--teal)]" /> Copy
                  </button>
                </div>
              </div>

              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-4 text-sm text-[var(--text-muted)]">
                Tip: later we can switch this to encode a public visitor URL (Phase 3 visitor web flow).
              </div>
            </div>
          )}
        </article>
      </section>
    </AdminPage>
  );
}

