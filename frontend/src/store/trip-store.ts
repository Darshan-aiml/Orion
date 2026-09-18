import { create } from "zustand";
import type { Destination, Guide, Activity } from "@/lib/api";

interface ItineraryItem {
  day: number;
  activityId: string;
  activityName: string;
  price: number;
}

interface TripStore {
  // Selection state
  selectedDestination: Destination | null;
  selectedGuide: Guide | null;
  startDate: string | null;
  endDate: string | null;
  itinerary: ItineraryItem[];

  // Actions
  setDestination: (destination: Destination | null) => void;
  setGuide: (guide: Guide | null) => void;
  setDates: (start: string, end: string) => void;
  addToItinerary: (item: ItineraryItem) => void;
  removeFromItinerary: (day: number, activityId: string) => void;
  resetTrip: () => void;

  // Agent feed
  agentEvents: { id: string; message: string; timestamp: string }[];
  addAgentEvent: (event: { id: string; message: string; timestamp: string }) => void;
}

export const useTripStore = create<TripStore>((set) => ({
  selectedDestination: null,
  selectedGuide: null,
  startDate: null,
  endDate: null,
  itinerary: [],
  agentEvents: [],

  setDestination: (destination) => set({ selectedDestination: destination }),
  setGuide: (guide) => set({ selectedGuide: guide }),
  setDates: (start, end) => set({ startDate: start, endDate: end }),
  addToItinerary: (item) =>
    set((state) => ({ itinerary: [...state.itinerary, item] })),
  removeFromItinerary: (day, activityId) =>
    set((state) => ({
      itinerary: state.itinerary.filter(
        (i) => !(i.day === day && i.activityId === activityId)
      ),
    })),
  resetTrip: () =>
    set({
      selectedDestination: null,
      selectedGuide: null,
      startDate: null,
      endDate: null,
      itinerary: [],
    }),
  addAgentEvent: (event) =>
    set((state) => ({ agentEvents: [event, ...state.agentEvents] })),
}));
