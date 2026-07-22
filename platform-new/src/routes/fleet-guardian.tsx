import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, useEffect, useRef } from "react";
import { HeartPulse, Info } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  Legend,
} from "recharts";
import { AgentPage } from "@/components/urja/AgentPage";
import { AgentSection, SectionTitle } from "@/components/urja/AgentSections";
import { GlassCard } from "@/components/urja/GlassCard";
import { StatCard } from "@/components/urja/StatCard";
import { StatusPill } from "@/components/urja/StatusPill";
import {
  fetchGuardianAssets,
  fetchGuardianSummary,
  fetchGuardianHealth,
  fetchGuardianHistory,
  fetchGuardianRecommendation,
  type GuardianAsset,
  type GuardianSummary,
  type GuardianHealth,
  type GuardianCycle,
  type GuardianRecommendation,
} from "@/lib/guardian";

import { z } from "zod";

const searchSchema = z.object({
  batteryId: z.string().optional(),
});

export const Route = createFileRoute("/fleet-guardian")({
  validateSearch: searchSchema,
  head: () => ({
    meta: [
      { title: "Fleet Guardian — Urja" },
      { name: "description", content: "Battery health diagnostics, safety tracking, and automated service recommendations." },
    ],
  }),
  component: () => {
    const { batteryId } = Route.useSearch();
    return (
    <AgentPage
      agentName="Fleet Guardian"
      eyebrow="Agent · Asset Health"
      mission="Cycle-level Remaining Useful Life forecasting, anomaly detection, and LLM-generated maintenance reasoning."
      tabs={[
        { key: "dashboard", label: "Dashboard", icon: HeartPulse },
        { key: "about", label: "About", icon: Info },
      ]}
      renderContent={(k) => (k === "dashboard" ? <DashboardTab /> : <AboutTab />)}
      initialTab={batteryId ? "dashboard" : "dashboard"}
    />
  );
  },
});

const TIER_TONE: Record<string, "healthy" | "watch" | "critical"> = {
  Healthy: "healthy",
  Watch: "watch",
  Critical: "critical",
};

function DashboardTab() {
  const { batteryId } = Route.useSearch();
  const [summary, setSummary] = useState<GuardianSummary | null>(null);
  const [assets, setAssets] = useState<GuardianAsset[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(batteryId || null);
  
  const [health, setHealth] = useState<GuardianHealth | null>(null);
  const [history, setHistory] = useState<GuardianCycle[]>([]);
  const [rec, setRec] = useState<GuardianRecommendation | null>(null);

  const detailsRef = useRef<HTMLDivElement>(null);

  const handleAssetClick = (id: string) => {
    setSelectedId(id);
    setTimeout(() => {
      detailsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  useEffect(() => {
    fetchGuardianSummary().then(setSummary);
    fetchGuardianAssets().then((data) => {
      setAssets(data);
      if (!batteryId && data.length > 0) setSelectedId(data[0].battery_id);
    });
  }, [batteryId]);

  useEffect(() => {
    if (selectedId) {
      fetchGuardianHealth(selectedId).then(setHealth);
      fetchGuardianHistory(selectedId).then(setHistory);
      fetchGuardianRecommendation(selectedId).then(setRec);
    }
  }, [selectedId]);

  const asset = assets.find((a) => a.battery_id === selectedId);

  const chartData = useMemo(() => {
    if (!history.length || !health) return [];
    
    const lastCycle = history[history.length - 1].cycle;
    const lastSoh = history[history.length - 1].soh * 100;
    
    const projection: { cycle: number; soh: number | null; capacity: number | null; projected: number | null }[] = [];
    
    let c = lastCycle;
    let s = lastSoh;
    const eol = 70;
    const maxCycles = lastCycle + 120;
    
    while (c < maxCycles && s > eol - 5) {
      c += 1;
      s += (health.slope_blend * 100);
      projection.push({ cycle: c, soh: null, capacity: null, projected: +(s.toFixed(2)) });
    }
    
    return [
      ...history.map((h) => ({ cycle: h.cycle, soh: h.soh * 100, capacity: h.capacity, projected: null })),
      ...projection
    ];
  }, [history, health]);

  if (!summary || !assets.length || !asset || !health) return null;

  return (
    <AgentSection>
      <SectionTitle eyebrow="Fleet" title="Battery APM · fleet-wide" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard label="Fleet Average SoH" value={summary.average_soh} suffix="%" decimals={1} status={{ tone: "healthy", label: "Healthy" }} />
        <StatCard label="Assets Monitored" value={summary.total_assets} hint={`${summary.healthy_count}H · ${summary.watch_count}W · ${summary.critical_count}C`} />
        <StatCard label="Needs Attention" value={summary.watch_count + summary.critical_count} status={{ tone: "watch", label: "Review" }} />
      </div>

      <GlassCard padding="md">
        <div className="mb-4 flex items-center justify-between">
          <div className="text-[16px] font-semibold">Fleet Health Heatmap</div>
          <div className="flex gap-2">
            <StatusPill tone="healthy">Healthy</StatusPill>
            <StatusPill tone="watch">Watch</StatusPill>
            <StatusPill tone="critical">Critical</StatusPill>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-4">
          {assets.map((a) => (
            <button
              key={a.battery_id}
              onClick={() => handleAssetClick(a.battery_id)}
              className="rounded-[14px] border p-3 text-left transition-colors"
              style={{
                background: a.battery_id === selectedId ? "rgba(91,95,237,0.14)" : "rgba(255,255,255,0.03)",
                borderColor: a.battery_id === selectedId ? "rgba(91,95,237,0.4)" : "rgba(255,255,255,0.06)",
              }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-[12px] text-[color:var(--color-text-tertiary)]">{a.battery_id}</div>
                  <div className="text-[13px] font-medium">{a.display_name}</div>
                </div>
                <StatusPill tone={TIER_TONE[a.risk_tier]}>{a.risk_tier}</StatusPill>
              </div>
              <div className="mt-2 flex items-end justify-between">
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">SoH</div>
                  <div className="text-[18px] font-semibold tabular-nums">{(a.current_soh * 100).toFixed(1)}%</div>
                </div>
                <MiniSpark seed={a.current_soh * 100} />
              </div>
              <div className="mt-1 text-[11px] text-[color:var(--color-text-secondary)]">
                RUL {Math.max(0, Math.round(((a.current_soh * 100) - 70) * 12))} cycles
              </div>
            </button>
          ))}
        </div>
      </GlassCard>

      <AssetTable assets={assets} selectedId={selectedId} onSelect={handleAssetClick} />

      <div ref={detailsRef}>
        <GlassCard padding="md">
          <div className="mb-3 flex items-end justify-between">
            <div>
              <div className="eyebrow">Selected asset</div>
            <div className="mt-1 text-[16px] font-semibold">{asset.display_name} · Capacity Fade Trajectory</div>
          </div>
          <div className="flex gap-3 text-[11px] text-[color:var(--color-text-secondary)]">
            <span>Cycle {health.current_cycle}</span>
            <span>RUL {health.rul_cycles} ± {health.confidence_band_cycles}</span>
            <StatusPill tone="accent">{health.confidence_level}</StatusPill>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="cycle" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis domain={[60, 100]} stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
            <ReferenceLine y={70} stroke="#f87171" strokeDasharray="4 4" label={{ value: "70% EoL", fill: "#f87171", fontSize: 11, position: "insideTopRight" }} />
            <Line type="monotone" dataKey="soh" name="Actual SoH" stroke="#5b5fed" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="projected" name="Projected fade" stroke="#fbbf24" strokeWidth={2} strokeDasharray="5 4" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </GlassCard>

      <div className="grid gap-6 md:grid-cols-2">
        <GlassCard padding="md">
          <div className="mb-3 text-[15px] font-semibold">Anomaly status</div>
          <div className="flex flex-col divide-y divide-white/5">
            <div className="flex items-center justify-between py-3">
              <span className="text-[13px]">Temperature anomaly</span>
              <StatusPill tone={health.temperature_anomaly ? "critical" : "healthy"}>{health.temperature_anomaly ? "Flagged" : "Nominal"}</StatusPill>
            </div>
            <div className="flex items-center justify-between py-3">
              <span className="text-[13px]">Voltage-sag anomaly</span>
              <StatusPill tone={health.voltage_sag_anomaly ? "critical" : "healthy"}>{health.voltage_sag_anomaly ? "Flagged" : "Nominal"}</StatusPill>
            </div>
            <div className="flex items-center justify-between py-3">
              <span className="text-[13px]">Slope blend</span>
              <span className="text-[13px] tabular-nums">{health.slope_blend.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between py-3">
              <span className="text-[13px]">Risk tier</span>
              <StatusPill tone={TIER_TONE[health.risk_tier]}>{health.risk_tier}</StatusPill>
            </div>
          </div>
        </GlassCard>

        <GlassCard padding="md">
          <div className="mb-3 flex items-center gap-2">
            <div className="text-[15px] font-semibold">What the Agent Sees</div>
            <StatusPill tone="accent">LLM</StatusPill>
          </div>
          <div className="flex flex-col gap-3 text-[13px]">
            {rec ? (
              <>
                <ReasoningBlock title="Diagnosis" body={rec.explanation} />
                <ReasoningBlock title="Likely Cause" body={rec.likely_cause} />
                <ReasoningBlock title="Recommended Action" body={rec.recommendation} tone={rec.urgency === "immediate" ? "critical" : rec.urgency === "planned" ? "watch" : "healthy"} />
              </>
            ) : (
              <div className="text-[color:var(--color-text-secondary)] italic">
                LLM reasoning is unavailable (check GROQ_API_KEY on the backend).
              </div>
            )}
          </div>
        </GlassCard>
        </div>
      </div>
    </AgentSection>
  );
}

function ReasoningBlock({ title, body, tone }: { title: string; body: string; tone?: "healthy" | "watch" | "critical" }) {
  return (
    <div className="rounded-[12px] border border-white/5 bg-white/[0.03] p-3">
      <div className="flex items-center gap-2">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-[color:var(--color-text-secondary)]">{title}</div>
        {tone && <StatusPill tone={tone}>{tone === "critical" ? "Immediate" : tone === "watch" ? "Planned" : "Monitor"}</StatusPill>}
      </div>
      <div className="mt-1 leading-relaxed">{body}</div>
    </div>
  );
}

function MiniSpark({ seed }: { seed: number }) {
  const points = Array.from({ length: 12 }, (_, i) => {
    const y = 100 - (i * (100 - seed)) / 12 + (Math.sin(i + seed) * 1.5);
    return `${(i / 11) * 60},${30 - ((y - 60) / 40) * 26}`;
  }).join(" ");
  return (
    <svg width={64} height={30} viewBox="0 0 60 30">
      <polyline points={points} fill="none" stroke="#5b5fed" strokeWidth={1.5} />
    </svg>
  );
}

function AboutTab() {
  return (
    <AgentSection>
      <SectionTitle eyebrow="About" title="Methodology & scope" />
      <GlassCard padding="lg">
        <h3 className="text-[16px] font-semibold">RUL confidence system</h3>
        <p className="mt-3 text-[13px] leading-relaxed text-[color:var(--color-text-secondary)]">
          Remaining Useful Life is estimated per battery using a blended slope model.
          When we have <strong className="text-[color:var(--color-text-primary)]">enough cycle history</strong> for
          an individual asset, the forecast is reported as{" "}
          <span style={{ color: "#7b7fff" }}>asset-specific</span> — the model leans
          on that asset's observed capacity fade slope, with confidence bands sized
          from its own residuals.
        </p>
        <p className="mt-3 text-[13px] leading-relaxed text-[color:var(--color-text-secondary)]">
          When cycle history is thin, the estimate falls back to a{" "}
          <span style={{ color: "#7b7fff" }}>population-estimate</span> mode: the
          forecast is anchored to the healthy-cohort baseline for the same chemistry
          and duty profile, with wider confidence bands to reflect that we have not
          yet learned this specific asset's fade signature.
        </p>
        <p className="mt-3 text-[13px] leading-relaxed text-[color:var(--color-text-secondary)]">
          Anomaly flags (temperature, voltage sag) are surfaced separately from the
          RUL estimate; a flagged anomaly does not by itself reduce RUL, but it does
          influence urgency of the recommended action.
        </p>
      </GlassCard>
      <GlassCard padding="lg">
        <h3 className="text-[16px] font-semibold">What this build is (and isn't)</h3>
        <ul className="mt-3 flex flex-col gap-2 text-[13px]">
          <li className="flex gap-2"><span className="mt-1 h-1.5 w-1.5 rounded-full" style={{ background: "#34d399" }} /><span><strong>Is:</strong> a battery Asset Performance Management view — RUL forecasting, anomaly detection, and LLM-generated maintenance reasoning surfaced per asset.</span></li>
          <li className="flex gap-2"><span className="mt-1 h-1.5 w-1.5 rounded-full" style={{ background: "#34d399" }} /><span><strong>Is:</strong> transparent about model confidence — the confidence level (asset-specific vs population-estimate) is shown alongside every RUL number.</span></li>
          <li className="flex gap-2"><span className="mt-1 h-1.5 w-1.5 rounded-full" style={{ background: "#f87171" }} /><span><strong>Isn't:</strong> a BMS replacement — this is downstream analytics over telemetry, not a real-time cell-balancing controller.</span></li>
          <li className="flex gap-2"><span className="mt-1 h-1.5 w-1.5 rounded-full" style={{ background: "#f87171" }} /><span><strong>Isn't:</strong> a warranty or safety certification tool.</span></li>
        </ul>
      </GlassCard>
    </AgentSection>
  );
}


function AssetTable({ assets, selectedId, onSelect }: { assets: GuardianAsset[], selectedId: string | null, onSelect: (id: string) => void }) {
  const TIER_ORDER: Record<string, number> = { Critical: 0, Watch: 1, Healthy: 2 };
  const sorted = [...assets].sort((a, b) => TIER_ORDER[a.risk_tier] - TIER_ORDER[b.risk_tier]);
  return (
    <GlassCard padding="md">
      <div className="mb-4 text-[16px] font-semibold">Fleet Inventory</div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-[13px]">
          <thead>
            <tr className="border-b border-white/5 text-[color:var(--color-text-tertiary)]">
              <th className="py-2 pr-4 font-medium uppercase tracking-wider text-[11px]">Asset ID</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">SoH</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">Risk Tier</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">RUL (cycles)</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(a => (
              <AssetRow key={a.battery_id} asset={a} selected={a.battery_id === selectedId} onSelect={onSelect} />
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
}

function AssetRow({ asset, selected, onSelect }: { asset: GuardianAsset, selected: boolean, onSelect: (id: string) => void }) {
  const [health, setHealth] = useState<GuardianHealth | null>(null);
  useEffect(() => {
    fetchGuardianHealth(asset.battery_id).then(setHealth);
  }, [asset.battery_id]);

  return (
    <tr 
      onClick={() => onSelect(asset.battery_id)}
      className="cursor-pointer border-b border-white/5 transition-colors hover:bg-white/[0.04]"
      style={{ background: selected ? 'rgba(91,95,237,0.1)' : 'transparent' }}
    >
      <td className="py-3 pr-4">
        <div className="font-medium text-white">{asset.battery_id}</div>
        <div className="text-[11px] text-[color:var(--color-text-tertiary)]">{asset.display_name}</div>
      </td>
      <td className="py-3 px-4 tabular-nums text-[14px]">{(asset.current_soh * 100).toFixed(1)}%</td>
      <td className="py-3 px-4"><StatusPill tone={TIER_TONE[asset.risk_tier]}>{asset.risk_tier}</StatusPill></td>
      <td className="py-3 px-4 tabular-nums text-[color:var(--color-text-secondary)] text-[14px]">
        {health ? health.rul_cycles : '...'}
      </td>
      <td className="py-3 px-4">
        {health ? (
          <div className="flex flex-col">
            <span className={health.confidence_level === 'asset_specific' ? 'text-white' : 'text-yellow-400'}>
              {health.confidence_level === 'asset_specific' ? 'asset-specific' : 'population'}
            </span>
            <span className="text-[11px] text-[color:var(--color-text-tertiary)]">± {health.confidence_band_cycles} cycles</span>
          </div>
        ) : '...'}
      </td>
    </tr>
  );
}
