import type { FleetResponse, MaintenanceResponse } from "@/lib/api";

export type View = "fleet" | "electrification" | "validation";

export default function TopBar({
  fleet,
  maintenance,
  view,
  onViewChange,
}: {
  fleet: FleetResponse | null;
  maintenance: MaintenanceResponse | null;
  view: View;
  onViewChange: (v: View) => void;
}) {
  const m = fleet?.meta;
  const kpis = [
    {
      label: "Fleet Avg SoH",
      value: m ? `${(m.fleet_soh_avg * 100).toFixed(1)}%` : "—",
    },
    { label: "At Risk", value: m ? `${m.at_risk_count}` : "—" },
    { label: "End-of-Life", value: m ? `${m.end_of_life_count}` : "—" },
    {
      label: "Swaps Overdue",
      value: maintenance ? `${maintenance.meta.overdue}` : "—",
    },
  ];
  return (
    <header className="topbar">
      <div className="brand">
        <h1>
          Fleet<span className="dot">Mind</span>
        </h1>
        <span className="sub">EV Battery Asset Performance &amp; RUL Intelligence</span>
        <div className="view-toggle">
          <button
            className={view === "fleet" ? "active" : ""}
            onClick={() => onViewChange("fleet")}
          >
            Fleet
          </button>
          <button
            className={view === "electrification" ? "active" : ""}
            onClick={() => onViewChange("electrification")}
          >
            Electrify
          </button>
          <button
            className={view === "validation" ? "active" : ""}
            onClick={() => onViewChange("validation")}
          >
            Validation
          </button>
        </div>
      </div>
      <div className="kpis">
        {kpis.map((k) => (
          <div className="kpi" key={k.label}>
            <div className="label">{k.label}</div>
            <div className="value mono">{k.value}</div>
          </div>
        ))}
      </div>
    </header>
  );
}
