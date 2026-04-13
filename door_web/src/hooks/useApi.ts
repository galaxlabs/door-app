import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useOrganizations() {
  return useQuery({
    queryKey: ["organizations"],
    queryFn: () => api.get("/organizations/").then((r) => r.data.results),
  });
}

export function useQRCodes(params?: object) {
  return useQuery({
    queryKey: ["qr-codes", params],
    queryFn: () => api.get("/qr/codes/", { params }).then((r) => r.data.results),
  });
}

export function useQueues(params?: object) {
  return useQuery({
    queryKey: ["queues", params],
    queryFn: () => api.get("/queues/", { params }).then((r) => r.data.results),
  });
}

export function useBroadcastChannels(params?: object) {
  return useQuery({
    queryKey: ["broadcast-channels", params],
    queryFn: () => api.get("/broadcast/channels/", { params }).then((r) => r.data.results),
  });
}

export function useAuditLogs(params?: object) {
  return useQuery({
    queryKey: ["audit-logs", params],
    queryFn: () => api.get("/audit/", { params }).then((r) => r.data.results),
  });
}
