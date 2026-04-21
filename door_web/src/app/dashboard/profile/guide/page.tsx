import Link from "next/link";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { ArrowLeft } from "lucide-react";

export default function GuidePage() {
  return (
    <AdminPage
      eyebrow="Profile"
      title="Quick guide"
      description="Short guide for the current MVP flows. (We’ll expand this later.)"
      stats={[
        { label: "Focus", value: "Profile → Doors", tone: "amber" },
        { label: "Next", value: "Doors UI", tone: "teal" },
        { label: "Mode", value: "MVP", tone: "neutral" },
      ]}
    >
      <Link
        href="/dashboard/profile"
        className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
      >
        <ArrowLeft size={16} /> Back to profile
      </Link>

      <section className="mt-4 rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-6 text-sm leading-7 text-[var(--text-muted)]">
        <p className="text-[var(--text)] font-semibold">1) Profile & visitor card</p>
        <p>Set your name, intro, age, language, and timezone. These details appear in visitor flows later.</p>

        <p className="mt-6 text-[var(--text)] font-semibold">2) Doors</p>
        <p>Create doors as mode-driven QR entries. Use queue doors when you want token issuance and queue operations.</p>

        <p className="mt-6 text-[var(--text)] font-semibold">3) Activity</p>
        <p>Open Activity to review recent records.</p>

        <p className="mt-6 text-[var(--text)] font-semibold">4) Meeting points</p>
        <p>Create a meeting point, save locations, and share a link.</p>
      </section>
    </AdminPage>
  );
}

