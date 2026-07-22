import { fetchGuardianAssets } from "./guardian";
import { fetchEvents } from "./supply";
import { fetchCommitments } from "./carbon";
import { fetchMaintenance } from "./fleet";

export interface ActionItem {
  id: string;
  source: "GUARDIAN" | "SUPPLY" | "NET ZERO" | "ELECTRIFY";
  tone: "critical" | "watch" | "healthy" | "neutral";
  title: string;
  desc: string;
  link: string;
}

export async function fetchAllActions(): Promise<ActionItem[]> {
  const [guardian, supply, carbon, fleet] = await Promise.allSettled([
    fetchGuardianActions(),
    fetchSupplyActions(),
    fetchCarbonActions(),
    fetchFleetActions(),
  ]);

  const actions: ActionItem[] = [];
  if (guardian.status === "fulfilled") actions.push(...guardian.value);
  if (supply.status === "fulfilled") actions.push(...supply.value);
  if (carbon.status === "fulfilled") actions.push(...carbon.value);
  if (fleet.status === "fulfilled") actions.push(...fleet.value);

  const toneScore = { critical: 3, watch: 2, healthy: 1, neutral: 0 };
  actions.sort((a, b) => toneScore[b.tone] - toneScore[a.tone]);

  return actions;
}

async function fetchGuardianActions(): Promise<ActionItem[]> {
  try {
    const assets = await fetchGuardianAssets();
    return assets
      .filter((a) => a.risk_tier.toLowerCase() === "critical")
      .map((a) => ({
        id: `guardian-${a.battery_id}`,
        source: "GUARDIAN",
        tone: "critical",
        title: `Critical Battery: ${a.display_name}`,
        desc: "Asset requires immediate attention due to critical health status.",
        link: `/fleet-guardian?batteryId=${a.battery_id}`,
      }));
  } catch (e) {
    console.error("fetchGuardianActions failed", e);
    return [];
  }
}

async function fetchSupplyActions(): Promise<ActionItem[]> {
  try {
    const events = await fetchEvents();
    return events
      .filter((e) => e.severity >= 80)
      .map((e) => ({
        id: `supply-${e.id}`,
        source: "SUPPLY",
        tone: "critical",
        title: `Supply Chain Alert: ${e.headline}`,
        desc: `Impacts: ${e.materials.join(", ")}`,
        link: `/cellsentry?eventId=${e.id}`,
      }));
  } catch (e) {
    console.error("fetchSupplyActions failed", e);
    return [];
  }
}

async function fetchCarbonActions(): Promise<ActionItem[]> {
  try {
    const commitments = await fetchCommitments();
    return commitments
      .filter((c) => c.status !== "On Track")
      .map((c) => ({
        id: `carbon-${c.organization}`,
        source: "NET ZERO",
        tone: "critical",
        title: `At-Risk Commitment: ${c.organization}`,
        desc: `Target: ${c.reduction_target_pct}% reduction by ${c.target_year}`,
        link: `/carbonpulse?tab=report`,
      }));
  } catch (e) {
    console.error("fetchCarbonActions failed", e);
    return [];
  }
}

async function fetchFleetActions(): Promise<ActionItem[]> {
  try {
    const maintenance = await fetchMaintenance();
    return maintenance.work_orders
      .filter((w) => w.overdue)
      .map((w) => ({
        id: `fleet-${w.asset_id}-${w.action}`,
        source: "ELECTRIFY",
        tone: "critical",
        title: `Overdue Work Order: ${w.name}`,
        desc: `Action: ${w.action}`,
        link: `/fleetmind?assetId=${w.asset_id}`,
      }));
  } catch (e) {
    console.error("fetchFleetActions failed", e);
    return [];
  }
}
