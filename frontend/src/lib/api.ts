/**
 * Thin typed wrapper around the backend API.
 * All paths are relative to NEXT_PUBLIC_API_URL.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json() as Promise<T>;
}

// ── Destinations ─────────────────────────────────────────────────────────────
export interface Destination {
  id: string;
  name: string;
  country: string;
  description: string | null;
}

export const fetchDestinations = (): Promise<Destination[]> =>
  apiFetch("/api/v1/discovery/destinations");

// ── Guides ────────────────────────────────────────────────────────────────────
export interface Guide {
  id: string;
  name: string;
  bio: string | null;
  languages: string[];
  specializations: string[];
  base_price_per_day: number;
  rating: number | null;
}

export const fetchGuides = (destinationId?: string): Promise<Guide[]> => {
  const qs = destinationId ? `?destination_id=${destinationId}` : "";
  return apiFetch(`/api/v1/discovery/guides${qs}`);
};

// ── Activities ────────────────────────────────────────────────────────────────
export interface Activity {
  id: string;
  name: string;
  activity_type: string;
  description: string | null;
  base_price: number;
  duration_mins: number | null;
}

export const fetchActivities = (destinationId?: string): Promise<Activity[]> => {
  const qs = destinationId ? `?destination_id=${destinationId}` : "";
  return apiFetch(`/api/v1/discovery/activities${qs}`);
};

// ── Events ────────────────────────────────────────────────────────────────────
export const simulateEvent = (payload: { event_type: string; payload: Record<string, unknown> }) =>
  apiFetch("/api/v1/events/simulate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
