"use client";

import { useEffect, useState } from "react";
import {
  fetchElectrification,
  fetchElecCandidate,
  type ElecAction,
  type ElecCandidate,
  type ElectrificationResponse,
} from "@/lib/api";

// ---- INR formatting (Indian lakh / crore) ----
function inr(n: number): string {
  if (n >= 1_00_00_000) return `₹${(n / 1_00_00_000).toFixed(2)} Cr`;
  if (n >= 1_00_000) return `₹${(n / 1_00_000).toFixed(1)} L`;
  return `₹${n.toLocaleString("en-IN")}`;
}

const ACTION_COLOR: Record<ElecAction, string> = {
  "Electrify now": "var(--healthy)",
  "Pilot deployment": "var(--aging)",
  "Defer / monitor": "var(--eol)",
};

const SUB_LABELS: { key: keyof ElecCandidate["subscores"]; label: string }[] = [
  { key: "range", label: "Range fit" },
  { key: "charging", label: "Depot charging" },
  { key: "payload", label: "Payload" },
  { key: "duty", label: "Duty cycle" },
  { key: "tco", label: "TCO payback" },
];

function scoreColor(v: number): string {
  if (v >= 70) return "var(--healthy)";
  if (v >= 45) return "var(--aging)";
  return "var(--eol)";
}

export default function ElectrificationView() {
  const [data, setData] = useState<ElectrificationResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ElecCandidate | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchElectrification()
      .then((d) => {
        setData(d);
        if (d.candidates.length > 0) setSelectedId(d.candidates[0].id);
      })
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setDetail(null);
    fetchElecCandidate(selectedId, true)
      .then(setDetail)
      .catch((e) => setError(String(e)));
  }, [selectedId]);

  if (error) return <div className="error">{error}</div>;
  if (!data) return <div className="loading">Loading electrification plan…</div>;

  const m = data.meta;
  const stats = [
    { label: "Electrify Now", value: `${m.electrify_now}`, sub: `of ${m.fleet_size} vehicles · phase 1` },
    { label: "Phase-1 CapEx", value: inr(m.phase1_capex_inr), sub: `≤${m.phase1_max_lead_weeks}-week delivery lead` },
    { label: "Fleet Fuel Saving", value: `${inr(m.fleet_annual_saving_inr)}/yr`, sub: "diesel/CNG → electric" },
    { label: "Avg Readiness", value: `${m.avg_readiness}`, sub: `${m.pilot} pilot · ${m.defer} defer` },
  ];

  return (
    <div className="elec">
      <div className="val-head">
        <h2>Fleet Electrification Readiness &amp; Procurement</h2>
        <span className="val-source">
          Operational data → optimal India-market EV → confidence-scored transition index
        </span>
      </div>

      <div className="val-stats">
        {stats.map((s) => (
          <div className="val-stat" key={s.label}>
            <div className="label">{s.label}</div>
            <div className="value mono">{s.value}</div>
            <div className="sub">{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="elec-grid">
        {/* ---- Candidate board ---- */}
        <div className="elec-board">
          <div className="col-title">Replacement Plan · readiness-ranked</div>
          {data.candidates.map((c) => {
            const color = ACTION_COLOR[c.action];
            const selected = c.id === selectedId;
            return (
              <div
                key={c.id}
                className={`elec-card ${selected ? "selected" : ""}`}
                style={selected ? { borderColor: color, boxShadow: `0 0 0 1px ${color}` } : undefined}
                onClick={() => setSelectedId(c.id)}
              >
                <div className="asset-head">
                  <div>
                    <div className="asset-id mono">{c.name}</div>
                    <div className="asset-name">
                      {c.region} · {c.powertrain.toUpperCase()} → {c.recommended_ev.oem}
                    </div>
                  </div>
                  <div className="asset-soh mono" style={{ color }}>
                    {c.readiness_index}
                  </div>
                </div>
                <div className="sohbar">
                  <span style={{ width: `${c.readiness_index}%`, background: color }} />
                </div>
                <div className="asset-meta">
                  <span className="badge" style={{ color, border: `1px solid ${color}55` }}>
                    {c.action}
                  </span>
                  <span className="badge chem">{c.confidence}% conf</span>
                  <span className="mono" style={{ marginLeft: "auto" }}>
                    {c.recommended_ev.lead_weeks}wk lead
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* ---- Detail ---- */}
        <div className="elec-detail">
          {detail ? <CandidateDetail c={detail} /> : <div className="loading">Loading…</div>}
        </div>
      </div>
    </div>
  );
}

function CandidateDetail({ c }: { c: ElecCandidate }) {
  const color = ACTION_COLOR[c.action];
  const ev = c.recommended_ev;
  const econ = c.economics;
  return (
    <>
      <div className="detail-head">
        <h2>{c.name}</h2>
        <span
          className="status-pill"
          style={{ color, background: `${color}22`, border: `1px solid ${color}66` }}
        >
          {c.action.toUpperCase()}
        </span>
      </div>

      {/* Operational profile + readiness */}
      <div className="panel">
        <h3>Transition Readiness · {c.readiness_index}/100 · {c.confidence}% confidence</h3>
        <div className="subscores">
          {SUB_LABELS.map(({ key, label }) => {
            const v = c.subscores[key];
            return (
              <div className="subrow" key={key}>
                <span className="sublabel">{label}</span>
                <div className="subbar">
                  <span style={{ width: `${v}%`, background: scoreColor(v) }} />
                </div>
                <span className="mono subval">{v}</span>
              </div>
            );
          })}
        </div>
        <div className="plan-note" style={{ marginTop: 12 }}>
          {c.daily_km} km/day · {c.payload_kg} kg payload · {c.dwell_hours} h depot dwell ·
          {c.returns_to_depot ? " returns to depot" : " no depot return"} ·
          {c.route_fixed ? " fixed route" : " variable route"}.{" "}
          <strong style={{ color }}>Binding constraint:</strong> {c.binding_constraint}.
        </div>
      </div>

      {/* Recommended EV */}
      <div className="panel">
        <h3>Recommended EV · {ev.oem}</h3>
        <div className="ev-name mono">{ev.model}</div>
        <div className="tiles" style={{ marginTop: 12 }}>
          <div className="tile">
            <div className="label">Real-world Range</div>
            <div className="big mono">{ev.range_km} km</div>
          </div>
          <div className="tile">
            <div className="label">On-road Price</div>
            <div className="big mono">{inr(ev.price_inr)}</div>
          </div>
          <div className="tile">
            <div className="label">Delivery Lead</div>
            <div className="big mono">{ev.lead_weeks} wk</div>
          </div>
          <div className="tile">
            <div className="label">Charging</div>
            <div className="small mono">{ev.fast_charge ? "DC fast-charge" : "AC depot only"}</div>
          </div>
        </div>
      </div>

      {/* Economics */}
      <div className="panel">
        <h3>Running-cost Case</h3>
        <div className="tiles">
          <div className="tile">
            <div className="label">Fuel → Electric / km</div>
            <div className="small mono">
              ₹{econ.fuel_cost_per_km} → ₹{econ.ev_cost_per_km}
            </div>
          </div>
          <div className="tile">
            <div className="label">Annual Saving</div>
            <div className="big mono" style={{ color: "var(--healthy)" }}>
              {inr(econ.annual_saving_inr)}
            </div>
          </div>
          <div className="tile">
            <div className="label">Saving / km</div>
            <div className="small mono">₹{econ.saving_per_km}</div>
          </div>
          <div className="tile">
            <div className="label">Payback</div>
            <div className="small mono">
              {econ.payback_years != null ? `${econ.payback_years} yr` : "—"}
            </div>
          </div>
        </div>
      </div>

      {/* Agent procurement brief */}
      {c.brief && (
        <div className="panel">
          <h3>Procurement Recommendation · AI Agent</h3>
          <div className="brief-text">{c.brief}</div>
        </div>
      )}

      {/* Alternatives */}
      {c.alternatives.length > 0 && (
        <div className="panel">
          <h3>Alternative Options Considered</h3>
          <table className="queue">
            <thead>
              <tr>
                <th>Model</th>
                <th>OEM</th>
                <th>Index</th>
                <th>Price</th>
                <th>Lead</th>
              </tr>
            </thead>
            <tbody>
              {c.alternatives.map((a) => (
                <tr key={a.id}>
                  <td className="mono">{a.model}</td>
                  <td>{a.oem}</td>
                  <td className="mono">{a.index}</td>
                  <td className="mono">{inr(a.price_inr)}</td>
                  <td className="mono">{a.lead_weeks}wk</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
