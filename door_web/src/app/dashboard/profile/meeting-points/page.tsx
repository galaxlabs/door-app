"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AdminPage } from "@/components/dashboard/AdminPage";
import { ArrowLeft, Copy, MapPin, Plus, Trash2 } from "lucide-react";

type SavedLocation = {
  id: string;
  label: string;
  note?: string;
};

type SavedMeetingPoint = {
  id: string;
  title: string;
  location: string;
  note: string;
  duration: number;
  created_at: number;
};

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

function readNumber(key: string, fallback: number) {
  if (typeof window === "undefined") return fallback;
  const raw = window.localStorage.getItem(key);
  if (!raw) return fallback;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function writeNumber(key: string, value: number) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, String(value));
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

function uid() {
  return `m_${Math.random().toString(16).slice(2)}_${Date.now().toString(16)}`;
}

export default function MeetingPointsPage() {
  const [title, setTitle] = useState("");
  const [note, setNote] = useState("");
  const [duration, setDuration] = useState(1);
  const [locationLabel, setLocationLabel] = useState("");
  const [locations, setLocations] = useState<SavedLocation[]>([]);
  const [meetingPoints, setMeetingPoints] = useState<SavedMeetingPoint[]>([]);
  const [geoStatus, setGeoStatus] = useState<string>("");
  const [defaultDuration, setDefaultDuration] = useState(1);
  const [includeCoords, setIncludeCoords] = useState(true);

  useEffect(() => {
    setLocations(readJson<SavedLocation[]>("door_saved_locations", []));
    setMeetingPoints(readJson<SavedMeetingPoint[]>("door_meeting_points", []));
    const storedDefault = readNumber("door_meeting_default_duration", 1);
    setDefaultDuration(storedDefault);
    setDuration(storedDefault);
    setIncludeCoords(readBool("door_meeting_include_coords", true));
  }, []);

  const selectedLocation = useMemo(() => {
    const normalized = locationLabel.trim().toLowerCase();
    return locations.find((l) => l.label.trim().toLowerCase() === normalized) ?? null;
  }, [locationLabel, locations]);

  const base = useMemo(() => {
    if (typeof window === "undefined") return "";
    return window.location.origin;
  }, []);

  const buildMeetLink = useMemo(() => {
    return (payload: { title: string; location: string; note: string; duration: number }) => {
      if (!base) return "";
      const params = new URLSearchParams();
      if (payload.title.trim()) params.set("title", payload.title.trim());
      if (payload.location.trim()) params.set("location", payload.location.trim());
      if (payload.note.trim()) params.set("note", payload.note.trim());
      params.set("duration", String(payload.duration));
      return `${base}/meet?${params.toString()}`;
    };
  }, [base]);

  const shareLink = useMemo(() => {
    return buildMeetLink({ title, location: locationLabel, note, duration });
  }, [buildMeetLink, duration, locationLabel, note, title]);

  function saveLocation() {
    const label = locationLabel.trim();
    if (!label) return;
    const next: SavedLocation[] = [
      { id: uid(), label, note: "" },
      ...locations.filter((l) => l.label.trim().toLowerCase() !== label.toLowerCase()),
    ];
    setLocations(next);
    writeJson("door_saved_locations", next);
  }

  function removeLocation(id: string) {
    const next = locations.filter((l) => l.id !== id);
    setLocations(next);
    writeJson("door_saved_locations", next);
  }

  function useCurrentLocation() {
    if (typeof window === "undefined") return;
    if (!navigator.geolocation) {
      setGeoStatus("Geolocation not supported.");
      return;
    }
    setGeoStatus("Getting location…");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude.toFixed(6);
        const lng = pos.coords.longitude.toFixed(6);
        setGeoStatus(`Location captured: ${lat}, ${lng}`);
        if (includeCoords) {
          setNote((prev) => {
            const stamp = `Location: ${lat}, ${lng}`;
            if (!prev.trim()) return stamp;
            if (prev.includes(stamp)) return prev;
            return `${prev.trim()}\n${stamp}`;
          });
        }
      },
      () => setGeoStatus("Could not get location."),
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }

  async function copyShare() {
    try {
      await navigator.clipboard.writeText(shareLink);
      alert("Link copied.");
    } catch {
      alert("Copy failed.");
    }
  }

  function saveMeetingPoint() {
    if (!title.trim() && !locationLabel.trim() && !note.trim()) return;
    const entry: SavedMeetingPoint = {
      id: uid(),
      title: title.trim(),
      location: locationLabel.trim(),
      note: note.trim(),
      duration,
      created_at: Date.now(),
    };
    const next = [entry, ...meetingPoints].slice(0, 30);
    setMeetingPoints(next);
    writeJson("door_meeting_points", next);
  }

  async function copyMeetingPoint(point: SavedMeetingPoint) {
    const link = buildMeetLink({
      title: point.title,
      location: point.location,
      note: point.note,
      duration: point.duration,
    });
    try {
      await navigator.clipboard.writeText(link);
      alert("Link copied.");
    } catch {
      alert("Copy failed.");
    }
  }

  function deleteMeetingPoint(id: string) {
    const next = meetingPoints.filter((p) => p.id !== id);
    setMeetingPoints(next);
    writeJson("door_meeting_points", next);
  }

  return (
    <AdminPage
      eyebrow="Profile"
      title="Meeting points"
      description="Create meeting points, save multiple share links, and manage local location labels."
      stats={[
        { label: "Locations", value: String(locations.length), tone: "amber" },
        { label: "Duration", value: `${duration}h`, tone: "teal" },
        { label: "Share", value: shareLink ? "Ready" : "—", tone: "neutral" },
      ]}
    >
      <Link
        href="/dashboard/profile"
        className="inline-flex items-center gap-2 rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-2 text-sm text-[var(--text-muted)] transition hover:text-[var(--text)]"
      >
        <ArrowLeft size={16} /> Back to profile
      </Link>

      <section className="mt-4 grid gap-4 xl:grid-cols-[1fr_0.9fr]">
        <article className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Create</p>
              <h3 className="mt-2 text-2xl font-semibold">Meeting point</h3>
            </div>
            <MapPin size={18} className="text-[var(--teal)]" />
          </div>

          <div className="mt-6 grid gap-4">
            <div>
              <label className="block text-sm text-[var(--text-muted)]">Meet location / title</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Gate 3, Reception, Lobby"
                className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
              />
            </div>

            <div>
              <label className="block text-sm text-[var(--text-muted)]">Note</label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={4}
                placeholder="Write a note…"
                className="mt-2 w-full resize-none rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm text-[var(--text-muted)]">Meet duration</label>
                <select
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                >
                  {[1, 2, 3, 4, 5, 6].map((v) => (
                    <option key={v} value={v}>
                      {v} hour{v > 1 ? "s" : ""}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-[var(--text-muted)]">Saved location label</label>
                <input
                  value={locationLabel}
                  onChange={(e) => setLocationLabel(e.target.value)}
                  placeholder="e.g. Parking A"
                  className="mt-2 w-full rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-4 text-[var(--text)] outline-none transition focus:border-[var(--line-strong)]"
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={saveLocation}
                className="inline-flex items-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-3 text-sm font-semibold transition hover:border-[var(--line-strong)]"
              >
                <Plus size={18} className="text-[var(--amber)]" /> Save location
              </button>
              <button
                type="button"
                onClick={saveMeetingPoint}
                className="inline-flex items-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-3 text-sm font-semibold transition hover:border-[var(--line-strong)]"
              >
                <Plus size={18} className="text-[var(--teal)]" /> Save meeting point
              </button>
              <button
                type="button"
                onClick={useCurrentLocation}
                className="inline-flex items-center gap-2 rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] px-4 py-3 text-sm font-semibold transition hover:border-[var(--line-strong)]"
              >
                <MapPin size={18} className="text-[var(--teal)]" /> Use current location
              </button>
              <button
                type="button"
                onClick={copyShare}
                className="inline-flex items-center gap-2 rounded-[18px] bg-[linear-gradient(135deg,#37d6c5,#239e91)] px-4 py-3 text-sm font-semibold text-[#041412] transition hover:brightness-105"
              >
                <Copy size={18} /> Copy share link
              </button>
            </div>

            <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
              <p className="font-semibold text-[var(--text)]">Settings</p>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div className="rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] p-4">
                  <p className="text-sm font-semibold">Default duration</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">Used when creating new meeting points.</p>
                  <select
                    value={defaultDuration}
                    onChange={(e) => {
                      const next = Number(e.target.value);
                      setDefaultDuration(next);
                      setDuration(next);
                      writeNumber("door_meeting_default_duration", next);
                    }}
                    className="mt-3 w-full rounded-[16px] border border-[var(--line)] bg-[var(--bg-card)] px-3 py-3 text-sm text-[var(--text)] outline-none"
                  >
                    {[1, 2, 3, 4, 5, 6].map((v) => (
                      <option key={v} value={v}>
                        {v} hour{v > 1 ? "s" : ""}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    const next = !includeCoords;
                    setIncludeCoords(next);
                    writeBool("door_meeting_include_coords", next);
                  }}
                  className="rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.02)] p-4 text-left transition hover:border-[var(--line-strong)]"
                >
                  <p className="text-sm font-semibold">Include coordinates in note</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">Current: {includeCoords ? "On" : "Off"}</p>
                </button>
              </div>
            </div>

            {geoStatus ? (
              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 text-sm text-[var(--text-muted)]">
                {geoStatus}
              </div>
            ) : null}

            {selectedLocation ? (
              <div className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4 text-sm text-[var(--text-muted)]">
                Using saved label: <span className="text-[var(--text)] font-semibold">{selectedLocation.label}</span>
              </div>
            ) : null}
          </div>
        </article>

        <div className="space-y-4">
          <article className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Meeting points</p>
            <h3 className="mt-2 text-2xl font-semibold">Saved links</h3>
            <p className="mt-3 text-sm text-[var(--text-muted)]">Saved meeting points are stored locally for now.</p>

            {meetingPoints.length === 0 ? (
              <div className="mt-6 rounded-[24px] border border-dashed border-[var(--line)] bg-[var(--bg-panel)] p-8 text-center text-sm text-[var(--text-muted)]">
                No saved meeting points yet.
              </div>
            ) : (
              <div className="mt-6 grid gap-3">
                {meetingPoints.slice(0, 20).map((point) => (
                  <div key={point.id} className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-[var(--text)]">{point.title || "Meeting point"}</p>
                        <p className="mt-1 text-xs text-[var(--text-muted)]">
                          {point.location ? `Location: ${point.location}` : "No location label"} • {point.duration}h
                        </p>
                        {point.note ? <p className="mt-2 text-xs text-[var(--text-muted)]">{point.note}</p> : null}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => copyMeetingPoint(point)}
                          className="rounded-2xl border border-[rgba(55,214,197,0.22)] bg-[rgba(55,214,197,0.08)] p-2 text-[var(--teal)]"
                          title="Copy link"
                        >
                          <Copy size={18} />
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteMeetingPoint(point.id)}
                          className="rounded-2xl border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-2 text-[var(--danger)]"
                          title="Delete"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </article>

          <article className="rounded-[var(--radius-xl)] border border-[var(--line)] bg-[var(--bg-card)] p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Locations</p>
            <h3 className="mt-2 text-2xl font-semibold">Saved labels</h3>
            <p className="mt-3 text-sm text-[var(--text-muted)]">Location labels are saved locally for now.</p>

            {locations.length === 0 ? (
              <div className="mt-6 rounded-[24px] border border-dashed border-[var(--line)] bg-[var(--bg-panel)] p-8 text-center text-sm text-[var(--text-muted)]">
                No saved locations yet.
              </div>
            ) : (
              <div className="mt-6 grid gap-3">
                {locations.slice(0, 20).map((l) => (
                  <div key={l.id} className="rounded-[20px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold">{l.label}</p>
                        <p className="mt-1 text-xs text-[var(--text-muted)]">{l.note ?? ""}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeLocation(l.id)}
                        className="rounded-2xl border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-2 text-[var(--danger)]"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </article>
        </div>
      </section>
    </AdminPage>
  );
}
