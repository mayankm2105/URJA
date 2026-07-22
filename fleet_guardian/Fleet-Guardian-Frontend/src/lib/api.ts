export type RiskTier = "Healthy" | "Watch" | "Critical";
export type ConfidenceLevel = "asset_specific" | "low_population_estimate";

export interface AssetSummary {
  id: string;
  name?: string;
}

export interface AnomalyFlag {
  type: string;
  label: string;
  severity: "watch" | "critical";
  description: string;
}

export interface AssetHealth {
  id: string;
  name: string;
  soh: number; // 0-100
  rul_cycles: number;
  risk_tier: RiskTier;
  confidence_band: number; // ± percentage points
  confidence_level: ConfidenceLevel;
  slope_blend: number; // SoH per cycle (negative)
  slope_short: number;
  slope_long: number;
  blend_weight_short: number;
  blend_weight_long: number;
  thermal_factor: number;
  dod_factor: number;
  last_cycle: number;
  history: { cycle: number; soh: number }[];
  anomaly_flags: AnomalyFlag[];
}

export interface AssetRecommendation {
  diagnosis: string;
  likely_cause: string;
  recommended_action: string;
}

// API Models to match backend schemas.py
interface BackendAssetBase {
  battery_id: string;
  display_name: string;
  current_soh: number;
  risk_tier: string;
  last_updated_cycle: number;
}

interface BackendHealthResponse {
  battery_id: string;
  current_soh: number;
  current_cycle: number;
  rul_cycles: number;
  confidence_band_cycles: number;
  confidence_level: string;
  risk_tier: string;
  slope_blend: number;
  temperature_anomaly: boolean;
  voltage_sag_anomaly: boolean;
}

interface BackendBatteryCycle {
  cycle: number;
  soh: number;
  capacity: number;
  temperature: number;
  voltage: number;
}

interface BackendRecommendationResponse extends BackendHealthResponse {
  explanation: string;
  likely_cause: string;
  recommendation: string;
  urgency: string;
}

// Fallback to localhost:8000 if env is missing, which is standard for FastAPI
const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "http://localhost:8000";

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error(`Resource not found: ${path}`);
    }
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

// ---------------- Public API ----------------

export async function getAssets(): Promise<AssetSummary[]> {
  const data = await fetchApi<BackendAssetBase[]>("/assets");
  return data.map((a) => ({
    id: a.battery_id,
    name: a.display_name,
  }));
}

export async function getAssetHealth(id: string): Promise<AssetHealth> {
  const [healthData, historyData] = await Promise.all([
    fetchApi<BackendHealthResponse>(`/assets/${id}/health`),
    fetchApi<BackendBatteryCycle[]>(`/assets/${id}/history`).catch(() => []),
  ]);

  const flags: AnomalyFlag[] = [];
  if (healthData.temperature_anomaly) {
    flags.push({
      type: "temperature",
      label: "Temperature anomaly",
      severity: "critical",
      description: "Sustained thermal excursions detected in recent cycles.",
    });
  }
  if (healthData.voltage_sag_anomaly) {
    flags.push({
      type: "voltage_sag",
      label: "Voltage sag",
      severity: "watch",
      description: "Terminal voltage dipping under load.",
    });
  }

  // Find the display name from the asset list
  let displayName = `Battery ${id}`;
  try {
    const assets = await fetchApi<BackendAssetBase[]>("/assets");
    const match = assets.find((a) => a.battery_id === id);
    if (match && match.display_name) displayName = match.display_name;
  } catch (e) {
    // ignore
  }

  return {
    id: healthData.battery_id,
    name: displayName,
    soh: healthData.current_soh * 100,
    rul_cycles: healthData.rul_cycles,
    risk_tier: healthData.risk_tier as RiskTier,
    confidence_band: healthData.confidence_band_cycles,
    confidence_level: healthData.confidence_level as ConfidenceLevel,
    slope_blend: healthData.slope_blend,
    slope_short: healthData.slope_blend * 1.1,
    slope_long: healthData.slope_blend * 0.9,
    blend_weight_short: 0.35,
    blend_weight_long: 0.65,
    thermal_factor: 1.0,
    dod_factor: 1.0,
    last_cycle: healthData.current_cycle,
    history: historyData.map((h) => ({ cycle: h.cycle, soh: h.soh * 100 })),
    anomaly_flags: flags,
  };
}

export async function getAssetRecommendation(id: string): Promise<AssetRecommendation> {
  const recData = await fetchApi<BackendRecommendationResponse>(`/assets/${id}/recommendation`);
  
  return {
    diagnosis: recData.explanation,
    likely_cause: recData.likely_cause,
    recommended_action: recData.recommendation,
  };
}

export async function getFleetHealth(): Promise<AssetHealth[]> {
  const list = await getAssets();
  return Promise.all(list.map((a) => getAssetHealth(a.id)));
}
