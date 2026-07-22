import type { AssetDetail as Detail } from "@/lib/api";
import { bandColor, bandLabel, CALENDAR_COLOR, CYCLE_COLOR } from "@/lib/colors";
import SohChart from "./SohChart";

function rulBig(d: Detail): string {
  const a = d.summary;
  if (a.horizon_capped) return ">10 years";
  if (a.rul_days <= 0) return "0 days";
  if (a.rul_days >= 365) return `${(a.rul_days / 365).toFixed(1)} years`;
  return `${a.rul_days.toFixed(0)} days`;
}

export default function AssetDetail({ detail }: { detail: Detail }) {
  const a = detail.summary;
  const color = bandColor(a.soh_band);
  const share = detail.fade_breakdown.cycle_share;
  const cyclePct = share != null ? Math.round(share * 100) : null;
  const calPct = cyclePct != null ? 100 - cyclePct : null;

  return (
    <div className="pane">
      <div className="detail-head">
        <div>
          <h2>{a.name}</h2>
          <div className="asset-name mono">
            {a.id} · {a.vehicle_type} · {a.chemistry} · {a.region}
          </div>
        </div>
        <span
          className="status-pill"
          style={{ background: `${color}22`, color, border: `1px solid ${color}66` }}
        >
          {bandLabel(a.soh_band)}
        </span>
      </div>

      <div className="panel">
        <h3>State-of-Health Trajectory</h3>
        <SohChart detail={detail} />
      </div>

      <div className="tiles">
        <div className="tile">
          <div className="label">Current SoH</div>
          <div className="big mono" style={{ color }}>
            {(a.soh * 100).toFixed(1)}%
          </div>
        </div>
        <div className="tile">
          <div className="label">Remaining Useful Life</div>
          <div className="big mono">{rulBig(detail)}</div>
        </div>
        <div className="tile">
          <div className="label">Equivalent Full Cycles</div>
          <div className="small mono">{a.efc_total.toLocaleString()} EFC</div>
        </div>
        <div className="tile">
          <div className="label">Dominant Fade Driver</div>
          <div className="small">{a.dominant_driver}</div>
        </div>
      </div>

      {cyclePct != null && (
        <div className="panel">
          <h3>Fade Attribution · data-derived (fleet-pooled fit)</h3>
          <div className="attrib">
            <span style={{ width: `${cyclePct}%`, background: CYCLE_COLOR }}>
              Cycle {cyclePct}%
            </span>
            <span style={{ width: `${calPct}%`, background: CALENDAR_COLOR }}>
              Calendar {calPct}%
            </span>
          </div>
          <div className="legend">
            <span>
              <i style={{ background: CYCLE_COLOR }} />
              Cycle (throughput) ageing
            </span>
            <span>
              <i style={{ background: CALENDAR_COLOR }} />
              Calendar ageing
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
