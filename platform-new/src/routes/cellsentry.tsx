import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Network, RotateCcw } from "lucide-react";
import { AgentPage } from "@/components/urja/AgentPage";
import { AgentSection, SectionTitle } from "@/components/urja/AgentSections";
import { GlassCard } from "@/components/urja/GlassCard";
import { StatusPill } from "@/components/urja/StatusPill";
import { SupplyGraph } from "@/components/urja/SupplyGraph";
import {
  fetchGraph,
  fetchEvents,
  runScenario,
  type GraphNode,
  type GraphEdge,
  type Alert,
  type RiskBand,
  type SignalEvent,
} from "@/lib/supply";
import { z } from "zod";

const searchSchema = z.object({
  eventId: z.string().optional(),
});

export const Route = createFileRoute("/cellsentry")({
  validateSearch: searchSchema,
  head: () => ({
    meta: [
      { title: "CellSentry — Urja" },
      { name: "description", content: "AI-driven supply chain transparency and disruption forecasting." },
    ],
  }),
  component: () => {
    const { eventId } = Route.useSearch();
    return (
      <AgentPage
        agentName="CellSentry"
        eyebrow="Agent · Supply Chain"
        mission="Graph-based risk and traceability across lithium, cobalt, nickel, and graphite sourcing — with scenario simulation for live risk events."
        tabs={[{ key: "supply", label: "Supply Chain Intelligence", icon: Network }]}
        renderContent={() => <SupplyChainTab />}
        initialTab={eventId ? "supply" : "dashboard"}
      />
    );
  },
});

const RISK_TONE: Record<RiskBand, "healthy" | "watch" | "critical"> = {
  low: "healthy",
  medium: "watch",
  high: "critical",
};
const RISK_COLOR: Record<RiskBand, string> = {
  low: "#34d399",
  medium: "#fbbf24",
  high: "#f87171",
};

function getSeverityBand(s: number): RiskBand {
  if (s >= 4) return "high";
  if (s >= 3) return "medium";
  return "low";
}

function SupplyChainTab() {
  const { eventId } = Route.useSearch();
  const [activeSignal, setActiveSignal] = useState<string | null>(eventId || null);
  const [loading, setLoading] = useState(false);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [signals, setSignals] = useState<SignalEvent[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    async function load() {
      try {
        const [g, evs] = await Promise.all([fetchGraph(), fetchEvents()]);
        setSignals(evs);
        if (eventId) {
          try {
            const res = await runScenario([eventId]);
            setNodes(res.nodes);
            setEdges(res.edges);
            setAlerts(res.alerts);
          } catch (e) {
            console.error("Scenario failed", e);
          }
        } else {
          setNodes(g.nodes);
          setEdges(g.edges);
        }
      } catch (e) {
        console.error("Failed to load baseline", e);
      }
    }
    load();
  }, []);

  async function selectSignal(id: string) {
    setActiveSignal(id);
    setLoading(true);
    setAlerts([]);
    try {
      const res = await runScenario([id]);
      setNodes(res.nodes);
      setEdges(res.edges);
      setAlerts(res.alerts);
    } catch (e) {
      console.error("Scenario failed", e);
    } finally {
      setLoading(false);
    }
  }

  async function reset() {
    setActiveSignal(null);
    setAlerts([]);
    setLoading(true);
    try {
      const g = await fetchGraph();
      setNodes(g.nodes);
      setEdges(g.edges);
    } catch (e) {
      console.error("Failed to reset", e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AgentSection>
      <SectionTitle eyebrow="Graph" title="Supply chain intelligence" />
      <div className="grid gap-6 xl:grid-cols-[1fr_2fr_1fr] h-[640px]">
        {/* Left: signal feed */}
        <GlassCard padding="md" className="flex flex-col h-full overflow-hidden">
          <div className="mb-3 text-[15px] font-semibold shrink-0">Signal Feed</div>
          <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-2 custom-scrollbar">
            {signals.map((s) => (
              <button
                key={s.id}
                onClick={() => selectSignal(s.id)}
                className="rounded-[12px] border p-3 text-left transition-colors"
                style={{
                  background: activeSignal === s.id ? "rgba(91,95,237,0.14)" : "rgba(255,255,255,0.03)",
                  borderColor: activeSignal === s.id ? "rgba(91,95,237,0.4)" : "rgba(255,255,255,0.06)",
                }}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[12px] font-medium leading-snug">{s.headline}</span>
                  <StatusPill tone={RISK_TONE[getSeverityBand(s.severity)]}>Sev {s.severity}</StatusPill>
                </div>
                <div className="mt-1 text-[11px] text-[color:var(--color-text-tertiary)]">{s.source.name} · {s.date} · {s.countries?.join(", ") || "Global"}</div>
                <div className="mt-1 text-[11px] leading-relaxed text-[color:var(--color-text-secondary)]">{s.body}</div>
              </button>
            ))}
          </div>
        </GlassCard>

        {/* Center: knowledge graph */}
        <GlassCard padding="md" className="flex flex-col h-full overflow-hidden">
          <div className="mb-3 flex items-center justify-between shrink-0">
            <div className="text-[15px] font-semibold">Knowledge Graph</div>
            <div className="flex items-center gap-3 text-[11px] text-[color:var(--color-text-secondary)]">
              <LegendDot color="#34d399" label="Low" />
              <LegendDot color="#fbbf24" label="Med" />
              <LegendDot color="#f87171" label="High" />
              {activeSignal && (
                <button onClick={reset} className="ml-2 inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 hover:bg-white/[0.08]">
                  <RotateCcw className="h-3 w-3" /> Reset
                </button>
              )}
            </div>
          </div>
          <div className="relative flex-1 min-h-0">
            {loading && (
              <div className="absolute inset-0 z-10 flex items-center justify-center rounded-[12px] bg-black/40 backdrop-blur-sm">
                <div className="text-[13px] text-[color:var(--color-text-secondary)]">Computing scenario…</div>
              </div>
            )}
            <SupplyGraph nodes={nodes} edges={edges} />
          </div>
        </GlassCard>

        {/* Right: alerts */}
        <GlassCard padding="md" className="flex flex-col h-full overflow-hidden">
          <div className="mb-3 text-[15px] font-semibold shrink-0">Risk Alerts</div>
          {!activeSignal && !loading && (
            <div className="rounded-[12px] border border-white/5 bg-white/[0.02] p-3 text-[12px] text-[color:var(--color-text-secondary)]">
              Select a signal to run a scenario simulation.
            </div>
          )}
          {loading && (
            <div className="rounded-[12px] border border-white/5 bg-white/[0.02] p-3 text-[12px] text-[color:var(--color-text-secondary)]">
              Recomputing risk across the graph…
            </div>
          )}
          {!loading && alerts.length > 0 && (
            <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-2 custom-scrollbar">
              {alerts.map((a, idx) => (
                <div key={idx} className="rounded-[12px] border border-white/5 bg-white/[0.03] p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[12px] font-medium">{a.product_label}</span>
                    <StatusPill tone={RISK_TONE[a.risk_band]}>{a.risk_band}</StatusPill>
                  </div>
                  <div className="mt-1 text-[12px] leading-relaxed text-[color:var(--color-text-secondary)]">{a.brief}</div>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </div>
    </AgentSection>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="inline-block h-2 w-2 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}

