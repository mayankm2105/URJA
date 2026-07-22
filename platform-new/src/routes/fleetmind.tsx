import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { Truck, Zap, ShieldCheck } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from "recharts";
import { AgentPage } from "@/components/urja/AgentPage";
import { AgentSection, SectionTitle } from "@/components/urja/AgentSections";
import { GlassCard } from "@/components/urja/GlassCard";
import { StatCard } from "@/components/urja/StatCard";
import { StatusPill } from "@/components/urja/StatusPill";
import {
  fetchFleet,
  fetchAsset,
  fetchMaintenance,
  fetchElectrification,
  fetchValidation,
  fetchValidationCells,
  type FleetResponse,
  type AssetSummary,
  type AssetDetail,
  type MaintenanceResponse,
  type ElectrificationResponse,
  type ValidationResponse,
  type ValidationCellsResponse,
  type HealthBand as SoHBand,
  fetchElecCandidate,
  type ElecCandidate,
} from "@/lib/fleet";

import { z } from "zod";

const searchSchema = z.object({
  assetId: z.string().optional(),
});

export const Route = createFileRoute("/fleetmind")({
  validateSearch: searchSchema,
  head: () => ({
    meta: [
      { title: "FleetMind — Urja" },
      { name: "description", content: "Battery-aware fleet electrification and EV procurement planning." },
    ],
  }),
  component: () => (
    <AgentPage
      agentName="FleetMind"
      eyebrow="Agent · Electrification"
      mission="Battery-aware asset health, EV replacement mapping, and NASA-validated model adequacy."
      tabs={[
        { key: "fleet", label: "Fleet", icon: Truck },
        { key: "electrify", label: "Electrify", icon: Zap },
        { key: "validation", label: "Validation", icon: ShieldCheck },
      ]}
      renderContent={(k) => (k === "fleet" ? <FleetTab /> : k === "electrify" ? <ElectrifyTab /> : <ValidationTab />)}
    />
  ),
});

const BAND_TONE: Record<SoHBand, "healthy" | "watch" | "critical"> = {
  healthy: "healthy",
  aging: "watch",
  end_of_life: "critical",
};

const BAND_TONE_COLOR: Record<SoHBand, string> = {
  healthy: "#34d399",
  aging: "#fbbf24",
  end_of_life: "#f87171",
};

function rulBig(a: AssetSummary): string {
  if (a.horizon_capped) return ">10 years";
  if (a.rul_days <= 0) return "0 days";
  if (a.rul_days >= 365) return `${(a.rul_days / 365).toFixed(1)} years`;
  return `${a.rul_days.toFixed(0)} days`;
}


// -------------------- 1. Fleet --------------------
function FleetTab() {
  const { assetId } = Route.useSearch();
  const [fleetData, setFleetData] = useState<FleetResponse | null>(null);
  const [maintData, setMaintData] = useState<MaintenanceResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(assetId || null);
  const [detail, setDetail] = useState<AssetDetail | null>(null);

  useEffect(() => {
    fetchFleet().then((data) => {
      setFleetData(data);
      if (!assetId && data.assets.length > 0) setSelectedId(data.assets[0].id);
    });
    fetchMaintenance().then(setMaintData);
  }, []);

  useEffect(() => {
    if (selectedId) fetchAsset(selectedId, true).then(setDetail);
  }, [selectedId]);

  const chartData = useMemo(() => {
    if (!detail) return [];
    const hist = detail.history.map((h) => ({ 
      x: h.day, 
      observed: h.soh_observed != null ? h.soh_observed * 100 : undefined, 
      true: h.soh_true != null ? h.soh_true * 100 : undefined
    }));
    const proj = detail.projection.map((p) => ({ 
      x: p.day, 
      predicted: p.soh_predicted != null ? p.soh_predicted * 100 : undefined 
    }));
    return [...hist, ...proj];
  }, [detail]);

  if (!fleetData || !maintData || !detail || !selectedId) return null;

  const asset = fleetData.assets.find((a) => a.id === selectedId)!;

  return (
    <AgentSection>
      <SectionTitle eyebrow="Fleet" title="Battery health and maintenance" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Fleet Avg SoH" value={fleetData.meta.fleet_soh_avg * 100} suffix="%" decimals={1} status={{ tone: "healthy", label: "Healthy" }} />
        <StatCard label="At Risk" value={fleetData.meta.at_risk_count} status={{ tone: "watch", label: "Watch" }} />
        <StatCard label="End of Life" value={fleetData.meta.end_of_life_count} status={{ tone: "critical", label: "Replace" }} />
        <StatCard label="Swaps Overdue" value={maintData.meta.overdue} status={{ tone: "critical", label: "Overdue" }} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
        <GlassCard padding="md">
          <div className="mb-3 text-[15px] font-semibold">Assets</div>
          <div className="flex flex-col gap-1">
            {fleetData.assets.map((a) => (
              <button
                key={a.id}
                onClick={() => setSelectedId(a.id)}
                className="rounded-[10px] p-2 text-left transition-colors"
                style={{
                  background: a.id === selectedId ? "rgba(91,95,237,0.14)" : "transparent",
                  border: `1px solid ${a.id === selectedId ? "rgba(91,95,237,0.35)" : "transparent"}`,
                }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-medium">{a.name}</span>
                  <StatusPill tone={BAND_TONE[a.soh_band]}>{a.soh_band}</StatusPill>
                </div>
                <div className="mt-1 text-[11px] text-[color:var(--color-text-secondary)]">
                  {a.id} · {a.vehicle_type} · {a.region}
                </div>
                <div className="mt-1 text-[11px] text-[color:var(--color-text-tertiary)]">
                  {a.chemistry} · SoH {Math.round(a.soh * 100)}% · {a.dominant_driver}
                </div>
              </button>
            ))}
          </div>
        </GlassCard>

        <div className="flex flex-col gap-6">
          <GlassCard padding="md">
            <div className="mb-3 flex items-end justify-between">
              <div>
                <div className="eyebrow">Selected asset</div>
                <div className="mt-1 text-[16px] font-semibold">{asset.name} · SoH history & projection</div>
              </div>
              <StatusPill tone={BAND_TONE[asset.soh_band]}>{asset.soh_band}</StatusPill>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="x" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} label={{ value: "Days", fill: "#5c5c68", fontSize: 10, position: "insideBottom", offset: -2 }} />
                <YAxis domain={[60, 100]} stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
                <Line type="monotone" dataKey="observed" name="Observed" stroke="#5b5fed" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="true" name="True" stroke="#3e8ef7" strokeWidth={2} dot={false} strokeDasharray="4 4" />
                <Line type="monotone" dataKey="predicted" name="Predicted" stroke="#fbbf24" strokeWidth={2} dot={false} strokeDasharray="6 3" />
              </LineChart>
                        </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 gap-4 xl:grid-cols-4">
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Current SoH</div>
                <div className="mt-1 text-[20px] font-semibold tabular-nums" style={{ color: BAND_TONE_COLOR[asset.soh_band] }}>
                  {(asset.soh * 100).toFixed(1)}%
                </div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Remaining Useful Life</div>
                <div className="mt-1 text-[20px] font-semibold tabular-nums">{rulBig(asset)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Equivalent Full Cycles</div>
                <div className="mt-1 text-[16px] font-semibold tabular-nums">{asset.efc_total.toLocaleString()} EFC</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Dominant Fade Driver</div>
                <div className="mt-1 text-[14px] font-medium text-[color:var(--color-text-primary)]">{asset.dominant_driver}</div>
              </div>
            </div>
          </GlassCard>

          <div className="grid gap-6 md:grid-cols-2">
            <GlassCard padding="md">
              <div className="mb-3 text-[15px] font-semibold">Fade breakdown</div>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Cycle loss</div>
                  <div className="mt-1 text-[24px] font-semibold">{Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%</div>
                </div>
                <div className="flex-1">
                  <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Calendar loss</div>
                  <div className="mt-1 text-[24px] font-semibold">{100 - Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%</div>
                </div>
              </div>
              <div className="mt-3 flex h-2 overflow-hidden rounded-full">
                <div style={{ width: `${Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%`, background: "#5b5fed" }} />
                <div style={{ width: `${100 - Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%`, background: "#3e8ef7" }} />
              </div>
              <p className="mt-4 text-[12px] leading-relaxed text-[color:var(--color-text-secondary)]">{detail.brief}</p>
            </GlassCard>

            <GlassCard padding="md">
              <div className="mb-3 text-[15px] font-semibold">Recommendations</div>
              <ul className="flex flex-col gap-2 text-[13px]">
                {detail.recommendations.map((r, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full" style={{ background: "#5b5fed" }} />
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </GlassCard>
          </div>
        </div>
      </div>

      <GlassCard padding="md">
        <div className="mb-4 flex items-end justify-between">
          <div className="text-[16px] font-semibold">Maintenance work-order queue</div>
          <div className="flex gap-4 text-[11px] text-[color:var(--color-text-secondary)]">
            <span>Scheduled {maintData.meta.scheduled}</span>
            <span>Overdue {maintData.meta.overdue}</span>
            <span>Bays {maintData.meta.service_bays}</span>
            <span>Parts LT {maintData.meta.parts_lead_days}d</span>
            <span>Queue clear day {maintData.meta.queue_clears_day}</span>
          </div>
        </div>
        <table className="w-full text-[13px]">
          <thead className="text-left text-[color:var(--color-text-secondary)]">
            <tr>
              <th className="pb-2 font-medium">Asset</th>
              <th className="pb-2 font-medium">Action</th>
              <th className="pb-2 font-medium text-right">Start day</th>
              <th className="pb-2 font-medium text-right">Complete day</th>
              <th className="pb-2 font-medium">Priority</th>
              <th className="pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {maintData.work_orders.map((w) => (
              <tr key={w.asset_id + w.action} className="border-t border-white/5">
                <td className="py-2">{w.asset_id}</td>
                <td className="py-2">{w.action}</td>
                <td className="py-2 text-right tabular-nums">{w.recommended_start_day}</td>
                <td className="py-2 text-right tabular-nums">{w.completion_day}</td>
                <td className="py-2">
                  <StatusPill tone={w.priority === 1 ? "critical" : w.priority === 2 ? "watch" : "healthy"}>P{w.priority}</StatusPill>
                </td>
                <td className="py-2">
                  {w.overdue ? <StatusPill tone="critical">Overdue</StatusPill> : <StatusPill tone="healthy">On plan</StatusPill>}
                </td>
              </tr>
            ))}
          </tbody>
                </table>
        {maintData.plan && (
          <div className="mt-4 rounded-[12px] border border-[rgba(91,95,237,0.25)] bg-[rgba(91,95,237,0.06)] p-3">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-hover)]">Asset Health Brief</div>
            <div className="mt-1 text-[13px] leading-relaxed text-[color:var(--color-text-secondary)]">
              {maintData.plan}
            </div>
          </div>
        )}
      </GlassCard>
    </AgentSection>
  );
}

// -------------------- 2. Electrify --------------------
const ACTION_TONE = {
  "Electrify now": "healthy",
  "Pilot deployment": "watch",
  "Defer/monitor": "critical",
} as const;

const ACTION_TONE_FIX: Record<string, "healthy" | "watch" | "critical"> = {
  "Electrify now": "healthy",
  "Pilot deployment": "watch",
  "Defer / monitor": "critical",
};
function ElectrifyTab() {
  const [elecData, setElecData] = useState<ElectrificationResponse | null>(null);
  const [enriched, setEnriched] = useState<Record<string, ElecCandidate>>({});
  
  useEffect(() => {
    fetchElectrification().then(async (data) => {
      setElecData(data);
      try {
        const details = await Promise.all(data.candidates.map(c => fetchElecCandidate(c.id, true)));
        const map: Record<string, ElecCandidate> = {};
        for (const d of details) map[d.id] = d;
        setEnriched(map);
      } catch(e) {
        console.error("Failed to fetch detailed AI briefs", e);
      }
    });
  }, []);
  
  if (!elecData) return null;

  const inr = (n: number) => `₹${(n / 10_000_000).toFixed(1)} Cr`;
  return (
    <AgentSection>
      <SectionTitle eyebrow="Procurement" title="Electrification candidates" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Electrify Now" value={elecData.meta.electrify_now} status={{ tone: "healthy", label: "Ready" }} />
        <StatCard label="Pilot" value={elecData.meta.pilot} status={{ tone: "watch", label: "Test" }} />
        <StatCard label="Defer" value={elecData.meta.defer} status={{ tone: "critical", label: "Hold" }} />
        <StatCard label="Avg Readiness" value={elecData.meta.avg_readiness} decimals={2} />
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Phase-1 Capex" value={elecData.meta.phase1_capex_inr / 10_000_000} decimals={1} prefix="₹" suffix=" Cr" />
        <StatCard label="Phase-1 Max Lead" value={elecData.meta.phase1_max_lead_weeks} suffix=" wks" />
        <StatCard label="Fleet Annual Saving" value={elecData.meta.fleet_annual_saving_inr / 10_000_000} decimals={1} prefix="₹" suffix=" Cr" status={{ tone: "healthy", label: "Saving" }} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        {elecData.candidates.map((c) => (
          <GlassCard key={c.id} padding="md">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-[16px] font-semibold">{c.name}</div>
                <div className="mt-0.5 text-[12px] text-[color:var(--color-text-secondary)]">
                  {c.vehicle_class} · {c.region} · {c.powertrain}
                </div>
              </div>
              <StatusPill tone={ACTION_TONE_FIX[c.action]}>{c.action}</StatusPill>
            </div>

            <div className="mt-3 grid grid-cols-3 gap-3 text-[12px]">
              <Metric label="Daily km" value={`${c.daily_km}`} />
              <Metric label="Payload" value={`${c.payload_kg} kg`} />
              <Metric label="Dwell" value={`${c.dwell_hours} h`} />
            </div>

            <div className="mt-4">
              <div className="flex items-center justify-between text-[12px]">
                <span className="text-[color:var(--color-text-secondary)]">Readiness Index</span>
                <span className="tabular-nums">{c.readiness_index.toFixed(2)} · conf {c.confidence.toFixed(2)}</span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/5">
                <div className="h-full rounded-full" style={{ width: `${c.readiness_index * 100}%`, background: "#5b5fed" }} />
              </div>
            </div>

            <div className="mt-3 rounded-[10px] border border-white/5 bg-white/[0.03] p-2 text-[12px] text-[color:var(--color-text-secondary)]">
              <span className="font-medium text-[color:var(--color-text-primary)]">Binding constraint: </span>
              {c.binding_constraint}
            </div>

            <div className="mt-3 grid grid-cols-5 gap-1 text-[11px]">
              {(["range","charging","payload","duty","tco"] as const).map((k) => (
                <div key={k} className="rounded-[8px] border border-white/5 bg-white/[0.02] p-2 text-center">
                  <div className="uppercase tracking-wider text-[color:var(--color-text-tertiary)]">{k}</div>
                  <div className="mt-1 font-semibold tabular-nums">{c.subscores[k].toFixed(2)}</div>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-[12px] border border-[rgba(91,95,237,0.25)] bg-[rgba(91,95,237,0.06)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-hover)]">Recommended EV</div>
              <div className="mt-1 text-[13px] font-medium">{c.recommended_ev.model} · {c.recommended_ev.oem}</div>
              <div className="mt-1 grid grid-cols-4 gap-2 text-[11px] text-[color:var(--color-text-secondary)]">
                <span>Range {c.recommended_ev.range_km} km</span>
                <span>Payload {c.recommended_ev.payload_kg} kg</span>
                <span>{inr(c.recommended_ev.price_inr)}</span>
                <span>LT {c.recommended_ev.lead_weeks} wk · {c.recommended_ev.fast_charge ? "Fast Charge" : "Slow Charge"}</span>
              </div>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-3 text-[12px]">
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">EV ₹/km</div>
                <div className="mt-1 font-semibold tabular-nums">{c.economics.ev_cost_per_km.toFixed(1)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">Fuel ₹/km</div>
                <div className="mt-1 font-semibold tabular-nums">{c.economics.fuel_cost_per_km.toFixed(1)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">Saving/km</div>
                <div className="mt-1 font-semibold tabular-nums" style={{ color: "#34d399" }}>+{c.economics.saving_per_km.toFixed(1)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">Payback</div>
                <div className="mt-1 font-semibold tabular-nums">{c.economics.payback_years?.toFixed(1) ?? "N/A"} yr</div>
              </div>
            </div>

            <div className="mt-3 text-[11px] text-[color:var(--color-text-secondary)]">
              Annual saving: <span className="text-[color:var(--color-text-primary)]">{inr(c.economics.annual_saving_inr)}</span>
            </div>

            <div className="mt-3">
              <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Alternatives</div>
              <div className="mt-1 flex flex-wrap gap-2">
                {c.alternatives.map((alt) => (
                  <span key={alt.model} className="rounded-full border border-white/5 bg-white/[0.03] px-2.5 py-1 text-[11px]">
                    {alt.oem} {alt.model} · {alt.chemistry} · {inr(alt.price_inr)}
                  </span>
                ))}
              </div>
            </div>
            
            {/* Operational profile text added from standalone */}
            <div className="mt-4 text-[12px] leading-relaxed text-[color:var(--color-text-secondary)]">
              {c.daily_km} km/day · {c.payload_kg} kg payload · {c.dwell_hours} h depot dwell ·
              {c.returns_to_depot ? " returns to depot" : " no depot return"} ·
              {c.route_fixed ? " fixed route" : " variable route"}.
            </div>

            {/* AI Brief fetched via fetchElecCandidate */}
            {enriched[c.id]?.brief && (
              <div className="mt-3 rounded-[12px] border border-[rgba(91,95,237,0.25)] bg-[rgba(91,95,237,0.06)] p-3">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-hover)]">Procurement Recommendation · AI Agent</div>
                <div className="mt-1 text-[12px] leading-relaxed text-[color:var(--color-text-secondary)]">
                  {enriched[c.id].brief}
                </div>
              </div>
            )}
          </GlassCard>
        ))}
      </div>
    </AgentSection>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
      <div className="text-[10px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">{label}</div>
      <div className="mt-1 text-[13px] font-semibold tabular-nums">{value}</div>
    </div>
  );
}

// -------------------- 3. Validation --------------------
function ValidationTab() {
  const [valData, setValData] = useState<ValidationResponse | null>(null);
  const [valCells, setValCells] = useState<ValidationCellsResponse | null>(null);
  const [cellIdx, setCellIdx] = useState(0);

  useEffect(() => {
    fetchValidation().then(setValData);
    fetchValidationCells().then(setValCells);
  }, []);

  if (!valData || !valCells || valCells.cells.length === 0) return null;

  const cell = valCells.cells[cellIdx];
  
  // Transform per_cell data to have rul_abs_err_cycles flatten 
  const chartData = valData.knee_onset_forecast.per_cell.map(pc => ({
    label: pc.cell,
    soh_mae_pct: pc.soh_mae_pct,
    rul_abs_err_cycles: pc.rul?.rul_abs_err_cycles ?? 0
  }));

  const fcByCell = new Map(valData.knee_onset_forecast.per_cell.map((r) => [r.cell, r]));

  return (
    <AgentSection>
      <SectionTitle eyebrow="Validation" title="NASA battery aging dataset" />
      <p className="text-[13px] text-[color:var(--color-text-secondary)]">Source · {valData.source}</p>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Mean RMSE" value={valData.model_adequacy.mean_rmse_pct} suffix="%" decimals={2} status={{ tone: "healthy", label: "Strong" }} />
        <StatCard label="Max RMSE" value={valData.model_adequacy.max_rmse_pct} suffix="%" decimals={2} />
        <StatCard label="Mean SoH MAE" value={valData.knee_onset_forecast.soh_mae_pct_mean} suffix="%" decimals={2} />
        <StatCard label="Max SoH MAE" value={valData.knee_onset_forecast.soh_mae_pct_max} suffix="%" decimals={2} />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard label="Median RUL abs err" value={valData.knee_onset_forecast.rul_median_abs_err_cycles} suffix=" cycles" />
        <StatCard label="Mean RUL abs err" value={valData.knee_onset_forecast.rul_mean_abs_err_cycles} decimals={1} suffix=" cycles" />
      </div>

      <GlassCard padding="md">
        <div className="mb-3 text-[16px] font-semibold">Per-cell knee-onset accuracy</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="label" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
            <Bar dataKey="soh_mae_pct" name="SoH MAE %" fill="#5b5fed" radius={[4,4,0,0]} />
            <Bar dataKey="rul_abs_err_cycles" name="RUL |err| cycles" fill="#3e8ef7" radius={[4,4,0,0]} />
          </BarChart>
                    </ResponsiveContainer>

        <div className="mt-6">
          <div className="mb-3 text-[15px] font-semibold">Per-cell forecast — fit early life ({valData.knee_onset_forecast.fit_window}), predict 80% knee</div>
          <table className="w-full text-[13px]">
            <thead className="text-left text-[color:var(--color-text-secondary)]">
              <tr>
                <th className="pb-2 font-medium">Cell</th>
                <th className="pb-2 font-medium">Fit RMSE</th>
                <th className="pb-2 font-medium">Fit window</th>
                <th className="pb-2 font-medium">SoH MAE</th>
                <th className="pb-2 font-medium">True EoL</th>
                <th className="pb-2 font-medium">Pred EoL</th>
                <th className="pb-2 font-medium">RUL err</th>
              </tr>
            </thead>
            <tbody>
              {valData.model_adequacy.per_cell.map((m) => {
                const f = fcByCell.get(m.cell);
                const r = f?.rul;
                const predEol = r ? r.true_eol_cycle - r.rul_true_cycles + r.rul_pred_cycles : null;
                return (
                  <tr key={m.cell} className="border-t border-white/5">
                    <td className="py-2 tabular-nums">{m.cell}</td>
                    <td className="py-2 tabular-nums">{m.in_sample_rmse_pct.toFixed(2)}%</td>
                    <td className="py-2 tabular-nums text-[color:var(--color-text-secondary)]">{r ? `${r.fit_window_cycles}cyc → ${r.cutoff_soh_pct}%` : "—"}</td>
                    <td className="py-2 tabular-nums">{f ? `${f.soh_mae_pct.toFixed(1)}pp` : "—"}</td>
                    <td className="py-2 tabular-nums">{r ? `cyc ${r.true_eol_cycle}` : "—"}</td>
                    <td className="py-2 tabular-nums">{predEol != null ? `cyc ${predEol}` : "—"}</td>
                    <td className="py-2 tabular-nums">
                      {r ? (
                        <StatusPill tone={r.rul_abs_err_cycles <= 25 ? "healthy" : "critical"}>
                          {r.rul_abs_err_cycles.toFixed(0)} cyc
                        </StatusPill>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

      </GlassCard>

      <GlassCard padding="md">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div className="text-[16px] font-semibold">Reference cells</div>
          <div className="flex gap-2">
            {valCells.cells.map((c, i) => (
              <button
                key={c.label}
                onClick={() => setCellIdx(i)}
                className="rounded-full px-3 py-1 text-[11px] font-medium"
                style={{
                  background: i === cellIdx ? "rgba(91,95,237,0.18)" : "rgba(255,255,255,0.04)",
                  color: i === cellIdx ? "#7b7fff" : "var(--color-text-secondary)",
                  border: `1px solid ${i === cellIdx ? "rgba(91,95,237,0.4)" : "rgba(255,255,255,0.08)"}`,
                }}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
        <div className="mb-3 grid grid-cols-2 gap-3 text-[12px] sm:grid-cols-4">
          <Metric label="Ambient" value={`${cell.ambient_c} °C`} />
          <Metric label="Cycles" value={`${cell.cycles}`} />
          <Metric label="SoH start → end" value={`${cell.soh_start} → ${cell.soh_end}%`} />
          <Metric label="True EoL cycle" value={`${cell.true_eol_cycle}`} />
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={cell.series} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="efc" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "rgba(15,17,23,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9a9aa8" }} />
            <Line type="monotone" dataKey="soh_observed" name="SoH %" stroke="#5b5fed" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="capacity_ah" name="Capacity Ah" stroke="#34d399" strokeWidth={2} dot={false} />
          </LineChart>
                    </ResponsiveContainer>
      </GlassCard>
    </AgentSection>
  );
}
