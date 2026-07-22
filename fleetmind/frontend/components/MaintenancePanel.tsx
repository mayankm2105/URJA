import type { AssetDetail, MaintenanceResponse } from "@/lib/api";

export default function MaintenancePanel({
  detail,
  maintenance,
  onSelect,
}: {
  detail: AssetDetail | null;
  maintenance: MaintenanceResponse | null;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="pane">
      <div className="col-title">Asset Health Brief</div>
      <div className="panel">
        {detail ? (
          <>
            <div className="brief-text">{detail.brief || briefFallback(detail)}</div>
            {detail.recommendations.length > 0 && (
              <ul className="recs">
                {detail.recommendations.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <div className="brief-text" style={{ color: "var(--text-faint)" }}>
            Select an asset to see its health brief.
          </div>
        )}
      </div>

      <div className="col-title" style={{ marginTop: 18 }}>
        Predictive Maintenance Queue
      </div>
      <div className="panel">
        {maintenance ? (
          <>
            <table className="queue">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Asset</th>
                  <th>SoH</th>
                  <th>Start</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {maintenance.work_orders.map((w) => (
                  <tr
                    key={w.asset_id}
                    style={{ cursor: "pointer" }}
                    onClick={() => onSelect(w.asset_id)}
                  >
                    <td className="mono">{w.priority}</td>
                    <td className="mono">{w.asset_id}</td>
                    <td className="mono">{(w.soh * 100).toFixed(0)}%</td>
                    <td className="mono">d{w.recommended_start_day}</td>
                    <td>
                      <span className={`tag ${w.overdue ? "overdue" : "ontime"}`}>
                        {w.overdue ? "OVERDUE" : "on-time"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {maintenance.plan && <div className="plan-note">{maintenance.plan}</div>}
          </>
        ) : (
          <div className="brief-text" style={{ color: "var(--text-faint)" }}>
            Loading queue…
          </div>
        )}
      </div>
    </div>
  );
}

function briefFallback(d: AssetDetail): string {
  return `${d.summary.name} is at ${(d.summary.soh * 100).toFixed(
    1
  )}% State-of-Health. Set ANTHROPIC_API_KEY on the backend for an AI-written brief.`;
}
