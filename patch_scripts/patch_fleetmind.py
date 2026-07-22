import re

with open("platform-new/src/routes/fleetmind.tsx", "r") as f:
    code = f.read()

# Chunk 1: Imports
code = code.replace("""import { useMemo, useState } from "react";""", """import { useMemo, useState, useEffect } from "react";""")
code = code.replace("""import {
  ASSETS,
  ASSET_DETAILS,
  FLEET_META,
  WORK_ORDERS,
  MAINT_META,
  ELEC_META,
  ELEC_CANDIDATES,
  NASA_CELLS,
  VALIDATION,
  type SoHBand,
} from "@/lib/mock/fleetmind";""", """import {
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
} from "@/lib/fleet";""")

# Chunk 2: FleetTab
code = code.replace("""function FleetTab() {
  const [selectedId, setSelectedId] = useState(ASSETS[0].id);
  const asset = ASSETS.find((a) => a.id === selectedId)!;
  const detail = ASSET_DETAILS[selectedId];
  const chartData = useMemo(() => {
    const hist = detail.history.map((h) => ({ x: h.day, observed: h.observed_soh, true: h.true_soh }));
    const proj = detail.projection.map((p) => ({ x: p.day, predicted: p.predicted_soh }));
    return [...hist, ...proj];
  }, [detail]);

  return (
    <AgentSection>
      <SectionTitle eyebrow="Fleet" title="Battery health and maintenance" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Fleet Avg SoH" value={FLEET_META.fleet_soh_avg} suffix="%" decimals={1} status={{ tone: "healthy", label: "Healthy" }} />
        <StatCard label="At Risk" value={FLEET_META.at_risk_count} status={{ tone: "watch", label: "Watch" }} />
        <StatCard label="End of Life" value={FLEET_META.end_of_life_count} status={{ tone: "critical", label: "Replace" }} />
        <StatCard label="Swaps Overdue" value={FLEET_META.swaps_overdue} status={{ tone: "critical", label: "Overdue" }} />
      </div>""", """function FleetTab() {
  const [fleetData, setFleetData] = useState<FleetResponse | null>(null);
  const [maintData, setMaintData] = useState<MaintenanceResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<AssetDetail | null>(null);

  useEffect(() => {
    fetchFleet().then((data) => {
      setFleetData(data);
      if (data.assets.length > 0) setSelectedId(data.assets[0].id);
    });
    fetchMaintenance().then(setMaintData);
  }, []);

  useEffect(() => {
    if (selectedId) fetchAsset(selectedId).then(setDetail);
  }, [selectedId]);

  const chartData = useMemo(() => {
    if (!detail) return [];
    const hist = detail.history.map((h) => ({ x: h.day, observed: h.soh_observed, true: h.soh_true }));
    const proj = detail.projection.map((p) => ({ x: p.day, predicted: p.soh_predicted }));
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
      </div>""")

# Wait, the meta soh_avg was multiplied by 100 above. Let's fix the SoH display for individual assets too.
code = code.replace("""{ASSETS.map((a) => (""", """{fleetData.assets.map((a) => (""")
code = code.replace("""SoH {a.soh}%""", """SoH {Math.round(a.soh * 100)}%""")
code = code.replace("""fit: { score: Math.round(a.soh), label: a.soh_band }""", """fit: { score: Math.round(a.soh * 100), label: a.soh_band }""")
code = code.replace("""<StatusPill tone={BAND_TONE[a.soh_band]}>{a.soh_band}</StatusPill>""", """<StatusPill tone={BAND_TONE[a.soh_band]}>{a.soh_band}</StatusPill>""")
# `a.soh_band` doesn't need *100, but wait `BAND_TONE` has "Healthy". The backend uses "healthy", "watch", "critical". So I need to fix BAND_TONE.
code = code.replace("""const BAND_TONE: Record<SoHBand, "healthy" | "watch" | "critical"> = {
  Healthy: "healthy",
  Watch: "watch",
  Critical: "critical",
};""", """const BAND_TONE: Record<SoHBand, "healthy" | "watch" | "critical"> = {
  healthy: "healthy",
  aging: "watch",
  end_of_life: "critical",
};""")

code = code.replace("""                  <div className="mt-1 text-[24px] font-semibold">{detail.fade_breakdown.cycle_loss_pct}%</div>
                </div>
                <div className="flex-1">
                  <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Calendar loss</div>
                  <div className="mt-1 text-[24px] font-semibold">{detail.fade_breakdown.calendar_loss_pct}%</div>
                </div>
              </div>
              <div className="mt-3 flex h-2 overflow-hidden rounded-full">
                <div style={{ width: `${detail.fade_breakdown.cycle_loss_pct}%`, background: "#5b5fed" }} />
                <div style={{ width: `${detail.fade_breakdown.calendar_loss_pct}%`, background: "#3e8ef7" }} />
              </div>""", """                  <div className="mt-1 text-[24px] font-semibold">{Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%</div>
                </div>
                <div className="flex-1">
                  <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Calendar loss</div>
                  <div className="mt-1 text-[24px] font-semibold">{100 - Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%</div>
                </div>
              </div>
              <div className="mt-3 flex h-2 overflow-hidden rounded-full">
                <div style={{ width: `${Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%`, background: "#5b5fed" }} />
                <div style={{ width: `${100 - Math.round((detail.fade_breakdown.cycle_share ?? 0) * 100)}%`, background: "#3e8ef7" }} />
              </div>""")

code = code.replace("""        <div className="mb-4 flex items-end justify-between">
          <div className="text-[16px] font-semibold">Maintenance work-order queue</div>
          <div className="flex gap-4 text-[11px] text-[color:var(--color-text-secondary)]">
            <span>Scheduled {MAINT_META.scheduled_count}</span>
            <span>Overdue {MAINT_META.overdue_count}</span>
            <span>Bays {MAINT_META.bay_capacity}</span>
            <span>Parts LT {MAINT_META.parts_lead_time_days}d</span>
            <span>Queue clear day {MAINT_META.queue_clear_day}</span>
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
            {WORK_ORDERS.map((w) => (
              <tr key={w.asset_id + w.action} className="border-t border-white/5">
                <td className="py-2">{w.asset_id}</td>
                <td className="py-2">{w.action}</td>
                <td className="py-2 text-right tabular-nums">{w.start_day}</td>
                <td className="py-2 text-right tabular-nums">{w.complete_day}</td>
                <td className="py-2">
                  <StatusPill tone={w.priority === "High" ? "critical" : w.priority === "Medium" ? "watch" : "healthy"}>{w.priority}</StatusPill>
                </td>
                <td className="py-2">
                  {w.overdue ? <StatusPill tone="critical">Overdue</StatusPill> : <StatusPill tone="healthy">On plan</StatusPill>}
                </td>
              </tr>
            ))}""", """        <div className="mb-4 flex items-end justify-between">
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
            ))}""")

# ElectrifyTab chunk
code = code.replace("""function ElectrifyTab() {
  const inr = (n: number) => `₹${(n / 10_000_000).toFixed(1)} Cr`;
  return (
    <AgentSection>
      <SectionTitle eyebrow="Procurement" title="Electrification candidates" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Electrify Now" value={ELEC_META.electrify_now} status={{ tone: "healthy", label: "Ready" }} />
        <StatCard label="Pilot" value={ELEC_META.pilot} status={{ tone: "watch", label: "Test" }} />
        <StatCard label="Defer" value={ELEC_META.defer} status={{ tone: "critical", label: "Hold" }} />
        <StatCard label="Avg Readiness" value={ELEC_META.avg_readiness} decimals={2} />
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Phase-1 Capex" value={ELEC_META.phase1_capex_inr / 10_000_000} decimals={1} prefix="₹" suffix=" Cr" />
        <StatCard label="Phase-1 Max Lead" value={ELEC_META.phase1_max_lead_weeks} suffix=" wks" />
        <StatCard label="Fleet Annual Saving" value={ELEC_META.fleet_annual_saving_inr / 10_000_000} decimals={1} prefix="₹" suffix=" Cr" status={{ tone: "healthy", label: "Saving" }} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        {ELEC_CANDIDATES.map((c) => (""", """const ACTION_TONE_FIX: Record<string, "healthy" | "watch" | "critical"> = {
  "Electrify now": "healthy",
  "Pilot deployment": "watch",
  "Defer / monitor": "critical",
};
function ElectrifyTab() {
  const [elecData, setElecData] = useState<ElectrificationResponse | null>(null);
  useEffect(() => {
    fetchElectrification().then(setElecData);
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
        {elecData.candidates.map((c) => (""")

code = code.replace("""<div className="text-[16px] font-semibold">{c.vehicle_name}</div>
                <div className="mt-0.5 text-[12px] text-[color:var(--color-text-secondary)]">
                  {c.vehicle_class} · {c.region} · {c.current_powertrain}
                </div>
              </div>
              <StatusPill tone={ACTION_TONE[c.action]}>{c.action}</StatusPill>""", """<div className="text-[16px] font-semibold">{c.name}</div>
                <div className="mt-0.5 text-[12px] text-[color:var(--color-text-secondary)]">
                  {c.vehicle_class} · {c.region} · {c.powertrain}
                </div>
              </div>
              <StatusPill tone={ACTION_TONE_FIX[c.action]}>{c.action}</StatusPill>""")

code = code.replace("""<div className="mt-1 text-[13px] font-medium">{c.ev_replacement.model} · {c.ev_replacement.oem}</div>
              <div className="mt-1 grid grid-cols-4 gap-2 text-[11px] text-[color:var(--color-text-secondary)]">
                <span>Range {c.ev_replacement.range_km} km</span>
                <span>Payload {c.ev_replacement.payload_kg} kg</span>
                <span>{inr(c.ev_replacement.price_inr)}</span>
                <span>LT {c.ev_replacement.lead_time_weeks} wk · {c.ev_replacement.fast_charge_kw} kW</span>
              </div>""", """<div className="mt-1 text-[13px] font-medium">{c.recommended_ev.model} · {c.recommended_ev.oem}</div>
              <div className="mt-1 grid grid-cols-4 gap-2 text-[11px] text-[color:var(--color-text-secondary)]">
                <span>Range {c.recommended_ev.range_km} km</span>
                <span>Payload {c.recommended_ev.payload_kg} kg</span>
                <span>{inr(c.recommended_ev.price_inr)}</span>
                <span>LT {c.recommended_ev.lead_weeks} wk · {c.recommended_ev.fast_charge ? "Fast Charge" : "Slow Charge"}</span>
              </div>""")

code = code.replace("""<div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">EV ₹/km</div>
                <div className="mt-1 font-semibold tabular-nums">{c.economics.cost_per_km_ev.toFixed(1)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">Fuel ₹/km</div>
                <div className="mt-1 font-semibold tabular-nums">{c.economics.cost_per_km_fuel.toFixed(1)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">Saving/km</div>
                <div className="mt-1 font-semibold tabular-nums" style={{ color: "#34d399" }}>+{c.economics.saving_per_km.toFixed(1)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
                <div className="text-[color:var(--color-text-secondary)]">Payback</div>
                <div className="mt-1 font-semibold tabular-nums">{c.economics.payback_years.toFixed(1)} yr</div>
              </div>""", """<div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-2">
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
              </div>""")

# ValidationTab Chunk
code = code.replace("""function ValidationTab() {
  const [cellIdx, setCellIdx] = useState(0);
  const cell = NASA_CELLS[cellIdx];
  return (
    <AgentSection>
      <SectionTitle eyebrow="Validation" title="NASA battery aging dataset" />
      <p className="text-[13px] text-[color:var(--color-text-secondary)]">Source · {VALIDATION.source}</p>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Mean RMSE" value={VALIDATION.model_adequacy.mean_rmse_pct} suffix="%" decimals={2} status={{ tone: "healthy", label: "Strong" }} />
        <StatCard label="Max RMSE" value={VALIDATION.model_adequacy.max_rmse_pct} suffix="%" decimals={2} />
        <StatCard label="Mean SoH MAE" value={VALIDATION.knee_onset_forecast.mean_soh_mae_pct} suffix="%" decimals={2} />
        <StatCard label="Max SoH MAE" value={VALIDATION.knee_onset_forecast.max_soh_mae_pct} suffix="%" decimals={2} />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard label="Median RUL abs err" value={VALIDATION.knee_onset_forecast.median_rul_abs_err_cycles} suffix=" cycles" />
        <StatCard label="Mean RUL abs err" value={VALIDATION.knee_onset_forecast.mean_rul_abs_err_cycles} decimals={1} suffix=" cycles" />
      </div>

      <GlassCard padding="md">
        <div className="mb-3 text-[16px] font-semibold">Per-cell knee-onset accuracy</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={VALIDATION.knee_onset_forecast.per_cell} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>""", """function ValidationTab() {
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
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>""")

code = code.replace("""{NASA_CELLS.map((c, i) => (""", """{valCells.cells.map((c, i) => (""")
code = code.replace("""<Metric label="Ambient" value={`${cell.ambient_temp_c} °C`} />""", """<Metric label="Ambient" value={`${cell.ambient_c} °C`} />""")
code = code.replace("""<Metric label="Cycles" value={`${cell.cycle_count}`} />""", """<Metric label="Cycles" value={`${cell.cycles}`} />""")
code = code.replace("""<Line type="monotone" dataKey="soh" name="SoH %" stroke="#5b5fed" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="capacity" name="Capacity Ah" stroke="#34d399" strokeWidth={2} dot={false} />""", """<Line type="monotone" dataKey="soh_observed" name="SoH %" stroke="#5b5fed" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="capacity_ah" name="Capacity Ah" stroke="#34d399" strokeWidth={2} dot={false} />""")
# Note: we should change x-axis to be `cycle` rather than `day`, but `fleet.ts` cell series has `day` and `efc`. I'll use `efc` instead of cycle.
code = code.replace("""<XAxis dataKey="cycle" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />""", """<XAxis dataKey="efc" stroke="#5c5c68" tick={{ fill: "#9a9aa8", fontSize: 11 }} axisLine={false} tickLine={false} />""")

with open("platform-new/src/routes/fleetmind.tsx", "w") as f:
    f.write(code)

