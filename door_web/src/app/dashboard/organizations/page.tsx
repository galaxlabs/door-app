"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Building2, DoorOpen, Globe2, Search, ShieldCheck } from "lucide-react";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { useOrganizations, useQRCodes } from "@/hooks/useApi";

type OrganizationRecord = {
  id: string;
  name: string;
  slug?: string;
  type?: string;
  status?: string;
  website?: string;
  description?: string;
  is_active?: boolean;
};

type QRRecord = {
  id: string;
  organization?: string | null;
};

export default function OrganizationsPage() {
  const [query, setQuery] = useState("");
  const { data, isLoading, error } = useOrganizations();
  const { data: qrData } = useQRCodes();
  const organizations = useMemo(() => (data ?? []) as OrganizationRecord[], [data]);
  const qrCodes = useMemo(() => (qrData ?? []) as QRRecord[], [qrData]);

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return organizations.filter((item) => {
      const haystack = [item.name, item.slug, item.type, item.status, item.website, item.description].join(" ").toLowerCase();
      return haystack.includes(normalizedQuery);
    });
  }, [organizations, query]);

  const orgDoorCount = new Map<string, number>();
  qrCodes.forEach((item) => {
    if (!item.organization) return;
    orgDoorCount.set(item.organization, (orgDoorCount.get(item.organization) ?? 0) + 1);
  });

  const activeCount = organizations.filter((item) => item.is_active).length;

  return (
    <AdminPage
      eyebrow="Organizations"
      title="Real organizations, not empty walls"
      description="This page pulls live organizations so the module feels connected to the rest of the app, with quick visibility into which orgs already have door records attached."
      stats={[
        { label: "Organizations", value: String(organizations.length), tone: "amber" },
        { label: "Active", value: String(activeCount), tone: "teal" },
        { label: "Door-linked", value: String(orgDoorCount.size), tone: "neutral" },
      ]}
    >
      <section className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Discover</p>
          <h3 className="mt-2 text-2xl font-semibold">Search organization space</h3>
          <div className="mt-5 rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-3">
            <div className="flex items-center gap-3">
              <Search size={18} className="text-[var(--amber)]" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search by name, slug, type, website"
                className="w-full bg-transparent py-2 text-[var(--text)] outline-none placeholder:text-[var(--text-muted)]"
              />
            </div>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Link href="/dashboard/doors/create" className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] p-4 transition hover:border-[var(--line-strong)]">
              <p className="font-semibold text-[var(--text)]">Bind a new door</p>
              <p className="mt-1 text-sm text-[var(--text-muted)]">Create a door and attach it to an organization.</p>
            </Link>
            <Link href="/dashboard/doors" className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-card)] p-4 transition hover:border-[var(--line-strong)]">
              <p className="font-semibold text-[var(--text)]">Review live doors</p>
              <p className="mt-1 text-sm text-[var(--text-muted)]">See which entries are already active across teams.</p>
            </Link>
          </div>
          <div className="mt-4 rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-4 text-sm text-[var(--text-muted)]">
            Events, groups, attendance, trips, and emergency modules can plug into this org space as they come online. This page is the front porch instead of a cardboard sign.
          </div>
        </article>

        <article className="glass-panel rounded-[var(--radius-lg)] border border-[var(--line)] p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Live list</p>
              <h3 className="mt-2 text-2xl font-semibold">{filtered.length} visible organizations</h3>
            </div>
            <Building2 className="text-[var(--amber)]" size={18} />
          </div>

          {isLoading ? (
            <div className="mt-6 rounded-[20px] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm text-[var(--text-muted)]">Loading organizations…</div>
          ) : error ? (
            <div className="mt-6 rounded-[20px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-5 text-sm text-[var(--text-soft)]">Could not load organizations. Please confirm the API is reachable.</div>
          ) : filtered.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--line)] bg-[var(--bg-card)] p-8 text-center">
              <Building2 className="mx-auto text-[var(--text-muted)]" size={32} />
              <p className="mt-4 text-lg font-semibold">No organizations found</p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">Once records exist, they will appear here with status, website, and linked door counts.</p>
            </div>
          ) : (
            <div className="mt-6 grid gap-3">
              {filtered.map((item) => (
                <div key={item.id} className="rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-4 transition hover:border-[var(--line-strong)]">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h4 className="text-lg font-semibold text-[var(--text)]">{item.name}</h4>
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.is_active ? "bg-[var(--teal-soft)] text-[var(--text)]" : "bg-[rgba(255,109,109,0.12)] text-[var(--text-soft)]"}`}>
                          {item.is_active ? "Active" : (item.status || "Inactive")}
                        </span>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--text-soft)]">
                        {item.type ? <span className="rounded-full border border-[var(--line)] px-3 py-1">Type: {item.type}</span> : null}
                        {item.slug ? <span className="rounded-full border border-[var(--line)] px-3 py-1">Slug: {item.slug}</span> : null}
                        <span className="rounded-full border border-[var(--line)] px-3 py-1">Doors: {orgDoorCount.get(item.id) ?? 0}</span>
                      </div>
                      {item.description ? <p className="mt-3 text-sm text-[var(--text-muted)]">{item.description}</p> : null}
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-2 text-xs text-[var(--text-muted)]">
                      <span className="rounded-2xl bg-[var(--amber-soft)] p-2 text-[var(--amber)]"><ShieldCheck size={18} /></span>
                      {item.website ? <span className="inline-flex items-center gap-1"><Globe2 size={14} /> live site</span> : null}
                      <span className="inline-flex items-center gap-1"><DoorOpen size={14} /> ready for doors</span>
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
