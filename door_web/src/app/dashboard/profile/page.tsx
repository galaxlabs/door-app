"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { normalizeLocale, persistLocale } from "@/lib/locale";
import { AdminPage } from "@/components/dashboard/AdminPage";
import DoorTypeSettingsSection from "@/components/profile/DoorTypeSettingsSection";
import {
  Bell,
  BookOpen,
  DoorOpen,
  History,
  Loader2,
  LogOut,
  MapPin,
  Settings2,
  Shield,
  Trash2,
  User,
} from "lucide-react";

type MeResponse = {
  id: string;
  public_id: string;
  email: string;
  phone_number: string;
  full_name: string;
  intro?: string;
  age?: number | null;
  avatar?: string | null;
  locale: "en" | "ar" | "ur";
  timezone: string;
};

type VisitorCardForm = {
  full_name: string;
  intro: string;
  age: number | null;
  locale: "en" | "ar" | "ur";
  timezone: string;
};

function initials(value: string) {
  const parts = value.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "U";
  const first = parts[0]?.[0] ?? "U";
  const second = parts.length > 1 ? parts[1]?.[0] ?? "" : "";
  return (first + second).toUpperCase();
}

function readBool(key: string, fallback: boolean) {
  if (typeof window === "undefined") return fallback;
  const raw = window.localStorage.getItem(key);
  if (raw === null) return fallback;
  return raw === "true";
}

function writeBool(key: string, value: boolean) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, value ? "true" : "false");
}

export default function ProfilePage() {
  const router = useRouter();
  const [me, setMe] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const { register, handleSubmit, reset, formState } = useForm<VisitorCardForm>({
    defaultValues: { full_name: "", intro: "", age: null, locale: "en", timezone: "UTC" },
  });

  useEffect(() => {
    setNotificationsEnabled(readBool("door_notifications_enabled", true));
  }, []);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get("auth/me/");
        if (!mounted) return;
        setMe(res.data as MeResponse);
        persistLocale(normalizeLocale(res.data.locale));
        reset({
          full_name: res.data.full_name ?? "",
          intro: res.data.intro ?? "",
          age: res.data.age ?? null,
          locale: (res.data.locale ?? "en") as VisitorCardForm["locale"],
          timezone: res.data.timezone ?? "UTC",
        });
      } catch (err: any) {
        if (!mounted) return;
        const detail = err?.response?.data?.detail;
        setError(typeof detail === "string" ? detail : "Could not load profile. Please sign in again.");
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [reset]);

  const headline = useMemo(() => {
    if (!me) return "—";
    return me.intro?.trim() ? me.intro.trim() : "Profile used across doors and visitor flows.";
  }, [me]);

  async function saveVisitorCard(values: VisitorCardForm) {
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const res = await api.patch("auth/me/", {
        full_name: values.full_name,
        intro: values.intro,
        age: values.age,
        locale: values.locale,
        timezone: values.timezone,
      });
      setMe(res.data as MeResponse);
      persistLocale(normalizeLocale(res.data.locale ?? values.locale));
      setSaved(true);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Could not save profile.");
    } finally {
      setSaving(false);
    }
  }

  function signOut() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/auth/login");
  }

  function deleteLocalData() {
    localStorage.removeItem("door_notifications_enabled");
    localStorage.removeItem("door_theme");
    localStorage.removeItem("door_meeting_points");
    localStorage.removeItem("door_saved_locations");
    setNotificationsEnabled(true);
  }

  return (
    <AdminPage
      eyebrow="Profile"
      title="Account"
      description="Profile, privacy, visitor card, meeting points, and activity shortcuts."
      stats={[
        { label: "ID", value: me?.public_id ?? "—", tone: "neutral" },
        { label: "Age", value: me?.age ? String(me.age) : "—", tone: "amber" },
        { label: "Locale", value: me?.locale ?? "—", tone: "teal" },
      ]}
    >
      <div className="space-y-6">
        <section className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="relative h-16 w-16 overflow-hidden rounded-full border border-[var(--line-strong)] bg-[rgba(246,185,74,0.12)]">
                {me?.avatar ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={me.avatar} alt="" className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-xl font-semibold text-[var(--amber)]">
                    {initials(me?.full_name ?? "User")}
                  </div>
                )}
              </div>
              <div className="min-w-0">
                <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Intro</p>
                <p className="mt-2 text-lg font-semibold">{headline}</p>
                <div className="mt-2 flex flex-wrap gap-2 text-sm text-[var(--text-muted)]">
                  <span className="rounded-full border border-[var(--line)] bg-[var(--bg-panel)] px-3 py-1">
                    Name: {me?.full_name ?? "—"}
                  </span>
                  <span className="rounded-full border border-[var(--line)] bg-[var(--bg-panel)] px-3 py-1">
                    Mobile: {me?.phone_number ?? "—"}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link
                href="/dashboard/doors/create"
                className="inline-flex items-center gap-2 rounded-[18px] bg-[linear-gradient(135deg,#f6b94a,#f39c28)] px-4 py-3 text-sm font-semibold text-[#1a1204] transition hover:brightness-105"
              >
                <DoorOpen size={18} />
                Create doors
              </Link>
              <Link
                href="/dashboard/doors"
                className="inline-flex items-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-3 text-sm font-semibold text-[var(--text)] transition hover:border-[var(--line-strong)]"
              >
                Manage doors
              </Link>
            </div>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <Link
              href="/dashboard/profile/guide"
              className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 transition hover:border-[var(--line-strong)]"
            >
              <div className="flex items-center gap-3">
                <BookOpen size={18} className="text-[var(--teal)]" />
                <div>
                  <p className="font-semibold">Quick guide</p>
                  <p className="mt-1 text-sm text-[var(--text-muted)]">How doors, QR, and visitor flows work.</p>
                </div>
              </div>
            </Link>

            <Link
              href="/dashboard/profile/activity"
              className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 transition hover:border-[var(--line-strong)]"
            >
              <div className="flex items-center gap-3">
                <History size={18} className="text-[var(--amber)]" />
                <div>
                  <p className="font-semibold">All activity</p>
                  <p className="mt-1 text-sm text-[var(--text-muted)]">Open history records.</p>
                </div>
              </div>
            </Link>

            <a
              href="#door-type-settings"
              className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 transition hover:border-[var(--line-strong)]"
            >
              <div className="flex items-center gap-3">
                <Settings2 size={18} className="text-[var(--teal)]" />
                <div>
                  <p className="font-semibold">Door type settings</p>
                  <p className="mt-1 text-sm text-[var(--text-muted)]">Create your own type and mode names.</p>
                </div>
              </div>
            </a>
          </div>
        </section>

        <section>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Activity</p>
          <Link
            href="/dashboard/profile/activity"
            className="mt-3 block rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5 transition hover:border-[var(--line-strong)]"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-lg font-semibold">All activity</p>
                <p className="mt-2 text-sm text-[var(--text-muted)]">Open activity history and records.</p>
              </div>
              <span className="rounded-2xl bg-[var(--amber-soft)] p-2 text-[var(--amber)]">
                <History size={18} />
              </span>
            </div>
          </Link>
        </section>

        <section>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Meeting points</p>
          <Link
            href="/dashboard/profile/meeting-points"
            className="mt-3 block rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5 transition hover:border-[var(--line-strong)]"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-lg font-semibold">Meeting points</p>
                <p className="mt-2 text-sm text-[var(--text-muted)]">Create and share a meeting point link.</p>
              </div>
              <span className="rounded-2xl bg-[var(--teal-soft)] p-2 text-[var(--teal)]">
                <MapPin size={18} />
              </span>
            </div>
          </Link>
        </section>

        <section>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">My visitor card</p>
          <div className="mt-3 rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5">
            {loading ? (
              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-5 text-sm text-[var(--text-muted)]">
                Loading…
              </div>
            ) : error ? (
              <div className="rounded-[20px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-sm text-[var(--text-soft)]">
                {error}
              </div>
            ) : !me ? (
              <div className="rounded-[20px] border border-dashed border-[var(--line)] bg-[var(--bg-panel)] p-8 text-center text-sm text-[var(--text-muted)]">
                No profile loaded.
              </div>
            ) : (
              <form onSubmit={handleSubmit(saveVisitorCard)} className="space-y-4">
                <div className="flex flex-wrap items-start gap-4">
                  <div className="relative h-16 w-16 overflow-hidden rounded-full border border-[var(--line)] bg-[var(--bg-panel)]">
                    <label className="group absolute inset-0 cursor-pointer">
                      {me.avatar ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={me.avatar} alt="" className="h-full w-full object-cover opacity-90 transition group-hover:opacity-70" />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center text-xl font-semibold text-[var(--amber)]">
                          {initials(me.full_name)}
                        </div>
                      )}
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={() => alert("Photo upload will be wired next.")}
                      />
                    </label>
                  </div>
                  <div className="min-w-[260px] flex-1">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <label className="block text-sm text-[var(--text-muted)]">Name</label>
                        <input
                          {...register("full_name", { required: true })}
                          className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-[var(--text-muted)]">Age</label>
                        <input
                          type="number"
                          min={1}
                          max={120}
                          {...register("age", { valueAsNumber: true })}
                          className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                        />
                      </div>
                    </div>
                    <div className="mt-4">
                      <label className="block text-sm text-[var(--text-muted)]">Intro</label>
                      <input
                        {...register("intro")}
                        placeholder="Short intro line…"
                        className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                      />
                    </div>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="block text-sm text-[var(--text-muted)]">Phone</label>
                    <input
                      value={me.phone_number}
                      readOnly
                      className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] px-4 py-4 text-[var(--text-muted)] outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-[var(--text-muted)]">Email</label>
                    <input
                      value={me.email}
                      readOnly
                      className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] px-4 py-4 text-[var(--text-muted)] outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-[var(--text-muted)]">Random ID</label>
                    <input
                      value={me.public_id}
                      readOnly
                      className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] px-4 py-4 text-[var(--text-muted)] outline-none"
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="block text-sm text-[var(--text-muted)]">Language</label>
                    <select
                      {...register("locale")}
                      className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                    >
                      <option value="en">English</option>
                      <option value="ur">اردو</option>
                      <option value="ar">العربية</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-[var(--text-muted)]">Timezone</label>
                    <input
                      {...register("timezone")}
                      placeholder="UTC"
                      className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                    />
                  </div>
                </div>

                <button
                  disabled={saving || !formState.isDirty}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-[18px] bg-[linear-gradient(135deg,#37d6c5,#239e91)] px-4 py-4 font-semibold text-[#041412] transition hover:brightness-105 disabled:opacity-70"
                >
                  {saving ? <Loader2 size={18} className="animate-spin" /> : <User size={18} />}
                  Save visitor card
                </button>

                {saved ? (
                  <div className="rounded-[20px] border border-[rgba(55,214,197,0.22)] bg-[rgba(55,214,197,0.08)] p-4 text-sm text-[var(--text)]">
                    Saved.
                  </div>
                ) : null}
              </form>
            )}
          </div>
        </section>

        <section>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">General</p>
          <div className="mt-3 rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="rounded-2xl bg-[var(--amber-soft)] p-2 text-[var(--amber)]">
                  <Bell size={18} />
                </span>
                <div>
                  <p className="font-semibold">Notifications</p>
                  <p className="text-sm text-[var(--text-muted)]">Golden = on, gray = off</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {[
                  { value: true, label: "On" },
                  { value: false, label: "Off" },
                ].map((opt) => (
                  <button
                    key={opt.label}
                    type="button"
                    onClick={() => {
                      setNotificationsEnabled(opt.value);
                      writeBool("door_notifications_enabled", opt.value);
                    }}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      notificationsEnabled === opt.value
                        ? "border border-[var(--line-strong)] bg-[var(--amber-soft)] text-[var(--text)]"
                        : "border border-[var(--line)] bg-[rgba(255,255,255,0.02)] text-[var(--text-muted)] hover:text-[var(--text)]"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <button
                type="button"
                onClick={() => localStorage.setItem("door_theme", "midnight")}
                className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 text-left transition hover:border-[var(--line-strong)]"
              >
                <p className="font-semibold">Theme</p>
                <p className="mt-1 text-sm text-[var(--text-muted)]">Midnight amber</p>
              </button>
              <Link
                href="/dashboard/profile/language"
                className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 transition hover:border-[var(--line-strong)]"
              >
                <p className="font-semibold">Languages</p>
                <p className="mt-1 text-sm text-[var(--text-muted)]">English / اردو / العربية</p>
              </Link>
            </div>
          </div>
        </section>

        <DoorTypeSettingsSection />

        <section>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Security</p>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <Link
              href="/dashboard/profile/privacy"
              className="rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5 transition hover:border-[var(--line-strong)]"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold">Privacy</p>
                  <p className="mt-2 text-sm text-[var(--text-muted)]">Save photo and analytics options.</p>
                </div>
                <span className="rounded-2xl bg-[rgba(255,255,255,0.03)] p-2 text-[var(--text-muted)]">
                  <Shield size={18} />
                </span>
              </div>
            </Link>
            <button
              type="button"
              onClick={deleteLocalData}
              className="rounded-[22px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-left transition hover:border-[rgba(255,109,109,0.35)]"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-[var(--text)]">Delete data</p>
                  <p className="mt-2 text-sm text-[var(--text-soft)]">Clears local settings and meeting points.</p>
                </div>
                <span className="rounded-2xl bg-[rgba(255,109,109,0.12)] p-2 text-[var(--danger)]">
                  <Trash2 size={18} />
                </span>
              </div>
            </button>
          </div>
        </section>

        <section>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Account</p>
          <div className="mt-3 rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5">
            <button
              type="button"
              onClick={signOut}
              className="inline-flex w-full items-center justify-center gap-2 rounded-[18px] border border-[rgba(255,109,109,0.25)] bg-[rgba(255,109,109,0.10)] px-4 py-4 text-sm font-semibold text-[var(--text)] transition hover:border-[rgba(255,109,109,0.35)]"
            >
              <LogOut size={18} />
              Sign out
            </button>
          </div>
        </section>

        <section>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">About</p>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <div className="rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5">
              <p className="text-sm text-[var(--text-muted)]">Version</p>
              <p className="mt-2 text-2xl font-semibold">0.1.0</p>
            </div>
            <Link
              href="/dashboard/profile/guide"
              className="rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5 transition hover:border-[var(--line-strong)]"
            >
              <p className="text-lg font-semibold">Guide</p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">Open the quick guide.</p>
            </Link>
            <button
              type="button"
              onClick={() => alert("Rate us flow can be wired later.")}
              className="rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-left transition hover:border-[var(--line-strong)]"
            >
              <p className="text-lg font-semibold">Rate us</p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">Share feedback.</p>
            </button>
          </div>
        </section>
      </div>
    </AdminPage>
  );
}
