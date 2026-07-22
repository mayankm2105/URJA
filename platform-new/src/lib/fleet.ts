// Typed client for the FleetMind backend.

export type HealthBand = "healthy" | "aging" | "end_of_life";

export interface AssetSummary {
  id: string;
  name: string;
  vehicle_type: string;
  region: string;
  chemistry: string;
  soh: number; // 0-1
  soh_band: HealthBand;
  rul_days: number;
  rul_efc: number;
  efc_total: number;
  age_days: number;
  dominant_driver: string;
  horizon_capped: boolean;
}

export interface FleetResponse {
  assets: AssetSummary[];
  meta: {
    fleet_size: number;
    fleet_soh_avg: number;
    at_risk_count: number;
    end_of_life_count: number;
  };
}

export interface SohPoint {
  day: number;
  efc: number;
  soh_observed?: number | null;
  soh_true?: number | null;
  soh_predicted?: number | null;
}

export interface AssetDetail {
  summary: AssetSummary;
  fit: { a: number; n: number; rmse: number };
  fade_breakdown: {
    cycle_loss: number;
    calendar_loss: number;
    cycle_share: number | null;
  };
  history: SohPoint[];
  projection: SohPoint[];
  recommendations: string[];
  brief: string;
}

export interface WorkOrder {
  asset_id: string;
  name: string;
  region: string;
  chemistry: string;
  soh: number;
  rul_days: number;
  eol_day: number;
  action: string;
  recommended_start_day: number;
  service_days: number;
  completion_day: number;
  overdue: boolean;
  priority: number;
  driver: string;
}

export interface MaintenanceResponse {
  work_orders: WorkOrder[];
  meta: {
    fleet_size: number;
    scheduled: number;
    overdue: number;
    service_bays: number;
    parts_lead_days: number;
    service_days: number;
    queue_clears_day: number;
    reactive_first_action_day: number;
    predictive_first_warning_day: number;
  };
  plan: string;
}

const API_BASE =
  process.env.NEXT_PUBLIC_FLEET_API ?? "http://localhost:8002/api";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed (${res.status})`);
  return res.json();
}

export function fetchFleet(): Promise<FleetResponse> {
  return getJSON<FleetResponse>("/fleet");
}

export function fetchAsset(id: string, brief = false): Promise<AssetDetail> {
  return getJSON<AssetDetail>(`/asset/${id}${brief ? "?brief=true" : ""}`);
}

export function fetchMaintenance(partsLeadDays?: number): Promise<MaintenanceResponse> {
  const lead = partsLeadDays != null ? `&parts_lead_days=${partsLeadDays}` : "";
  return getJSON<MaintenanceResponse>(`/maintenance?plan=true${lead}`);
}

// ---- Real-data validation (NASA battery aging dataset) ----

export interface ValidationCellForecast {
  fit_window_cycles: number;
  cutoff_soh_pct: number;
  true_eol_cycle: number;
  rul_true_cycles: number;
  rul_pred_cycles: number;
  rul_abs_err_cycles: number;
}

export interface ValidationResponse {
  source: string;
  cells: number;
  model_adequacy: {
    mean_rmse_pct: number;
    max_rmse_pct: number;
    per_cell: {
      cell: string;
      a_sqrt: number;
      c_linear: number;
      in_sample_rmse_pct: number;
    }[];
  };
  knee_onset_forecast: {
    fit_window: string;
    soh_mae_pct_mean: number;
    soh_mae_pct_max: number;
    rul_median_abs_err_cycles: number;
    rul_mean_abs_err_cycles: number;
    per_cell: {
      cell: string;
      held_out_cycles: number;
      soh_mae_pct: number;
      rul: ValidationCellForecast | null;
    }[];
  };
}

export interface NasaCell {
  id: string;
  label: string;
  ambient_c: number;
  cycles: number;
  soh_start: number;
  soh_end: number;
  true_eol_cycle: number | null;
  series: { day: number; efc: number; capacity_ah: number; soh_observed: number }[];
}

export interface ValidationCellsResponse {
  cells: NasaCell[];
}

export function fetchValidation(): Promise<ValidationResponse> {
  return getJSON<ValidationResponse>("/validation");
}

export function fetchValidationCells(): Promise<ValidationCellsResponse> {
  return getJSON<ValidationCellsResponse>("/validation/cells");
}

// ---- Electrification readiness & procurement ----

export type ElecAction = "Electrify now" | "Pilot deployment" | "Defer / monitor";

export interface ElecSubscores {
  range: number;
  charging: number;
  payload: number;
  duty: number;
  tco: number;
}

export interface RecommendedEv {
  id: string;
  model: string;
  oem: string;
  chemistry: string; // NMC | LFP — couples procurement to supply-chain risk
  range_km: number;
  payload_kg: number;
  price_inr: number;
  lead_weeks: number;
  fast_charge: boolean;
}

export interface ElecCarbon {
  ice_tco2_yr: number;
  ev_tco2_yr: number;
  saving_tco2_yr: number;
}

export interface ElecEconomics {
  ev_cost_per_km: number;
  fuel_cost_per_km: number;
  saving_per_km: number;
  annual_saving_inr: number;
  payback_years: number | null;
}

export interface ElecAlternative {
  id: string;
  model: string;
  oem: string;
  chemistry: string;
  index: number;
  price_inr: number;
  lead_weeks: number;
}

export interface ReadinessEval {
  baseline: string;
  candidates_scored: number;
  verdict_agreement_pct: number;
  cohen_kappa: number;
  spearman_rho: number;
  rank_within_1: number;
  disagreement_count: number;
  disagreements: {
    id: string;
    name: string;
    engine_action: string;
    expert_action: string;
    engine_rank: number;
    expert_rank: number;
    expert_reason: string;
  }[];
  per_candidate: {
    id: string;
    name: string;
    engine_action: string;
    expert_action: string;
    agree: boolean;
    engine_rank: number;
    expert_rank: number;
    readiness_index: number;
    expert_reason: string;
  }[];
}

export function fetchReadinessEval(): Promise<ReadinessEval> {
  return getJSON<ReadinessEval>("/electrification/eval");
}

export interface ElecCandidate {
  range_feasible: boolean;
  feasibility_note: string | null;
  id: string;
  name: string;
  region: string;
  vehicle_class: string;
  powertrain: string;
  daily_km: number;
  payload_kg: number;
  dwell_hours: number;
  returns_to_depot: boolean;
  route_fixed: boolean;
  readiness_index: number;
  confidence: number;
  action: ElecAction;
  binding_constraint: string;
  subscores: ElecSubscores;
  recommended_ev: RecommendedEv;
  economics: ElecEconomics;
  carbon: ElecCarbon;
  alternatives: ElecAlternative[];
  brief?: string;
}

export interface ElectrificationResponse {
  candidates: ElecCandidate[];
  meta: {
    fleet_size: number;
    electrify_now: number;
    pilot: number;
    defer: number;
    avg_readiness: number;
    phase1_capex_inr: number;
    phase1_max_lead_weeks: number;
    fleet_annual_saving_inr: number;
    phase1_co2_saving_tons: number;
    fleet_co2_saving_tons: number;
  };
}

export function fetchElectrification(): Promise<ElectrificationResponse> {
  return getJSON<ElectrificationResponse>("/electrification");
}

export function fetchElecCandidate(
  id: string,
  brief = false,
): Promise<ElecCandidate> {
  return getJSON<ElecCandidate>(
    `/electrification/${id}${brief ? "?brief=true" : ""}`,
  );
}

// ---- Depot charging infrastructure (PS3 build-area #6) ----

export interface ChargingDepot {
  id: string;
  name: string;
  chargers: number;
  power_kw: number;
  uptime: number;
  window_h: number;
  nameplate_kwh: number;
  delivered_kwh: number;
  demand_kwh: number;
  headroom_kwh: number;
  utilisation_pct: number;
  lost_to_downtime_kwh: number;
  status: "ok" | "tight" | "short";
  n1_delivered_kwh: number;
  n1_survives: boolean;
  at_risk: string[];
}

export interface ChargingResponse {
  depots: ChargingDepot[];
  stranded: {
    asset_id: string;
    name: string;
    depot: string;
    kwh_needed: number;
    kwh_available: number;
  }[];
  meta: {
    depot_count: number;
    chargers_total: number;
    fleet_demand_kwh: number;
    delivered_kwh: number;
    nameplate_kwh: number;
    lost_to_downtime_kwh: number;
    avg_uptime_pct: number;
    depots_short: number;
    assets_at_risk: number;
    shortfall_kwh: number;
    worst_depot: string | null;
    no_redundancy: string[];
    uplift: {
      depot: string;
      from_uptime: number;
      to_uptime: number;
      kwh_regained: number;
      closes_gap: boolean;
    } | null;
  };
}

export function fetchCharging(): Promise<ChargingResponse> {
  return getJSON<ChargingResponse>("/charging");
}
