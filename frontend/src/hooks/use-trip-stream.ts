"use client";

import { useEffect, useRef } from "react";
import { useTripStore } from "@/store/trip-store";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Opens a persistent SSE connection to the backend for a given trip.
 * Incoming agent events are pushed into the Zustand trip store.
 */
export function useTripStream(tripId: string | null) {
  const addAgentEvent = useTripStore((s) => s.addAgentEvent);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!tripId) return;

    const url = `${API_URL}/api/v1/stream/trip/${tripId}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "agent_action") {
          addAgentEvent({
            id: data.action_id ?? crypto.randomUUID(),
            message: data.reasoning_summary ?? "Agent took an action.",
            timestamp: new Date().toISOString(),
          });
        }
      } catch {
        // Ignore heartbeat / non-JSON messages
      }
    };

    es.onerror = () => {
      // Auto-reconnect is native to EventSource; just log
      console.warn("[SSE] Connection error — will retry automatically.");
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [tripId, addAgentEvent]);
}
