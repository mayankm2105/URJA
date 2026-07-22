import re

with open("platform-new/src/routes/fleetmind.tsx", "r") as f:
    code = f.read()

# Add BAND_TONE_COLOR and rulBig helper
new_helpers = """const BAND_TONE: Record<SoHBand, "healthy" | "watch" | "critical"> = {
  healthy: "healthy",
  aging: "watch",
  end_of_life: "critical",
};

const BAND_TONE_COLOR: Record<SoHBand, string> = {
  healthy: "#34d399",
  aging: "#fbbf24",
  end_of_life: "#f87171",
};

function rulBig(a: AssetSummary): string {
  if (a.horizon_capped) return ">10 years";
  if (a.rul_days <= 0) return "0 days";
  if (a.rul_days >= 365) return `${(a.rul_days / 365).toFixed(1)} years`;
  return `${a.rul_days.toFixed(0)} days`;
}
"""
code = code.replace("""const BAND_TONE: Record<SoHBand, "healthy" | "watch" | "critical"> = {
  healthy: "healthy",
  aging: "watch",
  end_of_life: "critical",
};""", new_helpers)

# Add the 4 data tiles to FleetTab
tiles_html = """            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 gap-4 xl:grid-cols-4">
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Current SoH</div>
                <div className="mt-1 text-[20px] font-semibold tabular-nums" style={{ color: BAND_TONE_COLOR[asset.soh_band] }}>
                  {(asset.soh * 100).toFixed(1)}%
                </div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Remaining Useful Life</div>
                <div className="mt-1 text-[20px] font-semibold tabular-nums">{rulBig(asset)}</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Equivalent Full Cycles</div>
                <div className="mt-1 text-[16px] font-semibold tabular-nums">{asset.efc_total.toLocaleString()} EFC</div>
              </div>
              <div className="rounded-[10px] border border-white/5 bg-white/[0.02] p-3">
                <div className="text-[11px] uppercase tracking-wider text-[color:var(--color-text-tertiary)]">Dominant Fade Driver</div>
                <div className="mt-1 text-[14px] font-medium text-[color:var(--color-text-primary)]">{asset.dominant_driver}</div>
              </div>
            </div>"""

code = code.replace("</ResponsiveContainer>", tiles_html)

# Add the AI Maintenance plan
plan_html = """        </table>
        {maintData.plan && (
          <div className="mt-4 rounded-[12px] border border-[rgba(91,95,237,0.25)] bg-[rgba(91,95,237,0.06)] p-3">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-hover)]">Asset Health Brief</div>
            <div className="mt-1 text-[13px] leading-relaxed text-[color:var(--color-text-secondary)]">
              {maintData.plan}
            </div>
          </div>
        )}"""
code = code.replace("</table>", plan_html)


with open("platform-new/src/routes/fleetmind.tsx", "w") as f:
    f.write(code)
