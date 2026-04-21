"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { ArrowLeft, ShieldCheck } from "lucide-react";

function read(key: string, fallback: boolean) {
  if (typeof window === "undefined") return fallback;
  const raw = window.localStorage.getItem(key);
  if (raw === null) return fallback;
  return raw === "true";
}

function write(key: string, value: boolean) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, value ? "true" : "false");
}

export default function PrivacyPage() {
  const [savePhoto, setSavePhoto] = useState(true);
  const [shareAnalytics, setShareAnalytics] = useState(false);

  useEffect(() => {
    setSavePhoto(read("door_privacy_save_photo", true));
    setShareAnalytics(read("door_privacy_share_analytics", false));
  }, []);

  return (
    <AdminPage
      eyebrow="Security"
      title="Privacy"
      description="Local privacy preferences for now. App policy text will be added later."
      stats={[
        { label: "Save photo", value: savePhoto ? "On" : "Off", tone: "amber" },
        { label: "Analytics", value: shareAnalytics ? "On" : "Off", tone: "teal" },
        { label: "Policy", value: "Draft", tone: "neutral" },
      ]}
    >
      <Link
        href="/dashboard/profile"
        className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
      >
        <ArrowLeft size={16} /> Back to profile
      </Link>

      <section className="mt-4 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Options</p>
            <h3 className="mt-2 text-2xl font-semibold">Privacy controls</h3>
          </div>
          <ShieldCheck size={18} className="text-[var(--amber)]" />
        </div>

        <div className="mt-6 grid gap-3">
          <button
            type="button"
            onClick={() => {
              const next = !savePhoto;
              setSavePhoto(next);
              write("door_privacy_save_photo", next);
            }}
            className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 text-left transition hover:border-[var(--line-strong)]"
          >
            <p className="font-semibold">Save photo</p>
            <p className="mt-1 text-sm text-[var(--text-muted)]">Current: {savePhoto ? "On" : "Off"}</p>
          </button>

          <button
            type="button"
            onClick={() => {
              const next = !shareAnalytics;
              setShareAnalytics(next);
              write("door_privacy_share_analytics", next);
            }}
            className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 text-left transition hover:border-[var(--line-strong)]"
          >
            <p className="font-semibold">Share analytics</p>
            <p className="mt-1 text-sm text-[var(--text-muted)]">Current: {shareAnalytics ? "On" : "Off"}</p>
          </button>

          <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
            <p className="font-semibold">Privacy policy</p>
            <p className="mt-1 text-sm text-[var(--text-muted)]">We’ll write the app policy text here later.</p>
            <p className="mt-3 text-sm text-[var(--teal)] underline decoration-[rgba(55,214,197,0.35)]">View full Privacy Policy</p>
          </div>
        </div>
      </section>
    </AdminPage>
  );
}

