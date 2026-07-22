// Mock data mirroring the shape the four backend agents (ports 8001-8004) return.
// Swap these functions for real fetch() calls once the APIs are wired.

export type Severity = "healthy" | "watch" | "critical";

export const PLATFORM_STATS = {
  assetsMonitored: 1284,
  fleetAvgSoH: 87.4,
  tonnesCO2Tracked: 42813,
  supplyChainNodes: 30,
  needsAttention: 37,
};

export function makeSeries(len: number, base: number, amp: number, drift = 0) {
  return Array.from({ length: len }, (_, i) => ({
    x: `${i + 1}`,
    y: +(base + Math.sin(i / 2) * amp + i * drift + (Math.random() - 0.5) * amp * 0.3).toFixed(2),
  }));
}

export const NEWS_EVENTS = [
  {
    id: "n1",
    title: "Cobalt export tariff raised in DRC",
    date: "Jul 14, 2026",
    severity: "critical" as Severity,
    impact: "Battery cell cost +4.2%",
  },
  {
    id: "n2",
    title: "New lithium refinery online in Chile",
    date: "Jul 12, 2026",
    severity: "healthy" as Severity,
    impact: "Supply diversification +12%",
  },
  {
    id: "n3",
    title: "Rail strike affecting graphite shipments",
    date: "Jul 10, 2026",
    severity: "watch" as Severity,
    impact: "Lead time +9 days",
  },
  {
    id: "n4",
    title: "Nickel spot price down 3.1%",
    date: "Jul 08, 2026",
    severity: "healthy" as Severity,
    impact: "Cell BOM −1.8%",
  },
  {
    id: "n5",
    title: "Geopolitical tension: Indonesia export policy",
    date: "Jul 06, 2026",
    severity: "watch" as Severity,
    impact: "HHI concentration risk ↑",
  },
];

export const ACTIONS = [
  {
    id: "a1",
    title: "Battery #B-2041 approaching end of life",
    desc: "RUL forecast 42 cycles · confidence 91%. Schedule replacement.",
    tone: "critical" as Severity,
    source: "GUARDIAN",
  },
  {
    id: "a2",
    title: "Cobalt supplier concentration exceeds HHI threshold",
    desc: "2 of 3 tier-1 suppliers in single region. Diversify sourcing.",
    tone: "critical" as Severity,
    source: "SUPPLY",
  },
  {
    id: "a3",
    title: "SBTi Scope-1 target trending 8% off pace",
    desc: "Accelerate diesel→electric transition on Route Cluster 4.",
    tone: "watch" as Severity,
    source: "NET ZERO",
  },
  {
    id: "a4",
    title: "14 diesel vehicles eligible for immediate EV swap",
    desc: "OEM lead time 6 weeks. Combined ROI 2.3 years.",
    tone: "watch" as Severity,
    source: "ELECTRIFY",
  },
  {
    id: "a5",
    title: "Depot 3 charge scheduling exceeds capacity 18–22h",
    desc: "Shift 6 vehicles to overnight window or add 400kW port.",
    tone: "watch" as Severity,
    source: "GUARDIAN",
  },
  {
    id: "a6",
    title: "Incoming cell batch #C-8814 flagged for QA",
    desc: "Voltage deviation on 3.2% of samples in cycle-test.",
    tone: "healthy" as Severity,
    source: "SUPPLY",
  },
];

export function makeHeat(n: number) {
  return Array.from({ length: n }, () => {
    const r = Math.random();
    const tone: Severity = r > 0.85 ? "critical" : r > 0.6 ? "watch" : "healthy";
    return { tone, intensity: 0.4 + Math.random() * 0.6 };
  });
}
