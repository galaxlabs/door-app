"use client";
import { useEffect, useRef, useCallback } from "react";

export function useQueueSocket(
  queueId: string,
  onEvent: (event: { type: string; data: unknown }) => void
) {
  const ws = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const token = localStorage.getItem("access_token");
    const url = `${process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8010"}/ws/queues/${queueId}/?token=${token}`;
    ws.current = new WebSocket(url);

    ws.current.onmessage = (e) => {
      try {
        onEvent(JSON.parse(e.data));
      } catch {/* ignore parse errors */}
    };

    ws.current.onclose = () => {
      setTimeout(connect, 3000); // reconnect
    };
  }, [queueId, onEvent]);

  useEffect(() => {
    connect();
    return () => ws.current?.close();
  }, [connect]);

  const send = useCallback((data: object) => {
    ws.current?.send(JSON.stringify(data));
  }, []);

  return { send };
}
