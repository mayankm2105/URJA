export interface Fleet {
  id: number;
  name: string;
}

// Typed client for the CarbonPulse (carbon_tracker) backend.

export interface CarbonDashboard {
  total_fleets: number;
  total_vehicles: number;
  ev_penetration_pct: number;
  scope1_ytd_tons: number;
  scope3_ytd_tons: number;
  ev_avoided_ytd_tons: number;
  net_zero_progress_pct: number;
  routes_electrified: number;
  total_routes: number;
}

export interface EmissionPoint {
  year: number;
  month: number;
  scope1_tons: number;
  scope3_tons: number;
  ev_avoided_tons: number;
  target_tons: number;
  label: string;
}

export interface Priority {
  rank: number;
  fleet_id: number;
  fleet_name: string;
  operator: string;
  asset_class: string;
  hub_city: string;
  ev_penetration_pct: number;
  annual_co2_tons: number;
  potential_saving_tons: number;
  readiness_index: number;
  impact_score: number;
  recommendation: string;
}

export interface Route {
  id: number;
  name: string;
  origin_city: string;
  dest_city: string;
  origin_lat: number;
  origin_lon: number;
  dest_lat: number;
  dest_lon: number;
  distance_km: number;
  monthly_co2_tons: number;
  potential_saving_tons: number;
  is_electrified: boolean;
}

export interface Commitment {
  id: number;
  organization: string;
  baseline_year: number;
  target_year: number;
  reduction_target_pct: number;
  current_reduction_pct: number;
  status: string;
}

export interface AssetClassEmissions {
  asset_class: string;
  fleet_count: number;
  scope1_tons: number;
  scope3_tons: number;
  ev_avoided_tons: number;
}

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatResponse {
  reply: string;
  intent: string;
  data_refs: string[];
}

const API_BASE =
  process.env.NEXT_PUBLIC_CARBON_API ?? "http://localhost:8003/api";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed (${res.status})`);
  return res.json();
}

async function postJSON<T>(path: string, body: any): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed (${res.status})`);
  return res.json();
}

export function fetchCarbonDashboard(): Promise<CarbonDashboard> {
  return getJSON<CarbonDashboard>("/dashboard");
}

export function fetchEmissions(fleetId?: number | string): Promise<EmissionPoint[]> {
  const q = fleetId && fleetId !== 'all' ? `?fleet_id=${fleetId}` : '';
  return getJSON<EmissionPoint[]>(`/emissions/timeseries${q}`);
}

export function fetchFleets(): Promise<Fleet[]> {
  return getJSON<Fleet[]>("/fleet");
}

export function fetchCommitments(): Promise<Commitment[]> {
  return getJSON<Commitment[]>("/commitments");
}

export function fetchAssetClassEmissions(): Promise<AssetClassEmissions[]> {
  return getJSON<AssetClassEmissions[]>("/emissions/by-asset-class");
}

export function fetchRoutes(): Promise<Route[]> {
  return getJSON<Route[]>("/routes");
}

export function fetchPriorities(): Promise<Priority[]> {
  return getJSON<Priority[]>("/ai/priorities");
}

export function fetchAssistantReply(message: string, history: ChatMessage[] = []): Promise<ChatResponse> {
  return postJSON<ChatResponse>("/ai/chat", { message, history });
}

// ---- Carbon accuracy vs metered fuel (PS3 metric #5) ----

export interface CarbonValidation {
  source: string;
  measured_quantity: string;
  routes_validated: number;
  mape_pct: number;
  median_pct_err: number;
  worst_pct_err: number;
  within_15_pct: number;
  fleet_total_estimated_tco2: number;
  fleet_total_measured_tco2: number;
  fleet_total_pct_err: number;
  per_route: {
    route: string;
    km_run: number;
    payload_tons: number;
    estimated_tco2: number;
    measured_tco2: number;
    pct_err: number;
    over: boolean;
  }[];
}

export function fetchCarbonValidation(): Promise<CarbonValidation> {
  return getJSON<CarbonValidation>("/carbon/validation");
}
