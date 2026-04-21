"use client";

import { useState } from "react";
import Link from "next/link";
import { Copy, MapPin } from "lucide-react";

type MeetActionsProps = {
  shareText: string;
  mapsHref: string;
};

export function MeetActions({ shareText, mapsHref }: MeetActionsProps) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(shareText);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      // Ignore; browser may block clipboard.
    }
  }

  return (
    <div className="mt-6 grid gap-3">
      <button
        type="button"
        onClick={copy}
        className="inline-flex items-center justify-center gap-2 rounded-[18px] bg-[linear-gradient(135deg,#37d6c5,#239e91)] px-4 py-4 text-sm font-semibold text-[#041412] transition hover:brightness-105"
      >
        <Copy size={18} />
        {copied ? "Copied" : "Copy details"}
      </button>

      {mapsHref ? (
        <a
          href={mapsHref}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center justify-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-sm font-semibold transition hover:border-[var(--line-strong)]"
        >
          <MapPin size={18} className="text-[var(--teal)]" /> Open in maps
        </a>
      ) : (
        <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 text-sm text-[var(--text-muted)]">
          To enable maps, include coordinates like <span className="text-[var(--text)]">31.5204, 74.3587</span> in the note.
        </div>
      )}

      <Link
        href="/dashboard/profile/meeting-points"
        className="inline-flex items-center justify-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-sm font-semibold transition hover:border-[var(--line-strong)]"
      >
        Edit meeting points
      </Link>

      <Link
        href="/dashboard"
        className="inline-flex items-center justify-center gap-2 rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] px-4 py-4 text-sm font-semibold text-[var(--text-muted)] transition hover:text-[var(--text)]"
      >
        Open Door App
      </Link>
    </div>
  );
}

