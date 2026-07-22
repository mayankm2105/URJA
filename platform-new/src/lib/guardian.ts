// Typed client for the Fleet Guardian (EV APM) backend.

export interface GuardianAsset {
  battery_id: string;
  display_name: string;
  current_soh: number; // percent (0-100)
  risk_tier: string; // Healthy | Watch | Critical
  last_updated_cycle: number;
}

export interface GuardianHealth {
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

export interface GuardianRecommendation extends GuardianHealth {
  explanation: string;
  likely_cause: string;
  recommendation: string;
  urgency: string;
}

export interface GuardianCycle {
  cycle: number;
  soh: number;
  capacity: number;
  temperature: number;
  voltage: number;
}

export interface GuardianSummary {
  total_assets: number;
  healthy_count: number;
  watch_count: number;
  critical_count: number;
  average_soh: number;
}

const API_BASE =
  process.env.NEXT_PUBLIC_GUARDIAN_API ?? "http://localhost:8004";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed (${res.status})`);
  return res.json();
}

export function fetchGuardianSummary(): Promise<GuardianSummary> {
  return getJSON<GuardianSummary>("/fleet/summary");
}

export function fetchGuardianAssets(): Promise<GuardianAsset[]> {
  return getJSON<GuardianAsset[]>("/assets");
}

export function fetchGuardianHealth(id: string): Promise<GuardianHealth> {
  return getJSON<GuardianHealth>(`/assets/${id}/health`);
}

export function fetchGuardianHistory(id: string): Promise<GuardianCycle[]> {
  return getJSON<GuardianCycle[]>(`/assets/${id}/history`);
}

export async function fetchGuardianRecommendation(
  id: string
): Promise<GuardianRecommendation | null> {
  // The recommendation endpoint needs a Groq key server-side; degrade quietly.
  try {
    return await getJSON<GuardianRecommendation>(`/assets/${id}/recommendation`);
  } catch {
    return null;
  }
}

// Risk tiers map onto the shared platform bands.
export function tierBand(tier: string): "healthy" | "aging" | "end_of_life" {
  const t = tier.toLowerCase();
  if (t.includes("critical")) return "end_of_life";
  if (t.includes("watch")) return "aging";
  return "healthy";
}
