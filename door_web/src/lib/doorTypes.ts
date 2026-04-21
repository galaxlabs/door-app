import {
  BriefcaseBusiness,
  CarFront,
  GraduationCap,
  HeartPulse,
  Home,
  LayoutGrid,
  LucideIcon,
  MapPin,
  ShieldAlert,
  Store,
} from "lucide-react";

export type DoorMode = "custom_action" | "queue_join" | "check_in" | "open_chat";

export type DoorFeatureKey =
  | "queue"
  | "appointments"
  | "time_slots"
  | "max_tokens"
  | "working_hours"
  | "sub_doors"
  | "live_serving"
  | "visitor_log"
  | "checkpoints"
  | "emergency_profile";

export type DoorIconKey =
  | "home"
  | "shop"
  | "clinic"
  | "office"
  | "school"
  | "trip"
  | "checkpoint"
  | "emergency"
  | "custom";

export type StoredDoorType = {
  id: string;
  label: string;
  description: string;
  iconKey: DoorIconKey;
  mode: DoorMode;
  modeLabel?: string;
  purpose: string;
  features: DoorFeatureKey[];
};

export type DoorTypeDefinition = StoredDoorType & {
  icon: LucideIcon;
  source: "system" | "custom";
};

export const CUSTOM_DOOR_TYPES_STORAGE_KEY = "door_custom_types_v1";
export const DOOR_TYPES_UPDATED_EVENT = "door:types-updated";

export const DOOR_MODE_LABELS: Record<DoorMode, string> = {
  custom_action: "Bell",
  queue_join: "Queue",
  check_in: "Check-in",
  open_chat: "Chat",
};

export const DOOR_MODE_OPTIONS: Array<{ id: DoorMode; label: string }> = [
  { id: "custom_action", label: "Custom action" },
  { id: "queue_join", label: "Queue join" },
  { id: "check_in", label: "Check in" },
  { id: "open_chat", label: "Open chat" },
];

export const FEATURE_LABELS: Record<DoorFeatureKey, string> = {
  queue: "Queue system",
  appointments: "Appointments",
  time_slots: "Time slots",
  max_tokens: "Max token count",
  working_hours: "Working hours",
  sub_doors: "Sub doors",
  live_serving: "Live serving updates",
  visitor_log: "Visitor log",
  checkpoints: "Check points",
  emergency_profile: "Emergency profile",
};

export const DOOR_ICON_OPTIONS: Array<{ id: DoorIconKey; label: string; icon: LucideIcon }> = [
  { id: "home", label: "Home", icon: Home },
  { id: "shop", label: "Shop / Factory", icon: Store },
  { id: "clinic", label: "Hospital / Clinic", icon: HeartPulse },
  { id: "office", label: "Office / Business", icon: BriefcaseBusiness },
  { id: "school", label: "Education / School", icon: GraduationCap },
  { id: "trip", label: "Trip Log", icon: CarFront },
  { id: "checkpoint", label: "Check Points", icon: MapPin },
  { id: "emergency", label: "Emergency", icon: ShieldAlert },
  { id: "custom", label: "More / Custom", icon: LayoutGrid },
];

const DOOR_ICON_MAP = Object.fromEntries(DOOR_ICON_OPTIONS.map((item) => [item.id, item.icon])) as Record<
  DoorIconKey,
  LucideIcon
>;

export const SYSTEM_DOOR_TYPES: DoorTypeDefinition[] = [
  {
    id: "home",
    iconKey: "home",
    icon: Home,
    label: "Home",
    description: "Standard doorbell for your house, apartment, or family entry point.",
    mode: "custom_action",
    modeLabel: "Bell",
    purpose: "bell",
    features: ["visitor_log", "working_hours"],
    source: "system",
  },
  {
    id: "shop",
    iconKey: "shop",
    icon: Store,
    label: "Shop / Factory",
    description: "Manage visitors, deliveries, walk-ins, and token-based service flow.",
    mode: "queue_join",
    modeLabel: "Queue",
    purpose: "queue",
    features: ["queue", "working_hours", "live_serving", "max_tokens"],
    source: "system",
  },
  {
    id: "clinic",
    iconKey: "clinic",
    icon: HeartPulse,
    label: "Hospital / Clinic",
    description: "Queue-based check-in with appointments, time slots, and doctor sub-doors.",
    mode: "queue_join",
    modeLabel: "Queue",
    purpose: "clinic",
    features: ["queue", "appointments", "time_slots", "max_tokens", "sub_doors", "live_serving"],
    source: "system",
  },
  {
    id: "office",
    iconKey: "office",
    icon: BriefcaseBusiness,
    label: "Office / Business",
    description: "Reception-style visitor logging, meetings, and controlled access.",
    mode: "open_chat",
    modeLabel: "Chat",
    purpose: "visitor_log",
    features: ["visitor_log", "appointments", "working_hours"],
    source: "system",
  },
  {
    id: "school",
    iconKey: "school",
    icon: GraduationCap,
    label: "Education / School",
    description: "School reception, guardian visits, and attendance-aware entry control.",
    mode: "check_in",
    modeLabel: "Check-in",
    purpose: "check_in",
    features: ["visitor_log", "time_slots", "working_hours", "checkpoints"],
    source: "system",
  },
  {
    id: "trip",
    iconKey: "trip",
    icon: CarFront,
    label: "Trip Log",
    description: "Travel checkpoints, route logs, and supervised movement tracking.",
    mode: "check_in",
    modeLabel: "Check-in",
    purpose: "trip",
    features: ["checkpoints", "time_slots", "working_hours"],
    source: "system",
  },
  {
    id: "checkpoint",
    iconKey: "checkpoint",
    icon: MapPin,
    label: "Check Points",
    description: "Security patrol, checkpoints, and location-based logging.",
    mode: "check_in",
    modeLabel: "Check-in",
    purpose: "checkpoint",
    features: ["checkpoints", "working_hours", "time_slots"],
    source: "system",
  },
  {
    id: "emergency",
    iconKey: "emergency",
    icon: ShieldAlert,
    label: "Emergency",
    description: "Urgent access profile with medical details and emergency contacts.",
    mode: "custom_action",
    modeLabel: "Bell",
    purpose: "emergency",
    features: ["emergency_profile"],
    source: "system",
  },
];

function hydrateDoorType(type: StoredDoorType, source: DoorTypeDefinition["source"]): DoorTypeDefinition {
  return {
    ...type,
    icon: DOOR_ICON_MAP[type.iconKey] ?? LayoutGrid,
    source,
  };
}

export function readCustomDoorTypes(): DoorTypeDefinition[] {
  if (typeof window === "undefined") return [];

  try {
    const raw = window.localStorage.getItem(CUSTOM_DOOR_TYPES_STORAGE_KEY);
    if (!raw) return [];

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed
      .filter(
        (item): item is StoredDoorType =>
          Boolean(item) &&
          typeof item.id === "string" &&
          typeof item.label === "string" &&
          typeof item.description === "string" &&
          typeof item.iconKey === "string" &&
          typeof item.mode === "string" &&
          (typeof item.modeLabel === "undefined" || typeof item.modeLabel === "string") &&
          typeof item.purpose === "string" &&
          Array.isArray(item.features)
      )
      .map((item) => hydrateDoorType(item, "custom"));
  } catch {
    return [];
  }
}

export function saveCustomDoorTypes(types: StoredDoorType[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(CUSTOM_DOOR_TYPES_STORAGE_KEY, JSON.stringify(types));
  window.dispatchEvent(new CustomEvent(DOOR_TYPES_UPDATED_EVENT));
}

export function getAllDoorTypes(): DoorTypeDefinition[] {
  return [...SYSTEM_DOOR_TYPES, ...readCustomDoorTypes()];
}

export function getDoorModeLabel(mode: DoorMode, overrideLabel?: string): string {
  const normalized = overrideLabel?.trim();
  if (normalized) return normalized;
  return DOOR_MODE_LABELS[mode];
}
