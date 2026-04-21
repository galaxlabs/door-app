"use client";

import Link from "next/link";
import { useMemo, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useOrganizations, useQueues } from "@/hooks/useApi";
import {
  DOOR_TYPES_UPDATED_EVENT,
  DoorTypeDefinition,
  FEATURE_LABELS,
  getAllDoorTypes,
  getDoorModeLabel,
} from "@/lib/doorTypes";
import {
  ArrowLeft,
  Settings2,
  Sparkles,
} from "lucide-react";

type CreateDoorClientProps = {
  initialType?: string;
};

type CreatedDoor = {
  id: string;
  label?: string;
  name?: string;
  mode?: string;
  purpose?: string;
  qr_token?: string;
  image_url?: string;
};

export default function CreateDoorClient({ initialType }: CreateDoorClientProps) {
  const router = useRouter();
  const [doorTypes, setDoorTypes] = useState<DoorTypeDefinition[]>(() => getAllDoorTypes());
  const [selectedType, setSelectedType] = useState("home");
  const [doorName, setDoorName] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<CreatedDoor | null>(null);

  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [organization, setOrganization] = useState("");
  const [queue, setQueue] = useState("");

  const [hasMultipleDoctors, setHasMultipleDoctors] = useState(false);
  const [requireAppointments, setRequireAppointments] = useState(false);
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("17:00");
  const [maxTokenCount, setMaxTokenCount] = useState("120");

  const [bloodGroup, setBloodGroup] = useState("");
  const [medicalConditions, setMedicalConditions] = useState("");
  const [emergencyContacts, setEmergencyContacts] = useState<string[]>(["", ""]);

  const [profileNotice, setProfileNotice] = useState<string | null>(null);

  const selectedTypeDef = useMemo(
    () => doorTypes.find((t) => t.id === selectedType) ?? doorTypes[0],
    [doorTypes, selectedType]
  );

  const { data: orgData } = useOrganizations();
  const { data: queueData } = useQueues();

  useEffect(() => {
    setDoorTypes(getAllDoorTypes());
  }, []);

  useEffect(() => {
    function syncDoorTypes() {
      setDoorTypes(getAllDoorTypes());
    }
    window.addEventListener(DOOR_TYPES_UPDATED_EVENT, syncDoorTypes);
    return () => {
      window.removeEventListener(DOOR_TYPES_UPDATED_EVENT, syncDoorTypes);
    };
  }, []);

  useEffect(() => {
    const normalized = String(initialType ?? "").toLowerCase().trim();
    const alias: Record<string, string> = {
      "shop/factory": "shop",
      "shop-factory": "shop",
      shop_factory: "shop",
      factory: "shop",
      "hospital/clinic": "clinic",
      "clinic/hospital": "clinic",
      hospital: "clinic",
      "office/business": "office",
      "office-business": "office",
      office_business: "office",
      business: "office",
      "education/school": "school",
      "education-school": "school",
      education_school: "school",
      education: "school",
      "trip log": "trip",
      "trip-log": "trip",
      trip_log: "trip",
      "check points": "checkpoint",
      "check-points": "checkpoint",
      checkpoints: "checkpoint",
      emergency: "emergency",
    };
    const match = doorTypes.find((t) => t.id === normalized);
    if (match) {
      setSelectedType(match.id);
      return;
    }
    if (alias[normalized]) setSelectedType(alias[normalized]);
  }, [doorTypes, initialType]);

  useEffect(() => {
    if (!selectedTypeDef) return;
    if (doorName.trim()) return;
    setDoorName(selectedTypeDef.label);
  }, [selectedTypeDef, doorName]);

  useEffect(() => {
    let mounted = true;
    async function loadMe() {
      try {
        const res = await api.get("/auth/me/");
        const fullName = String(res.data?.full_name ?? "").trim();
        if (!mounted) return;
        if (!fullName) {
          setProfileNotice("Tip: Set your name in Profile for cleaner visitor logs. Doors still work without it.");
        } else {
          setProfileNotice(null);
        }
      } catch {
        if (mounted) setProfileNotice(null);
      }
    }
    loadMe();
    return () => {
      mounted = false;
    };
  }, []);

  async function submit() {
    if (!doorName.trim()) {
      setError("Door name is required.");
      return;
    }

    setSaving(true);
    setError(null);
    setCreated(null);

    try {
      const metadata_json: any = {
        door_type: selectedTypeDef.id,
        door_type_label: selectedTypeDef.label,
        mode_label: getDoorModeLabel(selectedTypeDef.mode, selectedTypeDef.modeLabel),
        purpose: selectedTypeDef.purpose,
        ui_preset: "d-app",
        template_source: selectedTypeDef.source,
        template_features: selectedTypeDef.features,
        template_icon: selectedTypeDef.iconKey,
      };

      if (
        selectedTypeDef.features.includes("queue") ||
        selectedTypeDef.features.includes("appointments") ||
        selectedTypeDef.features.includes("time_slots") ||
        selectedTypeDef.features.includes("max_tokens") ||
        selectedTypeDef.features.includes("sub_doors")
      ) {
        metadata_json.flow = {
          has_multiple_doctors: hasMultipleDoctors,
          require_appointments: requireAppointments,
          from_time: startTime || null,
          to_time: endTime || null,
          max_queue_token_no: maxTokenCount ? Number(maxTokenCount) : null,
        };
      }

      if (selectedTypeDef.features.includes("emergency_profile")) {
        metadata_json.emergency = {
          blood_group: bloodGroup.trim(),
          medical_conditions: medicalConditions.trim(),
          contacts: emergencyContacts.map((c) => c.trim()).filter(Boolean),
        };
      }

      const payload = {
        entity_type: queue ? "queue" : "organization",
        organization: organization || null,
        queue: queue || null,
        name: doorName.trim(),
        purpose: selectedTypeDef.purpose,
        mode: selectedTypeDef.mode,
        payload_type: selectedTypeDef.mode,
        payload_data: metadata_json,
        action_payload: metadata_json,
        metadata_json,
        is_active: true,
        status: "active",
      };

      const res = await api.post("/qr/codes/", payload);
      setCreated(res.data as CreatedDoor);
      router.push(`/dashboard/qr?focus=${res.data?.id}`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Could not create door. Please check authentication and try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-2 pb-24 md:p-4">
      <div className="mx-auto w-full max-w-7xl">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link href="/dashboard/doors" className="p-2 -ml-2 text-[var(--text-muted)] transition-colors hover:text-white">
              <ArrowLeft className="h-6 w-6" />
            </Link>
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-[var(--text-muted)]">Doors</p>
              <h2 className="text-2xl font-bold tracking-tight text-white">Create New Door</h2>
            </div>
          </div>
          <Link
            href="/dashboard/profile#door-type-settings"
            className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] bg-[rgba(18,18,18,0.88)] px-4 py-3 text-sm font-semibold text-[var(--text)] transition hover:border-[var(--line-strong)]"
          >
            <Settings2 className="h-4 w-4 text-[var(--teal)]" />
            Type settings in Profile
          </Link>
        </div>

        {profileNotice ? (
          <div className="mb-5 rounded-2xl border border-[rgba(246,185,74,0.30)] bg-[rgba(246,185,74,0.10)] p-4 text-sm text-[var(--text)]">
            {profileNotice}
          </div>
        ) : null}

        {error ? (
          <div className="mb-5 rounded-2xl border border-[rgba(255,109,109,0.25)] bg-[rgba(255,109,109,0.10)] p-4 text-sm text-[var(--text)]">
            {error}
          </div>
        ) : null}

        <section className="mb-6 rounded-[30px] border border-[var(--line)] bg-[linear-gradient(145deg,rgba(246,185,74,0.12),rgba(55,214,197,0.06))] p-5 md:p-6">
          <div className="grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
            <div>
              <p className="text-xs uppercase tracking-[0.34em] text-[var(--text-muted)]">Door templates</p>
              <h3 className="mt-3 text-3xl font-semibold text-white">Pick a type in one swipe</h3>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-[var(--text-muted)]">
                We removed the cramped scroll-and-select flow. Each door type now uses a medium-size horizontal card, and custom
                types can be added from Profile settings.
              </p>
            </div>

            <div className="rounded-[26px] border border-[rgba(255,255,255,0.08)] bg-[rgba(7,10,12,0.58)] p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Selected</p>
                  <h4 className="mt-2 text-2xl font-semibold text-white">{selectedTypeDef.label}</h4>
                </div>
                <div className="rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">
                  {selectedTypeDef.source === "custom" ? "Custom" : "System"}
                </div>
              </div>
              <p className="mt-3 text-sm leading-6 text-[var(--text-muted)]">{selectedTypeDef.description}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full border border-[rgba(55,214,197,0.26)] bg-[rgba(55,214,197,0.08)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--teal)]">
                  Mode: {getDoorModeLabel(selectedTypeDef.mode, selectedTypeDef.modeLabel)}
                </span>
                {selectedTypeDef.features.map((feature) => (
                  <span
                    key={feature}
                    className="rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] px-3 py-1 text-xs font-medium text-[var(--text)]"
                  >
                    {FEATURE_LABELS[feature]}
                  </span>
                ))}
              </div>
              {selectedTypeDef.features.includes("live_serving") ? (
                <div className="mt-4 rounded-2xl border border-[rgba(55,214,197,0.22)] bg-[rgba(55,214,197,0.08)] p-4 text-sm text-[var(--text)]">
                  Queue members who join with QR can receive serving-now and estimated-time updates, so they only come forward at
                  the right time.
                </div>
              ) : null}
            </div>
          </div>
        </section>

        <div className="space-y-6 lg:grid lg:grid-cols-[1.2fr_0.8fr] lg:items-start lg:gap-6 lg:space-y-0">
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <label className="block text-sm font-bold text-white">Select Door Type</label>
              <span className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">Horizontal cards</span>
            </div>
            <div className="flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2">
              {doorTypes.map((item) => {
                const Icon = item.icon;
                const isSelected = selectedType === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedType(item.id)}
                    className={[
                      "min-h-[196px] min-w-[250px] snap-start rounded-[28px] border p-5 text-left transition-all md:min-w-[292px]",
                      "flex flex-col justify-between gap-5",
                      isSelected
                        ? "border-[rgba(246,185,74,0.78)] bg-[linear-gradient(160deg,rgba(246,185,74,0.16),rgba(246,185,74,0.05))] shadow-[0_20px_60px_rgba(246,185,74,0.10)]"
                        : "border-[var(--line)] bg-[rgba(18,18,18,0.90)] hover:border-[rgba(255,255,255,0.16)]",
                    ].join(" ")}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div
                        className={[
                          "flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border transition-colors",
                          isSelected
                            ? "border-[rgba(246,185,74,0.35)] bg-[rgba(246,185,74,0.18)] text-[var(--amber)]"
                            : "border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] text-[var(--text-muted)]",
                        ].join(" ")}
                      >
                        <Icon className="h-6 w-6" />
                      </div>
                      <span className="rounded-full border border-[rgba(255,255,255,0.08)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">
                        {item.source === "custom" ? "Custom" : "Preset"}
                      </span>
                    </div>

                    <div>
                      <h3 className={["text-lg font-bold leading-tight", isSelected ? "text-[var(--amber)]" : "text-white"].join(" ")}>
                        {item.label}
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">{item.description}</p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {item.features.slice(0, 3).map((feature) => (
                        <span
                          key={feature}
                          className="rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] px-3 py-1 text-[11px] font-medium text-[var(--text)]"
                        >
                          {FEATURE_LABELS[feature]}
                        </span>
                      ))}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="space-y-4 lg:sticky lg:top-4">
            <div className="space-y-5 rounded-[30px] border border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-5">
              <div className="rounded-[24px] border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] p-4">
                <div className="flex items-start gap-3">
                  <Sparkles className="mt-0.5 h-5 w-5 text-[var(--amber)]" />
                  <div>
                    <p className="font-semibold text-white">Simple create flow</p>
                    <p className="mt-1 text-sm leading-6 text-[var(--text-muted)]">
                      Start with the type, name the door, then add queue, appointment, time-slot, or emergency details only when
                      they matter.
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Door Name</label>
                <input
                  type="text"
                  value={doorName}
                  onChange={(e) => setDoorName(e.target.value)}
                  placeholder={`e.g. ${selectedTypeDef.label}`}
                  className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(246,185,74,0.35)]"
                />
              </div>

              {(selectedTypeDef.features.includes("queue") ||
                selectedTypeDef.features.includes("appointments") ||
                selectedTypeDef.features.includes("time_slots") ||
                selectedTypeDef.features.includes("max_tokens") ||
                selectedTypeDef.features.includes("sub_doors")) ? (
                <div className="space-y-4 border-t border-[rgba(255,255,255,0.06)] pt-4">
                  <h4 className="text-sm font-bold text-white">Flow Options</h4>

                  {selectedTypeDef.features.includes("sub_doors") ? (
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <span className="block text-sm text-white">Sub doors / multiple doctors</span>
                        <span className="text-xs text-[var(--text-muted)]">Use child doors for doctors, counters, or departments</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setHasMultipleDoctors((value) => !value)}
                        className={[
                          "h-7 w-12 rounded-full border transition",
                          hasMultipleDoctors ? "border-[rgba(246,185,74,0.55)] bg-[rgba(246,185,74,0.25)]" : "border-[rgba(255,255,255,0.14)] bg-[rgba(255,255,255,0.04)]",
                        ].join(" ")}
                        aria-pressed={hasMultipleDoctors}
                      >
                        <span
                          className={[
                            "block h-5 w-5 translate-y-[1px] rounded-full bg-white transition-transform",
                            hasMultipleDoctors ? "translate-x-[24px]" : "translate-x-[2px]",
                          ].join(" ")}
                        />
                      </button>
                    </div>
                  ) : null}

                  {selectedTypeDef.features.includes("appointments") ? (
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <span className="block text-sm text-white">Appointment required</span>
                        <span className="text-xs text-[var(--text-muted)]">Appointment users can still be handled through the same queue lane</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setRequireAppointments((value) => !value)}
                        className={[
                          "h-7 w-12 rounded-full border transition",
                          requireAppointments ? "border-[rgba(246,185,74,0.55)] bg-[rgba(246,185,74,0.25)]" : "border-[rgba(255,255,255,0.14)] bg-[rgba(255,255,255,0.04)]",
                        ].join(" ")}
                        aria-pressed={requireAppointments}
                      >
                        <span
                          className={[
                            "block h-5 w-5 translate-y-[1px] rounded-full bg-white transition-transform",
                            requireAppointments ? "translate-x-[24px]" : "translate-x-[2px]",
                          ].join(" ")}
                        />
                      </button>
                    </div>
                  ) : null}

                  {(selectedTypeDef.features.includes("time_slots") || selectedTypeDef.features.includes("working_hours")) ? (
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <label className="mb-1 block text-xs font-medium text-[var(--text-muted)]">From time</label>
                        <input
                          type="time"
                          value={startTime}
                          onChange={(e) => setStartTime(e.target.value)}
                          className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(246,185,74,0.35)]"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs font-medium text-[var(--text-muted)]">To time</label>
                        <input
                          type="time"
                          value={endTime}
                          onChange={(e) => setEndTime(e.target.value)}
                          className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(246,185,74,0.35)]"
                        />
                      </div>
                    </div>
                  ) : null}

                  {(selectedTypeDef.features.includes("queue") || selectedTypeDef.features.includes("max_tokens")) ? (
                    <div>
                      <label className="mb-1 block text-xs font-medium text-[var(--text-muted)]">Max queue token no</label>
                      <input
                        type="number"
                        min="1"
                        step="1"
                        value={maxTokenCount}
                        onChange={(e) => setMaxTokenCount(e.target.value)}
                        placeholder="120"
                        className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(246,185,74,0.35)]"
                      />
                    </div>
                  ) : null}
                </div>
              ) : null}

              {selectedTypeDef.features.includes("emergency_profile") ? (
                <div className="space-y-4 border-t border-[rgba(255,255,255,0.06)] pt-4">
                  <h4 className="text-sm font-bold text-[var(--danger)]">Emergency Profile Details</h4>
                  <p className="text-xs text-[var(--text-muted)]">This data is saved in metadata for now.</p>

                  <div>
                    <label className="mb-1 block text-xs font-medium text-[var(--text-muted)]">Blood Group</label>
                    <input
                      value={bloodGroup}
                      onChange={(e) => setBloodGroup(e.target.value)}
                      placeholder="e.g. O+, A-"
                      className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(255,109,109,0.35)]"
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-xs font-medium text-[var(--text-muted)]">Medical Conditions / Allergies</label>
                    <textarea
                      value={medicalConditions}
                      onChange={(e) => setMedicalConditions(e.target.value)}
                      rows={2}
                      placeholder="e.g. Asthma, Diabetic"
                      className="w-full resize-none rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(255,109,109,0.35)]"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-xs font-medium text-[var(--text-muted)]">Emergency Contacts</label>
                    <div className="space-y-2">
                      {emergencyContacts.map((value, idx) => (
                        <input
                          key={idx}
                          value={value}
                          onChange={(e) => {
                            const next = [...emergencyContacts];
                            next[idx] = e.target.value;
                            setEmergencyContacts(next);
                          }}
                          placeholder={`Contact ${idx + 1}`}
                          className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none focus:ring-2 focus:ring-[rgba(255,109,109,0.35)]"
                        />
                      ))}
                    </div>
                    <button
                      type="button"
                      onClick={() => setEmergencyContacts((prev) => [...prev, ""])}
                      className="mt-2 text-xs font-semibold text-[var(--danger)]"
                    >
                      + Add another contact
                    </button>
                  </div>
                </div>
              ) : null}

              <button
                type="button"
                onClick={() => setAdvancedOpen((v) => !v)}
                className="flex w-full items-center justify-between rounded-2xl border border-[rgba(255,255,255,0.10)] bg-[rgba(255,255,255,0.02)] px-4 py-3 text-sm font-semibold text-white transition hover:border-[rgba(255,255,255,0.16)]"
              >
                <span>Advanced (optional)</span>
                <span className="text-[var(--text-muted)]">{advancedOpen ? "Hide" : "Show"}</span>
              </button>

              {advancedOpen ? (
                <div className="space-y-4">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Attach to organization (optional)</label>
                    <select
                      value={organization}
                      onChange={(e) => setOrganization(e.target.value)}
                      className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none"
                    >
                      <option value="">None</option>
                      {(orgData ?? []).map((org: any) => (
                        <option key={org.id} value={org.id}>
                          {org.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-[var(--text-muted)]">Attach to queue (optional)</label>
                    <select
                      value={queue}
                      onChange={(e) => setQueue(e.target.value)}
                      className="w-full rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(26,26,26,0.92)] px-4 py-3 text-white outline-none"
                    >
                      <option value="">None</option>
                      {(queueData ?? []).map((q: any) => (
                        <option key={q.id} value={q.id}>
                          {q.name}
                        </option>
                      ))}
                    </select>
                    <p className="mt-2 text-xs text-[var(--text-muted)]">If a queue is selected, this door will be created as a queue entry point.</p>
                  </div>
                </div>
              ) : null}
            </div>

            <button
              type="button"
              disabled={saving}
              onClick={submit}
              className="w-full rounded-xl bg-[linear-gradient(135deg,#f6b94a,#f39c28)] py-4 text-sm font-bold text-[#1a1204] shadow-lg shadow-[rgba(246,185,74,0.18)] transition hover:brightness-105 disabled:opacity-70"
            >
              {saving ? "Creating…" : "Create Door & Configure Settings"}
            </button>

            {created?.id ? (
              <div className="rounded-2xl border border-[rgba(55,214,197,0.22)] bg-[rgba(55,214,197,0.08)] p-4 text-sm text-white">
                Created. Opening QR details…
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
