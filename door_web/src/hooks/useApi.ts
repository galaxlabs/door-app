import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

function extractCollection<T>(data: unknown): T[] {
  if (Array.isArray(data)) {
    return data as T[];
  }

  if (data && typeof data === "object") {
    const candidate = data as { results?: unknown; items?: unknown; data?: unknown };

    if (Array.isArray(candidate.results)) {
      return candidate.results as T[];
    }

    if (Array.isArray(candidate.items)) {
      return candidate.items as T[];
    }

    if (Array.isArray(candidate.data)) {
      return candidate.data as T[];
    }
  }

  return [];
}

export function useOrganizations() {
  return useQuery({
    queryKey: ["organizations"],
    queryFn: () => api.get("organizations/").then((r) => extractCollection(r.data)),
  });
}

export function useOrganizationMembers(orgId?: string) {
  return useQuery({
    queryKey: ["organization-members", orgId],
    enabled: Boolean(orgId),
    queryFn: () => api.get(`organizations/${orgId}/members/`).then((r) => extractCollection(r.data)),
  });
}

export function useQRCodes(params?: object) {
  return useQuery({
    queryKey: ["qr-codes", params],
    queryFn: () => api.get("qr/codes/", { params }).then((r) => extractCollection(r.data)),
  });
}

export function useQRCode(id?: string) {
  return useQuery({
    queryKey: ["qr-code", id],
    enabled: Boolean(id),
    queryFn: () => api.get(`qr/codes/${id}/`).then((r) => r.data),
  });
}

export function useQueues(params?: object) {
  return useQuery({
    queryKey: ["queues", params],
    queryFn: () => api.get("queues/", { params }).then((r) => extractCollection(r.data)),
  });
}

export function useBroadcastChannels(params?: object) {
  return useQuery({
    queryKey: ["broadcast-channels", params],
    queryFn: () => api.get("broadcast/channels/", { params }).then((r) => extractCollection(r.data)),
  });
}

export function useAuditLogs(params?: object) {
  return useQuery({
    queryKey: ["audit-logs", params],
    queryFn: () => api.get("audit/", { params }).then((r) => extractCollection(r.data)),
  });
}
