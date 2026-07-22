import re

with open("platform-new/src/routes/fleetmind.tsx", "r") as f:
    code = f.read()

# Fix 1: Remove all instances of fcByCell being defined, and we will place it EXACTLY where it belongs.
code = re.sub(r'  const fcByCell = new Map\(valData\.knee_onset_forecast\.per_cell\.map\(\(r\) => \[r\.cell, r\]\)\);\n\n', '', code)

# Place it only in ValidationTab right after chartData
target = """    rul_abs_err_cycles: pc.rul?.rul_abs_err_cycles ?? 0
  }));"""
replacement = """    rul_abs_err_cycles: pc.rul?.rul_abs_err_cycles ?? 0
  }));

  const fcByCell = new Map(valData.knee_onset_forecast.per_cell.map((r) => [r.cell, r]));"""
code = code.replace(target, replacement)

# Fix 2: Remove the duplicated Data Tiles from ValidationTab
# The Data Tiles block starts with `<div className="mt-4 grid grid-cols-2 gap-4 xl:grid-cols-4">` and ends before `</GlassCard>`
# Actually we can just locate it at the end of the file
bad_tiles = """                    </ResponsiveContainer>
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
            </div>
      </GlassCard>
    </AgentSection>
  );
}"""

good_ending = """                    </ResponsiveContainer>
      </GlassCard>
    </AgentSection>
  );
}"""
code = code.replace(bad_tiles, good_ending)

# Fix 3: Add imports
import_old = """  type ValidationCellsResponse,
  type HealthBand as SoHBand,
} from "@/lib/fleet";"""

import_new = """  type ValidationCellsResponse,
  type HealthBand as SoHBand,
  fetchElecCandidate,
  type ElecCandidate,
} from "@/lib/fleet";"""
code = code.replace(import_old, import_new)

with open("platform-new/src/routes/fleetmind.tsx", "w") as f:
    f.write(code)
