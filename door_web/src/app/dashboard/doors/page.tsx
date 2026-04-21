"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  AlertTriangle,
  DoorOpen,
  Link2,
  Plus,
  Settings,
  User,
} from "lucide-react";
import { useQRCodes } from "@/hooks/useApi";
import { DOOR_TYPES_UPDATED_EVENT, DoorMode, getAllDoorTypes, getDoorModeLabel } from "@/lib/doorTypes";

type QRRecord = {
  id: string;
  label?: string;
  name?: string;
  purpose?: string;
  mode?: string;
  is_active?: boolean;
  metadata_json?: Record<string, unknown> | null;
  payload_data?: Record<string, unknown> | null;
  action_payload?: Record<string, unknown> | null;
};

const doorModes = new Set(["custom_action", "queue_join", "check_in", "open_chat"]);

function readDoorMetaString(door: QRRecord, key: string): string | undefined {
  const candidates = [door.metadata_json, door.payload_data, door.action_payload];
  for (const source of candidates) {
    if (!source || typeof source !== "object") continue;
    const value = source[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return undefined;
}

export default function DoorsPage() {
  const { data, isLoading, error } = useQRCodes();
  const qrCodes = useMemo(() => (data ?? []) as QRRecord[], [data]);
  const [doorTypesById, setDoorTypesById] = useState(() => {
    return new Map(getAllDoorTypes().map((item) => [item.id, item]));
  });

  const doors = useMemo(() => {
    return qrCodes.filter((item) => doorModes.has(item.mode ?? ""));
  }, [qrCodes]);

  const unauthorized = useMemo(() => {
    if (!error) return false;
    if (axios.isAxiosError(error)) return error.response?.status === 401;
    return false;
  }, [error]);

  useEffect(() => {
    function syncDoorTypes() {
      setDoorTypesById(new Map(getAllDoorTypes().map((item) => [item.id, item])));
    }
    window.addEventListener(DOOR_TYPES_UPDATED_EVENT, syncDoorTypes);
    return () => {
      window.removeEventListener(DOOR_TYPES_UPDATED_EVENT, syncDoorTypes);
    };
  }, []);

  return (
    <div className="p-4 pb-24">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6">
          <h2 className="text-2xl font-bold tracking-tight text-white">Doors</h2>
          <p className="mt-1 text-sm text-[var(--text-muted)]">Manage your doors with quick horizontal cards and less scrolling.</p>
        </div>

        <p className="mb-3 text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">Quick actions</p>
        <div className="mb-8 flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2">
          <Link
            href="/dashboard/doors/create"
            className="flex min-h-[136px] min-w-[250px] snap-start items-center gap-4 rounded-2xl border border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-5 transition-colors hover:border-[rgba(246,185,74,0.35)] md:min-w-[290px]"
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[var(--amber-soft)] text-[var(--amber)]">
              <Plus className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Add Door</h3>
              <p className="text-sm text-[var(--text-muted)]">Create a new door and generate QR</p>
            </div>
          </Link>

          <Link
            href="/dashboard/doors/create?type=emergency"
            className="flex min-h-[136px] min-w-[250px] snap-start items-center gap-4 rounded-2xl border border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-5 transition-colors hover:border-[rgba(255,109,109,0.35)] md:min-w-[290px]"
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[rgba(255,109,109,0.12)] text-[var(--danger)]">
              <AlertTriangle className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Emergency</h3>
              <p className="text-sm text-[var(--text-muted)]">Create an emergency card door</p>
            </div>
          </Link>

          <Link
            href="/dashboard/qr"
            className="flex min-h-[136px] min-w-[250px] snap-start items-center gap-4 rounded-2xl border border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-5 transition-colors hover:border-[rgba(55,214,197,0.30)] md:min-w-[290px]"
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[var(--teal-soft)] text-[var(--teal)]">
              <Link2 className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Join Door</h3>
              <p className="text-sm text-[var(--text-muted)]">Scan a QR (join flow coming next)</p>
            </div>
          </Link>

          <Link
            href="/dashboard/profile"
            className="flex min-h-[136px] min-w-[250px] snap-start items-center gap-4 rounded-2xl border border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-5 transition-colors hover:border-[rgba(255,255,255,0.18)] md:min-w-[290px]"
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[rgba(255,255,255,0.03)] text-[var(--text-muted)]">
              <User className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Profile Settings</h3>
              <p className="text-sm text-[var(--text-muted)]">Visitor card, meeting points, door type config</p>
            </div>
          </Link>
        </div>

        <div>
          <h3 className="mb-4 text-lg font-bold text-white">My Doors</h3>

          {isLoading ? (
            <div className="rounded-2xl border border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-4 text-sm text-[var(--text-muted)]">
              Loading…
            </div>
          ) : unauthorized ? (
            <div className="rounded-2xl border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-4">
              <p className="text-sm font-semibold text-white">Sign in required</p>
              <p className="mt-1 text-sm text-[var(--text-soft)]">Doors load after you sign in.</p>
              <Link
                href="/auth/login"
                className="mt-3 inline-flex items-center justify-center rounded-xl bg-[linear-gradient(135deg,#f6b94a,#f39c28)] px-4 py-3 text-sm font-semibold text-[#1a1204] transition hover:brightness-105"
              >
                Sign in
              </Link>
            </div>
          ) : error ? (
            <div className="rounded-2xl border border-[rgba(255,109,109,0.22)] bg-[rgba(255,109,109,0.08)] p-4 text-sm text-[var(--text-soft)]">
              Could not load doors. Please refresh.
            </div>
          ) : doors.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-6 text-center">
              <DoorOpen className="mx-auto h-9 w-9 text-[var(--text-muted)]" />
              <p className="mt-4 text-lg font-semibold text-white">No doors yet</p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">Create your first door and it will appear here.</p>
              <Link
                href="/dashboard/doors/create"
                className="mt-4 inline-flex items-center justify-center rounded-xl bg-[linear-gradient(135deg,#f6b94a,#f39c28)] px-4 py-3 text-sm font-semibold text-[#1a1204] transition hover:brightness-105"
              >
                Add Door
              </Link>
            </div>
          ) : (
            <div className="grid gap-3 lg:grid-cols-2">
              {doors.map((door) => (
                <div key={door.id} className="flex items-center justify-between rounded-2xl border border-[var(--line)] bg-[rgba(18,18,18,0.85)] p-4">
                  {(() => {
                    const typeId = readDoorMetaString(door, "door_type");
                    const typeLabelFromType = typeId ? doorTypesById.get(typeId)?.label : undefined;
                    const customModeFromType = typeId ? doorTypesById.get(typeId)?.modeLabel : undefined;
                    const doorTypeLabel = readDoorMetaString(door, "door_type_label") ?? typeLabelFromType;
                    const customModeLabel = readDoorMetaString(door, "mode_label") ?? customModeFromType;
                    const fallbackMode: DoorMode =
                      door.mode === "queue_join" || door.mode === "check_in" || door.mode === "open_chat"
                        ? door.mode
                        : "custom_action";
                    const doorModeLabel = customModeLabel || getDoorModeLabel(fallbackMode, undefined);

                    return (
                      <>
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[rgba(255,255,255,0.03)] text-[var(--text-muted)]">
                            <DoorOpen className="h-5 w-5" />
                          </div>
                          <div className="min-w-0">
                            <h4 className="truncate font-bold text-white">{door.label || door.name || "Untitled door"}</h4>
                            <p className="text-xs text-[var(--text-muted)]">
                              {door.is_active ? (
                                <span className="text-[var(--success)]">Active</span>
                              ) : (
                                <span className="text-[var(--danger)]">Inactive</span>
                              )}
                              <span className="mx-2 text-[rgba(255,255,255,0.18)]">•</span>
                              {doorModeLabel}
                              {doorTypeLabel ? (
                                <>
                                  <span className="mx-2 text-[rgba(255,255,255,0.18)]">•</span>
                                  {doorTypeLabel}
                                </>
                              ) : null}
                            </p>
                          </div>
                        </div>
                        <Link
                          href={`/dashboard/qr?focus=${door.id}`}
                          className="p-2 text-[var(--text-muted)] transition-colors hover:text-white"
                          aria-label="Open settings"
                        >
                          <Settings className="h-5 w-5" />
                        </Link>
                      </>
                    );
                  })()}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
