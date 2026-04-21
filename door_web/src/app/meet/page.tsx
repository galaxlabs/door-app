import Link from "next/link";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { MapPin } from "lucide-react";
import { MeetActions } from "./MeetActions";

function parseDuration(value: unknown) {
  const parsed = typeof value === "string" ? Number(value) : Number.NaN;
  if (!Number.isFinite(parsed) || parsed < 1) return 1;
  if (parsed > 6) return 6;
  return Math.round(parsed);
}

function extractLatLng(note: string) {
  const match = note.match(/(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)/);
  if (!match) return null;
  const lat = Number(match[1]);
  const lng = Number(match[2]);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  return { lat, lng };
}

type MeetPageProps = {
  searchParams?: Record<string, string | string[] | undefined>;
};

export default function MeetPage({ searchParams = {} }: MeetPageProps) {
  const get = (key: string) => {
    const value = searchParams[key];
    if (Array.isArray(value)) return value[0] ?? "";
    return value ?? "";
  };

  const title = String(get("title")).trim();
  const location = String(get("location")).trim();
  const note = String(get("note")).trim();
  const duration = parseDuration(get("duration"));

  const coords = extractLatLng(note);
  const mapsHref = coords ? `https://www.google.com/maps?q=${coords.lat},${coords.lng}` : "";

  const shareText = [
    title ? `Meet: ${title}` : "",
    location ? `Location: ${location}` : "",
    note ? `Note: ${note}` : "",
    `Duration: ${duration} hour${duration > 1 ? "s" : ""}`,
  ]
    .filter(Boolean)
    .join("\n");

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <AdminPage
        eyebrow="Meeting point"
        title={title || "Meet here"}
        description="Shared meeting details."
        stats={[
          { label: "Duration", value: `${duration}h`, tone: "amber" },
          { label: "Location", value: location ? "Set" : "—", tone: "teal" },
          { label: "Map", value: mapsHref ? "Ready" : "—", tone: "neutral" },
        ]}
      >
        <section className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
          <article className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Details</p>
                <h3 className="mt-2 text-2xl font-semibold">Meeting info</h3>
              </div>
              <MapPin size={18} className="text-[var(--teal)]" />
            </div>

            <div className="mt-6 space-y-3 text-sm text-[var(--text-muted)]">
              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                <p className="text-xs uppercase tracking-[0.24em]">Meet location / title</p>
                <p className="mt-2 text-base font-semibold text-[var(--text)]">{title || "—"}</p>
              </div>
              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                <p className="text-xs uppercase tracking-[0.24em]">Saved location label</p>
                <p className="mt-2 text-base font-semibold text-[var(--text)]">{location || "—"}</p>
              </div>
              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                <p className="text-xs uppercase tracking-[0.24em]">Note</p>
                <pre className="mt-2 whitespace-pre-wrap text-sm text-[var(--text)]">{note || "—"}</pre>
              </div>
            </div>
          </article>

          <article className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-6">
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Actions</p>
            <h3 className="mt-2 text-2xl font-semibold">Share & open</h3>
            <MeetActions shareText={shareText} mapsHref={mapsHref} />
          </article>
        </section>

        <div className="mt-6">
          <Link
            href="/dashboard/profile/meeting-points"
            className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
          >
            Back to meeting points
          </Link>
        </div>
      </AdminPage>
    </main>
  );
}

