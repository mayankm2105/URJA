"use client";

import { useEffect, useState } from "react";
import {
  fetchValidation,
  fetchValidationCells,
  type NasaCell,
  type ValidationResponse,
} from "@/lib/api";
import NasaChart from "./NasaChart";

export default function ValidationView() {
  const [v, setV] = useState<ValidationResponse | null>(null);
  const [cells, setCells] = useState<NasaCell[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchValidation(), fetchValidationCells()])
      .then(([val, c]) => {
        setV(val);
        setCells(c.cells);
      })
      .catch((e) => setError(String(e)));
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!v) return <div className="loading">Loading real-data validation…</div>;

  const ma = v.model_adequacy;
  const fc = v.knee_onset_forecast;
  const stats = [
    { label: "Real Cells Validated", value: `${v.cells}`, sub: "NASA B0005/6/7/18" },
    { label: "Model Fit RMSE", value: `${ma.max_rmse_pct.toFixed(1)}%`, sub: "max, full trajectory" },
    { label: "SoH Forecast MAE", value: `${fc.soh_mae_pct_mean.toFixed(1)} pp`, sub: "knee-onset holdout" },
    {
      label: "RUL Forecast Error",
      value: `${fc.rul_median_abs_err_cycles}`,
      sub: "median cycles to 80%",
    },
  ];

  // Index forecast rows by cell for the table.
  const fcByCell = new Map(fc.per_cell.map((r) => [r.cell, r]));

  return (
    <div className="validation">
      <div className="val-head">
        <h2>Real-Data Validation</h2>
        <span className="val-source">{v.source}</span>
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

      <div className="panel">
        <h3>Measured capacity fade · real NASA cells</h3>
        <NasaChart cells={cells} />
        <div className="plan-note" style={{ marginTop: 6 }}>
          The same 2-mechanism estimator (loss = a·√EFC + c·EFC) and RUL projection
          that drive the operational fleet, validated against real cells cycled to
          failure. The linear term activates here to track the late-life knee a
          pure-√ model under-predicts.
        </div>
      </div>

      <div className="panel">
        <h3>Per-cell forecast — fit early life ({fc.fit_window}), predict 80% knee</h3>
        <table className="queue">
          <thead>
            <tr>
              <th>Cell</th>
              <th>Fit RMSE</th>
              <th>Fit window</th>
              <th>SoH MAE</th>
              <th>True EoL</th>
              <th>Pred EoL</th>
              <th>RUL err</th>
            </tr>
          </thead>
          <tbody>
            {ma.per_cell.map((m) => {
              const f = fcByCell.get(m.cell);
              const r = f?.rul;
              const predEol = r ? r.true_eol_cycle - r.rul_true_cycles + r.rul_pred_cycles : null;
              return (
                <tr key={m.cell}>
                  <td className="mono">{m.cell}</td>
                  <td className="mono">{m.in_sample_rmse_pct.toFixed(2)}%</td>
                  <td className="mono">{r ? `${r.fit_window_cycles}cyc→${r.cutoff_soh_pct}%` : "—"}</td>
                  <td className="mono">{f ? `${f.soh_mae_pct.toFixed(1)}pp` : "—"}</td>
                  <td className="mono">{r ? `cyc ${r.true_eol_cycle}` : "—"}</td>
                  <td className="mono">{predEol != null ? `cyc ${predEol}` : "—"}</td>
                  <td className="mono">
                    {r ? (
                      <span className={`tag ${r.rul_abs_err_cycles <= 25 ? "ontime" : "overdue"}`}>
                        {r.rul_abs_err_cycles.toFixed(0)} cyc
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
