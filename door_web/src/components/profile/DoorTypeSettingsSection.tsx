"use client";

import { useEffect, useMemo, useState } from "react";
import {
  DOOR_ICON_OPTIONS,
  DOOR_MODE_LABELS,
  DOOR_MODE_OPTIONS,
  DoorFeatureKey,
  DoorMode,
  FEATURE_LABELS,
  StoredDoorType,
  SYSTEM_DOOR_TYPES,
  readCustomDoorTypes,
  saveCustomDoorTypes,
} from "@/lib/doorTypes";
import { Plus, Settings2, Trash2 } from "lucide-react";

type FormState = {
  label: string;
  description: string;
  iconKey: (typeof DOOR_ICON_OPTIONS)[number]["id"];
  mode: DoorMode;
  modeLabel: string;
  purpose: string;
  features: DoorFeatureKey[];
};

const FEATURE_ORDER: DoorFeatureKey[] = [
  "queue",
  "appointments",
  "time_slots",
  "max_tokens",
  "working_hours",
  "sub_doors",
  "live_serving",
  "visitor_log",
  "checkpoints",
  "emergency_profile",
];

function createInitialForm(): FormState {
  return {
    label: "",
    description: "",
    iconKey: "custom",
    mode: "custom_action",
    modeLabel: "",
    purpose: "custom",
    features: ["visitor_log"],
  };
}

function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 32);
}

export default function DoorTypeSettingsSection() {
  const [customTypes, setCustomTypes] = useState<StoredDoorType[]>([]);
  const [form, setForm] = useState<FormState>(() => createInitialForm());
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = readCustomDoorTypes().map(({ icon, source, ...item }) => item);
    setCustomTypes(stored);
  }, []);

  const selectedIcon = useMemo(
    () => DOOR_ICON_OPTIONS.find((item) => item.id === form.iconKey) ?? DOOR_ICON_OPTIONS[DOOR_ICON_OPTIONS.length - 1],
    [form.iconKey]
  );
  const SelectedPreviewIcon = selectedIcon.icon;
  const previewModeLabel = form.modeLabel.trim() || DOOR_MODE_LABELS[form.mode];

  function toggleFeature(feature: DoorFeatureKey) {
    setForm((current) => {
      const exists = current.features.includes(feature);
      const nextFeatures = exists ? current.features.filter((item) => item !== feature) : [...current.features, feature];
      return { ...current, features: nextFeatures };
    });
  }

  function persist(nextTypes: StoredDoorType[]) {
    setCustomTypes(nextTypes);
    saveCustomDoorTypes(nextTypes);
  }

  function addDoorType() {
    const label = form.label.trim();
    const description = form.description.trim();
    if (!label || !description) {
      setError("Type name and description are required.");
      return;
    }

    const id = slugify(label);
    if (!id) {
      setError("Please use a stronger name for the new door type.");
      return;
    }

    if (SYSTEM_DOOR_TYPES.some((item) => item.id === id) || customTypes.some((item) => item.id === id)) {
      setError("A door type with this name already exists.");
      return;
    }

    const next: StoredDoorType = {
      id,
      label,
      description,
      iconKey: form.iconKey,
      mode: form.mode,
      modeLabel: form.modeLabel.trim() || undefined,
      purpose: form.purpose.trim() || "custom",
      features: Array.from(new Set(form.features)),
    };

    persist([...customTypes, next]);
    setForm(createInitialForm());
    setError(null);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2000);
  }

  function removeDoorType(id: string) {
    const next = customTypes.filter((item) => item.id !== id);
    persist(next);
  }

  return (
    <section id="door-type-settings">
      <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Door type settings</p>
      <div className="mt-3 rounded-[22px] border border-[var(--line)] bg-[var(--bg-card)] p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-xl font-semibold">Type & mode names (per user)</h3>
            <p className="mt-2 text-sm text-[var(--text-muted)]">
              Add your own door type and mode naming. This keeps Create Door simple and avoids extra door-level settings.
            </p>
          </div>
          <Settings2 size={18} className="text-[var(--teal)]" />
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {[
            { title: "Clinic queue", mode: "Queue", note: "Type: Specialist Clinic" },
            { title: "Family bell", mode: "Bell", note: "Type: Home main gate" },
            { title: "Checkpoint scan", mode: "Check-in", note: "Type: Warehouse gate" },
          ].map((item) => (
            <div key={item.title} className="rounded-[18px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
              <p className="font-semibold">{item.title}</p>
              <p className="mt-1 text-sm text-[var(--text-muted)]">Mode label: {item.mode}</p>
              <p className="mt-1 text-sm text-[var(--text-muted)]">{item.note}</p>
            </div>
          ))}
        </div>

        {error ? (
          <div className="mt-4 rounded-2xl border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-4 text-sm text-[var(--text)]">
            {error}
          </div>
        ) : null}
        {saved ? (
          <div className="mt-4 rounded-2xl border border-[rgba(55,214,197,0.22)] bg-[rgba(55,214,197,0.08)] p-4 text-sm text-[var(--text)]">
            Saved. This type appears immediately in Create Door.
          </div>
        ) : null}

        <div className="mt-5 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Type name</label>
                <input
                  value={form.label}
                  onChange={(e) => setForm((current) => ({ ...current, label: e.target.value }))}
                  placeholder="e.g. Specialist Clinic"
                  className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(246,185,74,0.35)]"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Purpose</label>
                <input
                  value={form.purpose}
                  onChange={(e) => setForm((current) => ({ ...current, purpose: e.target.value }))}
                  placeholder="clinic"
                  className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(246,185,74,0.35)]"
                />
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Description</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm((current) => ({ ...current, description: e.target.value }))}
                rows={3}
                placeholder="Short summary for the card picker."
                className="w-full resize-none rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(246,185,74,0.35)]"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Mode</label>
                <select
                  value={form.mode}
                  onChange={(e) => setForm((current) => ({ ...current, mode: e.target.value as DoorMode }))}
                  className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none"
                >
                  {DOOR_MODE_OPTIONS.map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Mode display name</label>
                <input
                  value={form.modeLabel}
                  onChange={(e) => setForm((current) => ({ ...current, modeLabel: e.target.value }))}
                  placeholder={DOOR_MODE_LABELS[form.mode]}
                  className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(55,214,197,0.28)]"
                />
                <p className="mt-1 text-xs text-[var(--text-muted)]">You can rename mode text (example: Queue → Token Lane).</p>
              </div>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium text-[var(--text-muted)]">Icon</p>
              <div className="grid grid-cols-3 gap-2">
                {DOOR_ICON_OPTIONS.map((option) => {
                  const Icon = option.icon;
                  const active = form.iconKey === option.id;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => setForm((current) => ({ ...current, iconKey: option.id }))}
                      className={[
                        "rounded-2xl border px-3 py-3 text-center transition",
                        active
                          ? "border-[rgba(246,185,74,0.66)] bg-[rgba(246,185,74,0.14)]"
                          : "border-[var(--line)] bg-[var(--bg-panel)] hover:border-[var(--line-strong)]",
                      ].join(" ")}
                    >
                      <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] text-[var(--amber)]">
                        <Icon size={18} />
                      </div>
                      <p className="mt-2 text-[11px] leading-4 text-[var(--text-muted)]">{option.label}</p>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="rounded-[22px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
              <div className="flex items-start gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] text-[var(--amber)]">
                  <SelectedPreviewIcon size={22} />
                </div>
                <div>
                  <p className="font-semibold">{form.label.trim() || "Preview type"}</p>
                  <p className="mt-1 text-sm text-[var(--text-muted)]">{form.description.trim() || "Description preview for the card selector."}</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">Mode label: {previewModeLabel}</p>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={addDoorType}
              className="inline-flex items-center gap-2 rounded-[18px] bg-[linear-gradient(135deg,#f6b94a,#f39c28)] px-5 py-3 text-sm font-semibold text-[#1a1204] transition hover:brightness-105"
            >
              <Plus size={16} />
              Add Door Type
            </button>
          </div>

          <div>
            <p className="mb-2 text-sm font-medium text-[var(--text-muted)]">Features</p>
            <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
              {FEATURE_ORDER.map((feature) => {
                const active = form.features.includes(feature);
                return (
                  <button
                    key={feature}
                    type="button"
                    onClick={() => toggleFeature(feature)}
                    className={[
                      "flex items-center justify-between rounded-2xl border px-4 py-3 text-left transition",
                      active
                        ? "border-[rgba(55,214,197,0.42)] bg-[rgba(55,214,197,0.10)] text-[var(--text)]"
                        : "border-[var(--line)] bg-[var(--bg-panel)] text-[var(--text-muted)]",
                    ].join(" ")}
                  >
                    <span className="text-sm font-medium">{FEATURE_LABELS[feature]}</span>
                    <span className="text-xs uppercase tracking-[0.18em]">{active ? "On" : "Off"}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="mt-6">
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Saved in this browser</p>
          {customTypes.length === 0 ? (
            <div className="mt-3 rounded-[22px] border border-dashed border-[var(--line)] bg-[var(--bg-panel)] p-6 text-sm text-[var(--text-muted)]">
              No custom door types yet.
            </div>
          ) : (
            <div className="mt-3 grid gap-3">
              {customTypes.map((item) => {
                const iconOption =
                  DOOR_ICON_OPTIONS.find((option) => option.id === item.iconKey) ?? DOOR_ICON_OPTIONS[DOOR_ICON_OPTIONS.length - 1];
                const Icon = iconOption.icon;
                const modeName = item.modeLabel?.trim() || DOOR_MODE_LABELS[item.mode];
                return (
                  <div key={item.id} className="flex flex-wrap items-start justify-between gap-4 rounded-[22px] border border-[var(--line)] bg-[var(--bg-panel)] p-4">
                    <div className="flex min-w-0 items-start gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] text-[var(--amber)]">
                        <Icon size={20} />
                      </div>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="font-semibold">{item.label}</p>
                          <span className="rounded-full border border-[rgba(255,255,255,0.08)] px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
                            {modeName}
                          </span>
                        </div>
                        <p className="mt-2 text-sm text-[var(--text-muted)]">{item.description}</p>
                        <div className="mt-3 flex flex-wrap gap-2">
                          {item.features.map((feature) => (
                            <span
                              key={feature}
                              className="rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] px-3 py-1 text-[11px] text-[var(--text)]"
                            >
                              {FEATURE_LABELS[feature]}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => removeDoorType(item.id)}
                      className="inline-flex items-center gap-2 rounded-[18px] border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] px-4 py-3 text-sm font-semibold text-[var(--text)] transition hover:border-[rgba(255,109,109,0.38)]"
                    >
                      <Trash2 size={16} />
                      Remove
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
