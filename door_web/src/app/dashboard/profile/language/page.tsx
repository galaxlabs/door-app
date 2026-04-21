"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import { normalizeLocale, persistLocale } from "@/lib/locale";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { ArrowLeft, Languages } from "lucide-react";

type Locale = "en" | "ur" | "ar";

export default function LanguagePage() {
  const [current, setCurrent] = useState<Locale>("en");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const res = await api.get("auth/me/");
        if (!mounted) return;
        const locale = normalizeLocale(res.data.locale ?? "en") as Locale;
        setCurrent(locale);
        persistLocale(locale);
      } catch (err: any) {
        if (!mounted) return;
        setError("Could not load profile.");
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  async function setLocale(locale: Locale) {
    setSaving(true);
    setError(null);
    try {
      await api.patch("auth/me/", { locale });
      setCurrent(locale);
      persistLocale(locale);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Could not save language.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AdminPage
      eyebrow="General"
      title="Languages"
      description="Choose a primary language for the admin interface."
      stats={[
        { label: "Current", value: current, tone: "amber" },
        { label: "Status", value: saving ? "Saving" : "Ready", tone: "teal" },
        { label: "Scope", value: "Profile", tone: "neutral" },
      ]}
    >
      <Link
        href="/dashboard/profile"
        className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
      >
        <ArrowLeft size={16} /> Back to profile
      </Link>

      {error ? (
        <div className="mt-4 rounded-[18px] border border-[rgba(255,109,109,0.25)] bg-[rgba(255,109,109,0.10)] px-4 py-3 text-sm text-[var(--text-soft)]">
          {error}
        </div>
      ) : null}

      <section className="mt-4 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Select</p>
            <h3 className="mt-2 text-2xl font-semibold">Language</h3>
          </div>
          <Languages size={18} className="text-[var(--teal)]" />
        </div>

        <div className="mt-6 grid gap-3 md:grid-cols-3">
          {[
            { key: "en" as const, label: "English" },
            { key: "ur" as const, label: "اردو" },
            { key: "ar" as const, label: "العربية" },
          ].map((item) => (
            <button
              key={item.key}
              type="button"
              disabled={saving}
              onClick={() => setLocale(item.key)}
              className={`rounded-[20px] border p-5 text-left transition disabled:opacity-70 ${
                current === item.key
                  ? "border-[var(--line-strong)] bg-[var(--amber-soft)]"
                  : "border-[var(--line)] bg-[var(--bg-panel)] hover:border-[var(--line-strong)]"
              }`}
            >
              <p className="text-lg font-semibold">{item.label}</p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">{current === item.key ? "Selected" : "Tap to select"}</p>
            </button>
          ))}
        </div>
      </section>
    </AdminPage>
  );
}
