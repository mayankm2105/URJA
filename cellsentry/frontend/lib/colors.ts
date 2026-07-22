import type { RiskBand } from "./api";

// Risk palette (matches the Stitch design tokens).
export const RISK_COLOR: Record<RiskBand, string> = {
  low: "#10b981",
  medium: "#ee9800",
  high: "#ff5d52",
};

export const HOT = "#ff5d52";

export function bandColor(band: string): string {
  return RISK_COLOR[band as RiskBand] ?? "#64748b";
}

export function severityBand(severity: number): RiskBand {
  if (severity >= 60) return "high";
  if (severity >= 35) return "medium";
  return "low";
}
