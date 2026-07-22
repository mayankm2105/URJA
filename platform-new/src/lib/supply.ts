export type RiskBand = "low" | "medium" | "high";

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  tier?: number | null;
  country?: string | null;
  country_shares?: Record<string, number> | null;
  risk: number;
  risk_band: RiskBand;
  baseline_risk?: number | null;
  lead_time_days?: number | null;
  risk_breakdown?: Record<string, number>;
  x?: number;
  y?: number;
  hot?: boolean;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  dependency: number;
  buffer_days: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  meta: Record<string, number>;
}

export interface EventSource {
  name: string;
  url?: string | null;
}

export interface SignalEvent {
  id: string;
  date: string;
  headline: string;
  body?: string | null;
  source: EventSource;
  event_type: string;
  severity: number;
  direction: string;
  materials: string[];
  countries: string[];
  suppliers: string[];
}

export interface Alert {
  product_id: string;
  product_label: string;
  scenario_risk: number;
  baseline_risk: number;
  delta: number;
  risk_band: RiskBand;
  lead_time_days?: number | null;
  path_labels: string[];
  via_label?: string | null;
  triggering_event_ids: string[];
  triggering_headlines: string[];
  recommendations: string[];
  brief: string;
}

export interface ScenarioResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  alerts: Alert[];
  events_applied: string[];
  meta: Record<string, number | boolean>;
}

const API_BASE = import.meta.env?.VITE_SUPPLY_API ?? "http://localhost:8001/api";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed (${res.status})`);
  return res.json();
}

export async function fetchGraph(): Promise<GraphResponse> {
  const data = await getJSON<GraphResponse>("/graph");
  return data;
}

export async function fetchEvents(): Promise<SignalEvent[]> {
  return getJSON<SignalEvent[]>("/events");
}

export async function runScenario(eventIds: string[]): Promise<ScenarioResponse> {
  const res = await fetch(`${API_BASE}/scenario`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_ids: eventIds, generate_briefs: true }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`scenario failed (${res.status})`);
  const data = await res.json();
  return data;
}
