import re

with open("platform-new/src/routes/fleetmind.tsx", "r") as f:
    code = f.read()

# Fix 1: fetchAsset(selectedId, true)
code = code.replace("fetchAsset(selectedId).then(setDetail);", "fetchAsset(selectedId, true).then(setDetail);")

# Fix 2: Render detail.brief in Recommendations
target_rec = """            <GlassCard padding="md">
              <div className="mb-3 text-[15px] font-semibold">Recommendations</div>
              <ul className="flex flex-col gap-2">"""
replacement_rec = """            <GlassCard padding="md">
              <div className="mb-3 text-[15px] font-semibold">Recommendations</div>
              {detail.brief && <div className="mb-3 text-[13px] leading-relaxed text-[color:var(--color-text-secondary)]">{detail.brief}</div>}
              <ul className="flex flex-col gap-2">"""
code = code.replace(target_rec, replacement_rec)

# Fix 3: Restore the Validation table
target_table = """          </BarChart>
                    </ResponsiveContainer>

      </GlassCard>"""
replacement_table = """          </BarChart>
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
code = code.replace(target_table, replacement_table)

with open("platform-new/src/routes/fleetmind.tsx", "w") as f:
    f.write(code)
