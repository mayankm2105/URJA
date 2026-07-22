import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Activity,
  Map as MapIcon,
  Bot,
  FileText,
  ShieldCheck,
  Send,
  Printer,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from "recharts";
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useRef } from 'react';
import { AgentPage } from "@/components/urja/AgentPage";
import { AgentSection, SectionTitle } from "@/components/urja/AgentSections";
import { GlassCard } from "@/components/urja/GlassCard";
import { StatCard } from "@/components/urja/StatCard";
import { StatusPill } from "@/components/urja/StatusPill";
import {
  fetchCarbonDashboard,
  fetchEmissions,
  fetchCommitments,
  fetchAssetClassEmissions,
  fetchRoutes,
  fetchPriorities,
  fetchAssistantReply,
  fetchCarbonValidation,
  fetchFleets,
  type CarbonDashboard,
  type EmissionPoint,
  type Fleet,
  type Commitment,
  type AssetClassEmissions,
  type Route as RouteRow,
  type Priority,
  type CarbonValidation,
  type ChatMessage,
} from "@/lib/carbon";

import { z } from "zod";

const searchSchema = z.object({
  tab: z.string().optional(),
});

export const Route = createFileRoute("/carbonpulse")({
  validateSearch: searchSchema,
  head: () => ({
    meta: [
      { title: "CarbonPulse — Urja" },
      { name: "description", content: "Scope 1/3 accounting versus SBTi with geospatial route analytics and AI electrification priorities." },
    ],
  }),
  component: () => {
    const { tab } = Route.useSearch();
    return (
    <AgentPage
      agentName="CarbonPulse"
      eyebrow="Agent · Net Zero"
      mission="Scope 1 and 3 accounting versus SBTi, geospatial route analytics, and AI-ranked electrification priorities."
      tabs={[
        { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
        { key: "emissions", label: "Emissions Intelligence", icon: Activity },
        { key: "routes", label: "Geospatial Route Map", icon: MapIcon },
        { key: "advisor", label: "AI Carbon Advisor", icon: Bot },
        { key: "report", label: "Generate Report", icon: FileText },
        { key: "validation", label: "Validation", icon: ShieldCheck },
      ]}
      renderContent={(k) =>
        k === "dashboard" ? <DashboardTab />
        : k === "emissions" ? <EmissionsTab />
        : k === "routes" ? <RoutesTab />
        : k === "advisor" ? <AdvisorTab />
        : k === "report" ? <ReportTab />
        : <ValidationTab />
      }
      initialTab={tab}
    />
  );
  },
});

// -------------------- 1. Dashboard --------------------
function DashboardTab() {
  const [d, setD] = useState<CarbonDashboard | null>(null);
  const [ts, setTs] = useState<EmissionPoint[]>([]);
  const [fleets, setFleets] = useState<Fleet[]>([]);
  const [fleetId, setFleetId] = useState<string>("all");

  useEffect(() => {
    fetchFleets().then(setFleets);
    fetchCarbonDashboard().then(setD);
  }, []);

  useEffect(() => {
    fetchEmissions(fleetId).then(setTs);
  }, [fleetId]);

  if (!d) return null;
  return (
    <AgentSection>
      <SectionTitle eyebrow="Overview" title="Fleet-wide net zero snapshot" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard label="Net Zero Progress" value={d.net_zero_progress_pct} suffix="%" decimals={1} status={{ tone: "watch", label: "In progress" }} />
        <StatCard label="Fleet EV Penetration" value={d.ev_penetration_pct} suffix="%" decimals={1} />
        <StatCard label="Scope 1 YTD" value={d.scope1_ytd_tons} hint="tCO₂e" />
        <StatCard label="Scope 3 YTD" value={d.scope3_ytd_tons} hint="tCO₂e" />
        <StatCard label="CO₂ Avoided by EVs" value={d.ev_avoided_ytd_tons} hint="tCO₂e" status={{ tone: "healthy", label: "Saved" }} />
        <StatCard label="Routes Electrified" value={d.routes_electrified} hint={`of ${d.total_routes}`} />
      </div>
      <GlassCard padding="md">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <div className="eyebrow">Monthly trajectory</div>
            <div className="mt-1 text-[16px] font-semibold">Scope 1 vs SBTi target vs CO₂ saved by EVs</div>
          </div>
          <select
            value={fleetId}
            onChange={(e) => setFleetId(e.target.value)}
            className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[13px] text-white outline-none focus:border-[rgba(91,95,237,0.5)]"
          >
            <option value="all">All Fleets Combined</option>
            {fleets.map(f => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={ts} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="label" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
            <Line type="monotone" dataKey="scope1_tons" name="Scope 1" stroke="#5b5fed" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="target_tons" name="Target Path" stroke="#fbbf24" strokeWidth={2} strokeDasharray="4 4" dot={false} />
            <Line type="monotone" dataKey="ev_avoided_tons" name="CO₂ Saved by EVs" stroke="#34d399" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </GlassCard>
    </AgentSection>
  );
}

// -------------------- 2. Emissions Intelligence --------------------
function EmissionsTab() {
  const [ts, setTs] = useState<EmissionPoint[]>([]);
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [assets, setAssets] = useState<AssetClassEmissions[]>([]);
  useEffect(() => {
    fetchEmissions().then(setTs);
    fetchCommitments().then(setCommitments);
    fetchAssetClassEmissions().then(setAssets);
  }, []);
  
  return (
    <AgentSection>
      <SectionTitle eyebrow="Composition" title="Emissions composition and trajectory" />

      <GlassCard padding="md">
        <div className="mb-3">
          <div className="eyebrow">Composition</div>
          <div className="mt-1 text-[16px] font-semibold">Direct, indirect, and EV-offset (monthly, tCO₂e)</div>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={ts} margin={{ top: 8, right: 8, left: -20, bottom: 0 }} stackOffset="none">
            <defs>
              <linearGradient id="s1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5b5fed" stopOpacity={0.5}/><stop offset="100%" stopColor="#5b5fed" stopOpacity={0}/></linearGradient>
              <linearGradient id="s3" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3e8ef7" stopOpacity={0.45}/><stop offset="100%" stopColor="#3e8ef7" stopOpacity={0}/></linearGradient>
              <linearGradient id="evo" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#34d399" stopOpacity={0.45}/><stop offset="100%" stopColor="#34d399" stopOpacity={0}/></linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="label" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
            <Area type="monotone" dataKey="scope1_tons" name="Scope 1 (Direct)" stroke="#5b5fed" fill="url(#s1)" strokeWidth={2} />
            <Area type="monotone" dataKey="scope3_tons" name="Scope 3 (Indirect)" stroke="#3e8ef7" fill="url(#s3)" strokeWidth={2} />
            <Area type="monotone" dataKey="ev_avoided_tons" name="Avoided by EV Offset" stroke="#34d399" fill="url(#evo)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </GlassCard>

      <GlassCard padding="md">
        <div className="mb-4 text-[16px] font-semibold">Net Zero Commitments</div>
        <div className="flex flex-col divide-y divide-white/5">
          {commitments.map((c) => {
            const pct = Math.min(100, Math.round((c.current_reduction_pct / c.reduction_target_pct) * 100));
            return (
              <div key={c.organization} className="py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[14px] font-medium">{c.organization}</div>
                    <div className="mt-0.5 text-[12px] text-[color:var(--color-text-secondary)]">
                      Baseline {c.baseline_year} → Target {c.target_year} · {c.reduction_target_pct}% reduction
                    </div>
                  </div>
                  <StatusPill tone={c.status === "On Track" ? "healthy" : "critical"}>{c.status}</StatusPill>
                </div>
                <div className="mt-3 flex items-center gap-3">
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/5">
                    <div className="h-full rounded-full" style={{ width: `${pct}%`, background: c.status === "On Track" ? "#34d399" : "#f87171" }} />
                  </div>
                  <div className="w-16 text-right text-[12px] tabular-nums text-[color:var(--color-text-secondary)]">
                    {c.current_reduction_pct.toFixed(1)}%
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </GlassCard>

      <GlassCard padding="md">
        <div className="mb-3">
          <div className="eyebrow">2026 YTD</div>
          <div className="mt-1 text-[16px] font-semibold">Carbon Footprint by Asset Class</div>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={assets} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="asset_class" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
            <Bar dataKey="scope1_tons" name="Scope 1" fill="#5b5fed" radius={[6,6,0,0]} />
            <Bar dataKey="scope3_tons" name="Scope 3" fill="#3e8ef7" radius={[6,6,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </GlassCard>
    </AgentSection>
  );
}

// -------------------- 3. Geospatial Route Map --------------------
function RoutesTab() {
  const [filter, setFilter] = useState<"all" | "diesel" | "ev">("all");
  const [routes, setRoutes] = useState<RouteRow[]>([]);
  useEffect(() => {
    fetchRoutes().then(setRoutes);
  }, []);

  const filtered = routes.filter((r) =>
    filter === "all" ? true : filter === "ev" ? r.is_electrified : !r.is_electrified,
  );
  const topEmitters = [...routes].sort((a, b) => b.monthly_co2_tons - a.monthly_co2_tons).slice(0, 6);

  return (
    <AgentSection>
      <SectionTitle eyebrow="India" title="Geospatial route map" />
      <div className="flex gap-2">
        {(["all", "diesel", "ev"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className="rounded-full px-4 py-1.5 text-[12px] font-medium transition-colors"
            style={{
              background: filter === f ? "rgba(91,95,237,0.18)" : "rgba(255,255,255,0.04)",
              color: filter === f ? "#7b7fff" : "var(--color-text-secondary)",
              border: `1px solid ${filter === f ? "rgba(91,95,237,0.4)" : "rgba(255,255,255,0.08)"}`,
            }}
          >
            {f === "all" ? "All Routes" : f === "diesel" ? "Diesel Only" : "Electrified"}
          </button>
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <GlassCard padding="md">
          <IndiaMap routes={filtered} />
          <div className="mt-3 flex items-center gap-4 text-[11px] text-[color:var(--color-text-secondary)]">
            <LegendDot color="#f87171" label="High emission diesel (>150t)" />
            <LegendDot color="#fbbf24" label="Mid emission diesel (50–150t)" />
            <LegendDot color="#34d399" label="Electrified EV route (<20t)" />
          </div>
        </GlassCard>
        <GlassCard padding="md">
          <div className="mb-3 text-[16px] font-semibold">Top Carbon-Emitting Routes</div>
          <div className="flex flex-col divide-y divide-white/5">
            {topEmitters.map((r, i) => {
              const potential = -(r.monthly_co2_tons * 0.85).toFixed(0);
              return (
                <div key={r.id} className="py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-[color:var(--color-text-tertiary)]">#{i + 1}</span>
                        <span className="truncate text-[13px] font-medium">{r.name}</span>
                      </div>
                      <div className="mt-1 text-[11px] text-[color:var(--color-text-secondary)]">
                        {r.monthly_co2_tons} tCO₂/mo · saving {potential} t
                      </div>
                    </div>
                    <StatusPill tone={r.is_electrified ? "healthy" : "critical"}>
                      {r.is_electrified ? "Electrified" : "Diesel"}
                    </StatusPill>
                  </div>
                </div>
              );
            })}
          </div>
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

function IndiaMap({ routes }: { routes: RouteRow[] }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInst = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    if (!mapInst.current) {
      mapInst.current = L.map(mapRef.current).setView([22.0, 78.0], 4);
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: "abcd",
        maxZoom: 20
      }).addTo(mapInst.current);
    }
    
    // Clear existing layers except tile layer
    mapInst.current.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.CircleMarker) {
        mapInst.current?.removeLayer(layer);
      }
    });

    const colorFor = (r: RouteRow) =>
      r.is_electrified ? "#34d399" : r.monthly_co2_tons > 150 ? "#f87171" : "#fbbf24";

    routes.forEach(r => {
      const c = colorFor(r);
      const origin = [r.origin_lat, r.origin_lon] as [number, number];
      const dest = [r.dest_lat, r.dest_lon] as [number, number];

      // Draw line
      L.polyline([origin, dest], {
        color: c,
        weight: 2,
        opacity: 0.6,
        dashArray: r.is_electrified ? "5,5" : undefined
      }).addTo(mapInst.current!);

      // Draw origin marker
      L.circleMarker(origin, {
        radius: 5,
        fillColor: c,
        color: "#fff",
        weight: 1,
        fillOpacity: 1
      }).addTo(mapInst.current!).bindTooltip(r.origin_city);

      // Draw dest marker
      L.circleMarker(dest, {
        radius: 5,
        fillColor: c,
        color: "#fff",
        weight: 1,
        fillOpacity: 1
      }).addTo(mapInst.current!).bindTooltip(r.dest_city);
    });

  }, [routes]);

  return <div ref={mapRef} className="w-full h-[520px] rounded-[12px] overflow-hidden" />;
}

// -------------------- 4. AI Carbon Advisor --------------------
function AdvisorTab() {
  const suggestions = [
    "Where can I cut Scope 1 the fastest?",
    "Which routes should I electrify next quarter?",
    "How am I tracking against my SBTi target?",
  ];
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "I analyze fleet telematics, Scope 1/3 emissions, and your geospatial routes to find carbon-reduction pathways. Ask me anything about your net-zero trajectory.",
    },
  ]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [priorities, setPriorities] = useState<Priority[]>([]);

  useEffect(() => {
    fetchPriorities().then(setPriorities);
  }, []);

  async function send(text: string) {
    const msg = text.trim();
    if (!msg) return;
    
    const userMsg = { role: "user", content: msg };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setPending(true);
    
    try {
      const res = await fetchAssistantReply(msg, messages);
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
    } catch (e) {
      console.error(e);
      setMessages((m) => [...m, { role: "assistant", content: "Sorry, I encountered an error." }]);
    } finally {
      setPending(false);
    }
  }

  return (
    <AgentSection>
      <SectionTitle eyebrow="Copilot" title="AI Carbon Advisor" />
      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <GlassCard padding="md" className="flex flex-col" >
          <div className="flex-1 space-y-3 overflow-y-auto pr-1" style={{ height: "70vh" }}>
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className="max-w-[80%] rounded-[14px] px-4 py-2.5 text-[13px] leading-relaxed"
                  style={{
                    background: m.role === "user" ? "rgba(91,95,237,0.18)" : "rgba(255,255,255,0.04)",
                    color: m.role === "user" ? "#f5f5f7" : "var(--color-text-primary)",
                    border: "1px solid rgba(255,255,255,0.06)",
                  }}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {pending && (
              <div className="flex justify-start">
                <div className="rounded-[14px] border border-white/5 bg-white/[0.04] px-4 py-2.5 text-[13px] text-[color:var(--color-text-secondary)]">
                  Thinking…
                </div>
              </div>
            )}
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1.5 text-[12px] text-[color:var(--color-text-secondary)] transition-colors hover:bg-white/[0.06]"
              >
                {s}
              </button>
            ))}
          </div>
          <div className="mt-3 flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send(input)}
              placeholder="Ask about emissions, routes, or electrification priorities…"
              className="flex-1 rounded-[12px] border border-white/8 bg-white/[0.03] px-4 py-2.5 text-[13px] outline-none focus:border-[rgba(91,95,237,0.5)]"
            />
            <button
              onClick={() => send(input)}
              className="flex h-10 w-10 items-center justify-center rounded-[12px] text-white"
              style={{ background: "#5b5fed" }}
              aria-label="Send"
            >
              <Send className="h-4 w-4" />
            </button>
            <button
              onClick={() => setMessages(messages.slice(0, 1))}
              className="rounded-[12px] border border-white/8 bg-white/[0.03] px-3 py-2 text-[12px] text-[color:var(--color-text-secondary)] hover:bg-white/[0.06]"
            >
              Clear
            </button>
          </div>
        </GlassCard>

        <GlassCard padding="md">
          <div className="mb-3 text-[16px] font-semibold">AI Electrification Priorities</div>
          <div className="flex flex-col gap-3 overflow-y-auto pr-1" style={{ height: "70vh" }}>
            {priorities.map((p) => (
              <div key={p.rank} className="rounded-[14px] border border-white/5 bg-white/[0.03] p-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="text-[13px] font-medium">#{p.rank} · {p.fleet_name}</div>
                    <div className="mt-0.5 text-[11px] text-[color:var(--color-text-secondary)]">
                      {p.asset_class} · {p.hub_city}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Impact</div>
                    <div className="text-[15px] font-semibold">{p.impact_score}<span className="text-[11px] text-[color:var(--color-text-secondary)]">/100</span></div>
                  </div>
                </div>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/5">
                  <div className="h-full rounded-full" style={{ width: `${p.impact_score}%`, background: "#5b5fed" }} />
                </div>
                <div className="mt-2 flex justify-between text-[11px] text-[color:var(--color-text-secondary)]">
                  <span>{p.potential_saving_tons.toLocaleString()} t/yr CO₂ saving</span>
                  <span>Readiness {p.readiness_index.toFixed(2)}</span>
                </div>
                <div className="mt-2 rounded-[10px] border border-[rgba(91,95,237,0.25)] bg-[rgba(91,95,237,0.08)] p-2 text-[12px]">
                  <span className="mr-1 text-[10px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-hover)]">AI</span>
                  {p.recommendation}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </AgentSection>
  );
}

// -------------------- 5. Generate Report --------------------
function ReportTab() {
  const [d, setD] = useState<CarbonDashboard | null>(null);
  const [routes, setRoutes] = useState<RouteRow[]>([]);
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [assets, setAssets] = useState<AssetClassEmissions[]>([]);

  useEffect(() => {
    fetchCarbonDashboard().then(setD);
    fetchRoutes().then(setRoutes);
    fetchCommitments().then(setCommitments);
    fetchPriorities().then(setPriorities);
    fetchAssetClassEmissions().then(setAssets);
  }, []);

  if (!d) return null;

  const now = new Date();
  const stamp = now.toLocaleString("en-IN", { dateStyle: "long", timeStyle: "short" });
  const topRoutes = [...routes].sort((a, b) => b.monthly_co2_tons - a.monthly_co2_tons).slice(0, 10);
  
  return (
    <AgentSection>
      <div className="flex items-center justify-between">
        <SectionTitle eyebrow="Export" title="Board-ready net-zero report" />
        <button
          onClick={() => window.print()}
          className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[12px] font-medium text-white"
          style={{ background: "#5b5fed" }}
        >
          <Printer className="h-3.5 w-3.5" /> Print / Save PDF
        </button>
      </div>
      <div className="rounded-[20px] bg-white p-8 text-[13px] text-slate-800 shadow-lg print:shadow-none">
        <header className="border-b border-slate-200 pb-4">
          <div className="text-[10px] font-semibold uppercase tracking-widest text-indigo-600">CarbonPulse Report</div>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">Fleet Net-Zero Intelligence Report</h1>
          <div className="mt-1 text-[12px] text-slate-500">Generated {stamp}</div>
        </header>

        <section className="mt-5">
          <h2 className="text-[14px] font-semibold text-slate-900">YoY Emissions Summary</h2>
          <table className="mt-2 w-full border-collapse text-[12px]">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr><th className="p-2">Metric</th><th className="p-2">Value</th></tr>
            </thead>
            <tbody>
              <tr className="border-t border-slate-200"><td className="p-2">Scope 1 YTD</td><td className="p-2">{d.scope1_ytd_tons.toLocaleString()} tCO₂e</td></tr>
              <tr className="border-t border-slate-200"><td className="p-2">Scope 3 YTD</td><td className="p-2">{d.scope3_ytd_tons.toLocaleString()} tCO₂e</td></tr>
              <tr className="border-t border-slate-200"><td className="p-2">CO₂ Avoided by EVs</td><td className="p-2">{d.ev_avoided_ytd_tons.toLocaleString()} tCO₂e</td></tr>
              <tr className="border-t border-slate-200"><td className="p-2">Net Zero Progress</td><td className="p-2">{d.net_zero_progress_pct}%</td></tr>
              <tr className="border-t border-slate-200"><td className="p-2">Routes Electrified</td><td className="p-2">{d.routes_electrified} / {d.total_routes}</td></tr>
            </tbody>
          </table>
        </section>

        <section className="mt-6">
          <h2 className="text-[14px] font-semibold text-slate-900">Top Emitting Routes</h2>
          <table className="mt-2 w-full border-collapse text-[12px]">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr><th className="p-2">Route</th><th className="p-2">Distance</th><th className="p-2">Powertrain</th><th className="p-2 text-right">tCO₂/mo</th></tr>
            </thead>
            <tbody>
              {topRoutes.map((r) => (
                <tr key={r.id} className="border-t border-slate-200">
                  <td className="p-2">{r.name}</td>
                  <td className="p-2">{r.distance_km} km</td>
                  <td className="p-2">{r.is_electrified ? "Electrified" : "Diesel"}</td>
                  <td className="p-2 text-right tabular-nums">{r.monthly_co2_tons}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="mt-6">
          <h2 className="text-[14px] font-semibold text-slate-900">Net Zero Commitments</h2>
          <table className="mt-2 w-full border-collapse text-[12px]">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr><th className="p-2">Organization</th><th className="p-2">Target</th><th className="p-2">Progress</th><th className="p-2">Status</th></tr>
            </thead>
            <tbody>
              {commitments.map((c) => {
                const pct = Math.min(100, Math.round((c.current_reduction_pct / c.reduction_target_pct) * 100));
                return (
                  <tr key={c.organization} className="border-t border-slate-200">
                    <td className="p-2">{c.organization}</td>
                    <td className="p-2">{c.reduction_target_pct}% by {c.target_year}</td>
                    <td className="p-2">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-32 overflow-hidden rounded-full bg-slate-200">
                          <div className="h-full rounded-full bg-indigo-500" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-[11px] text-slate-500">{c.current_reduction_pct.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="p-2">{c.status}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>

        <section className="mt-6">
          <h2 className="text-[14px] font-semibold text-slate-900">AI Electrification Priorities</h2>
          <table className="mt-2 w-full border-collapse text-[12px]">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr><th className="p-2">Rank</th><th className="p-2">Fleet</th><th className="p-2">Impact</th><th className="p-2">Saving t/yr</th><th className="p-2">Readiness</th></tr>
            </thead>
            <tbody>
              {priorities.map((p) => (
                <tr key={p.rank} className="border-t border-slate-200">
                  <td className="p-2">#{p.rank}</td>
                  <td className="p-2">{p.fleet_name}</td>
                  <td className="p-2">{p.impact_score}/100</td>
                  <td className="p-2 tabular-nums">{p.potential_saving_tons.toLocaleString()}</td>
                  <td className="p-2 tabular-nums">{p.readiness_index.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="mt-6">
          <h2 className="text-[14px] font-semibold text-slate-900">Emissions by Asset Class</h2>
          <table className="mt-2 w-full border-collapse text-[12px]">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr><th className="p-2">Asset Class</th><th className="p-2">Fleet Count</th><th className="p-2 text-right">Scope 1 t</th><th className="p-2 text-right">Scope 3 t</th></tr>
            </thead>
            <tbody>
              {assets.map((c) => (
                <tr key={c.asset_class} className="border-t border-slate-200">
                  <td className="p-2">{c.asset_class}</td>
                  <td className="p-2">{c.fleet_count}</td>
                  <td className="p-2 text-right tabular-nums">{c.scope1_tons.toLocaleString()}</td>
                  <td className="p-2 text-right tabular-nums">{c.scope3_tons.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </AgentSection>
  );
}

// -------------------- 6. Validation --------------------
function ValidationTab() {
  const [v, setV] = useState<CarbonValidation | null>(null);
  useEffect(() => {
    fetchCarbonValidation().then(setV);
  }, []);
  
  if (!v) return null;
  
  return (
    <AgentSection>
      <SectionTitle eyebrow="Validation" title="Estimate vs measured tCO₂" />

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Fleet-Wide Error" value={v.fleet_total_pct_err} suffix="%" decimals={2} status={{ tone: "healthy", label: "In band" }} />
        <StatCard label="Typical Route MAPE" value={v.mape_pct} suffix="%" decimals={1} status={{ tone: "healthy", label: "Strong" }} />
        <StatCard label="Routes Validated" value={v.routes_validated} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard label="Estimated" value={v.fleet_total_estimated_tco2} hint="tCO₂/mo" />
        <StatCard label="Fuel-Meter Measured" value={v.fleet_total_measured_tco2} hint="tCO₂/mo" />
      </div>

      <GlassCard padding="md">
        <div className="mb-3">
          <div className="eyebrow">Per-route</div>
          <div className="mt-1 text-[16px] font-semibold">Claim vs measured delta</div>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={v.per_route} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="route" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 10 }} axisLine={false} tickLine={false} interval={0} angle={-15} textAnchor="end" height={60} />
            <YAxis stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
            <Bar dataKey="estimated_tco2" name="Estimated" fill="#5b5fed" radius={[4,4,0,0]} />
            <Bar dataKey="measured_tco2" name="Measured" fill="#3e8ef7" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </GlassCard>

      <GlassCard padding="md">
        <div className="mb-3 text-[16px] font-semibold">Per-route breakdown</div>
        <table className="w-full text-[13px]">
          <thead className="text-left text-[color:var(--color-text-secondary)]">
            <tr><th className="pb-2 font-medium">Route</th><th className="pb-2 font-medium text-right">Our estimate</th><th className="pb-2 font-medium text-right">Meter reading</th><th className="pb-2 font-medium text-right">% off</th></tr>
          </thead>
          <tbody>
            {v.per_route.map((r) => (
              <tr key={r.route} className="border-t border-white/5">
                <td className="py-2">{r.route}</td>
                <td className="py-2 text-right tabular-nums">{r.estimated_tco2}</td>
                <td className="py-2 text-right tabular-nums">{r.measured_tco2}</td>
                <td className="py-2 text-right tabular-nums" style={{ color: r.pct_err > 4 ? "#fbbf24" : "#34d399" }}>
                  {r.over ? "+" : "−"}{r.pct_err.toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </GlassCard>
    </AgentSection>
  );
}
