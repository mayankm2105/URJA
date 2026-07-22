import re

with open("platform-new/src/routes/fleetmind.tsx", "r") as f:
    code = f.read()

# Add fcByCell before return in ValidationTab
val_return_old = """  return (
    <AgentSection>"""
val_return_new = """  const fcByCell = new Map(valData.knee_onset_forecast.per_cell.map((r) => [r.cell, r]));

  return (
    <AgentSection>"""
code = code.replace(val_return_old, val_return_new)

# Add the table below the BarChart GlassCard
bar_chart_old = """            <Bar dataKey="rul_abs_err_cycles" name="RUL |err| cycles" fill="#3e8ef7" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </GlassCard>"""
bar_chart_new = """            <Bar dataKey="rul_abs_err_cycles" name="RUL |err| cycles" fill="#3e8ef7" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-6">
          <div className="mb-3 text-[15px] font-semibold">Per-cell forecast — fit early life ({valData.knee_onset_forecast.fit_window}), predict 80% knee</div>
          <table className="w-full text-[13px]">
            <thead className="text-left text-[color:var(--color-text-secondary)]">
              <tr>
                <th className="pb-2 font-medium">Cell</th>
                <th className="pb-2 font-medium">Fit RMSE</th>
                <th className="pb-2 font-medium">Fit window</th>
                <th className="pb-2 font-medium">SoH MAE</th>
                <th className="pb-2 font-medium">True EoL</th>
                <th className="pb-2 font-medium">Pred EoL</th>
                <th className="pb-2 font-medium">RUL err</th>
              </tr>
            </thead>
            <tbody>
              {valData.model_adequacy.per_cell.map((m) => {
                const f = fcByCell.get(m.cell);
                const r = f?.rul;
                const predEol = r ? r.true_eol_cycle - r.rul_true_cycles + r.rul_pred_cycles : null;
                return (
                  <tr key={m.cell} className="border-t border-white/5">
                    <td className="py-2 tabular-nums">{m.cell}</td>
                    <td className="py-2 tabular-nums">{m.in_sample_rmse_pct.toFixed(2)}%</td>
                    <td className="py-2 tabular-nums text-[color:var(--color-text-secondary)]">{r ? `${r.fit_window_cycles}cyc → ${r.cutoff_soh_pct}%` : "—"}</td>
                    <td className="py-2 tabular-nums">{f ? `${f.soh_mae_pct.toFixed(1)}pp` : "—"}</td>
                    <td className="py-2 tabular-nums">{r ? `cyc ${r.true_eol_cycle}` : "—"}</td>
                    <td className="py-2 tabular-nums">{predEol != null ? `cyc ${predEol}` : "—"}</td>
                    <td className="py-2 tabular-nums">
                      {r ? (
                        <StatusPill tone={r.rul_abs_err_cycles <= 25 ? "healthy" : "critical"}>
                          {r.rul_abs_err_cycles.toFixed(0)} cyc
                        </StatusPill>
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
      </GlassCard>"""
code = code.replace(bar_chart_old, bar_chart_new)

with open("platform-new/src/routes/fleetmind.tsx", "w") as f:
    f.write(code)
