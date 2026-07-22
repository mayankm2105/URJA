import type { HealthBand } from "./api";

// Health palette — shared with the Stitch design tokens and the CellSentry suite.
export const BAND_COLOR: Record<HealthBand, string> = {
  healthy: "#10b981",
  aging: "#ee9800",
  end_of_life: "#ff5d52",
};

export const HOT = "#ff5d52";
export const CYCLE_COLOR = "#3b82f6";
export const CALENDAR_COLOR = "#8b5cf6";

export function bandColor(band: string): string {
  return BAND_COLOR[band as HealthBand] ?? "#64748b";
}

export function bandLabel(band: string): string {
  return (
    { healthy: "HEALTHY", aging: "AGING", end_of_life: "END-OF-LIFE" }[band] ??
    band.toUpperCase()
  );
}
