import { GuidesSelector } from "@/components/guides-selector";
import { PackageBuilder } from "@/components/package-builder";
import { AgentFeed } from "@/components/agent-feed";
import { SimulateEventPanel } from "@/components/simulate-event-panel";
import { MapPin } from "lucide-react";

// Next.js 16: params must be awaited
export default async function DestinationPage(props: PageProps<"/destinations/[id]">) {
  const { id } = await props.params;

  // We use a fixed demo trip ID for the SSE stream. In production this would
  // come from the authenticated user's active trip in the database.
  const DEMO_TRIP_ID = "00000000-0000-0000-0000-000000000000";

  return (
    <main className="max-w-6xl mx-auto w-full px-6 py-12 flex flex-col gap-12">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm text-neutral-500 dark:text-neutral-400">
        <MapPin className="h-4 w-4" />
        <span>Destination Details</span>
      </div>

      {/* Guide Selection */}
      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-white">Choose Your Guide</h2>
          <p className="text-neutral-500 dark:text-neutral-400 mt-1">
            Select a local expert to accompany your journey.
          </p>
        </div>
        <GuidesSelector destinationId={id} />
      </section>

      {/* Package Builder */}
      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-white">Build Your Itinerary</h2>
          <p className="text-neutral-500 dark:text-neutral-400 mt-1">
            Add activities to each day. The AI agent will adapt in real time.
          </p>
        </div>
        <PackageBuilder destinationId={id} />
      </section>

      {/* Real-time Agent Panel */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Simulate Disruption */}
        <div>
          <div className="mb-4">
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Simulate a Disruption</h2>
            <p className="text-neutral-500 dark:text-neutral-400 text-sm mt-1">
              Trigger the AI agent and watch it resolve the issue live.
            </p>
          </div>
          <SimulateEventPanel />
        </div>

        {/* Agent Activity Feed */}
        <div>
          <div className="mb-4">
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Agent Activity</h2>
            <p className="text-neutral-500 dark:text-neutral-400 text-sm mt-1">
              Transparent real-time feed of what the AI is doing.
            </p>
          </div>
          <AgentFeed tripId={DEMO_TRIP_ID} />
        </div>
      </section>
    </main>
  );
}

