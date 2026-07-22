import type { AssetSummary } from "@/lib/api";
import { bandColor, bandLabel } from "@/lib/colors";

function rulText(a: AssetSummary): string {
  if (a.horizon_capped) return "RUL >10y";
  if (a.rul_days <= 0) return "RUL 0d";
  if (a.rul_days >= 365) return `RUL ${(a.rul_days / 365).toFixed(1)}y`;
  return `RUL ${a.rul_days.toFixed(0)}d`;
}

export default function FleetBoard({
  assets,
  selectedId,
  onSelect,
}: {
  assets: AssetSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="col">
      <div className="col-title">Fleet Health Board · worst-first</div>
      {assets.map((a) => {
        const color = bandColor(a.soh_band);
        const selected = a.id === selectedId;
        return (
          <div
            key={a.id}
            className={`asset-card ${a.soh_band === "end_of_life" ? "eol" : ""} ${
              selected ? "selected" : ""
            }`}
            onClick={() => onSelect(a.id)}
          >
            <div className="asset-head">
              <div>
                <div className="asset-id mono">{a.id}</div>
                <div className="asset-name">
                  {a.name} · {a.region}
                </div>
              </div>
              <div className="asset-soh mono" style={{ color }}>
                {(a.soh * 100).toFixed(1)}%
              </div>
            </div>
            <div className="sohbar">
              <span style={{ width: `${a.soh * 100}%`, background: color }} />
            </div>
            <div className="asset-meta">
              <span className="badge chem">{a.chemistry}</span>
              <span className="badge" style={{ color, border: `1px solid ${color}55` }}>
                {bandLabel(a.soh_band)}
              </span>
              <span className="mono" style={{ marginLeft: "auto" }}>
                {rulText(a)}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
