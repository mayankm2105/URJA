"use client";

import type { Alert } from "@/lib/api";

export default function AlertPanel({
  alerts,
  hasScenario,
  loading,
}: {
  alerts: Alert[];
  hasScenario: boolean;
  loading: boolean;
}) {
  return (
    <aside className="panel panel-right">
      <div className="panel-head">
        <h2>Active Alerts</h2>
        <span className="count">{alerts.length}</span>
      </div>

      {loading && <div className="muted small">Running scenario…</div>}

      {!loading && !hasScenario && (
        <div className="empty">
          Select a disruption signal on the left to model its impact across the
          supply chain — affected products, lead time before impact, and
          recommended actions appear here.
        </div>
      )}

      {!loading && hasScenario && alerts.length === 0 && (
        <div className="empty">No products materially affected by this signal.</div>
      )}

      {!loading &&
        alerts.map((a) => (
          <div key={a.product_id} className="alert">
            <div className="alert-head">
              <span className="alert-product">{a.product_label}</span>
              <span className={`badge badge-${a.risk_band}`}>{a.risk_band.toUpperCase()}</span>
            </div>

            <div className="alert-metrics">
              <div className="metric">
                <div className="metric-label">Risk score</div>
                <div className="risk-row">
                  <span className="risk-base">{Math.round(a.baseline_risk)}</span>
                  <span className="arrow">→</span>
                  <span className="risk-now">{Math.round(a.scenario_risk)}</span>
                </div>
              </div>
              <div className="metric leadtime">
                <div className="metric-label">Lead time to impact</div>
                <div className="leadtime-val">
                  {a.lead_time_days != null ? `~${Math.round(a.lead_time_days)}d` : "—"}
                </div>
              </div>
            </div>

            {a.path_labels.length > 0 && (
              <div className="alert-path">{a.path_labels.join("  →  ")}</div>
            )}
            {a.brief && <div className="alert-brief">{a.brief}</div>}

            {a.recommendations.length > 0 && (
              <div className="recs">
                <div className="recs-title">Recommended actions</div>
                <ul>
                  {a.recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
    </aside>
  );
}
