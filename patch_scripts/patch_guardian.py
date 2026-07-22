import re

with open("platform-new/src/routes/fleet-guardian.tsx", "r") as f:
    code = f.read()

# 1. Add useRef to imports if not there
if "useRef" not in code:
    code = code.replace('import { useMemo, useState, useEffect } from "react";', 'import { useMemo, useState, useEffect, useRef } from "react";')

# 2. Update DashboardTab state and refs
target_state = """  const [history, setHistory] = useState<GuardianCycle[]>([]);
  const [rec, setRec] = useState<GuardianRecommendation | null>(null);"""
replacement_state = """  const [history, setHistory] = useState<GuardianCycle[]>([]);
  const [rec, setRec] = useState<GuardianRecommendation | null>(null);

  const detailsRef = useRef<HTMLDivElement>(null);

  const handleAssetClick = (id: string) => {
    setSelectedId(id);
    setTimeout(() => {
      detailsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };"""
code = code.replace(target_state, replacement_state)

# 3. Update heatmap onClick and current_soh formatting
target_heatmap_button = """              key={a.battery_id}
              onClick={() => setSelectedId(a.battery_id)}"""
replacement_heatmap_button = """              key={a.battery_id}
              onClick={() => handleAssetClick(a.battery_id)}"""
code = code.replace(target_heatmap_button, replacement_heatmap_button)

target_soh = """                  <div className="text-[18px] font-semibold tabular-nums">{a.current_soh}%</div>"""
replacement_soh = """                  <div className="text-[18px] font-semibold tabular-nums">{(a.current_soh * 100).toFixed(1)}%</div>"""
code = code.replace(target_soh, replacement_soh)

target_rul = """                RUL {Math.max(0, Math.round((a.current_soh - 70) * 12))} cycles"""
replacement_rul = """                RUL {Math.max(0, Math.round(((a.current_soh * 100) - 70) * 12))} cycles"""
code = code.replace(target_rul, replacement_rul)

# 4. Fix chartData projection
target_chartdata = """  const chartData = useMemo(() => {
    if (!history.length || !asset) return [];
    const proj = Array.from({ length: 15 }, (_, i) => ({
      cycle: history[history.length - 1].cycle + (i + 1) * 4,
      soh: null as number | null,
      projected: +(asset.current_soh - (i + 1) * 0.5).toFixed(2),
      capacity: null as number | null,
    }));
    return [...history.map((h) => ({ cycle: h.cycle, soh: h.soh, capacity: h.capacity, projected: null })), ...proj];
  }, [history, asset]);"""

replacement_chartdata = """  const chartData = useMemo(() => {
    if (!history.length || !health) return [];
    
    const lastCycle = history[history.length - 1].cycle;
    const lastSoh = history[history.length - 1].soh;
    
    const projection: { cycle: number; soh: number | null; capacity: number | null; projected: number | null }[] = [];
    
    let c = lastCycle;
    let s = lastSoh;
    const eol = 70;
    const maxCycles = lastCycle + 120;
    
    while (c < maxCycles && s > eol - 5) {
      c += 1;
      s += (health.slope_blend * 100); // slope_blend is a fraction (e.g., -0.004) -> -0.4%
      projection.push({ cycle: c, soh: null, capacity: null, projected: +(s.toFixed(2)) });
    }
    
    return [
      ...history.map((h) => ({ cycle: h.cycle, soh: h.soh, capacity: h.capacity, projected: null })),
      ...projection
    ];
  }, [history, health]);"""
code = code.replace(target_chartdata, replacement_chartdata)

# 5. Insert AssetTable above details section, and add detailsRef to the details GlassCard
target_details_card = """      <GlassCard padding="md">
        <div className="mb-3 flex items-end justify-between">
          <div>
            <div className="eyebrow">Selected asset</div>"""
replacement_details_card = """      <AssetTable assets={assets} selectedId={selectedId} onSelect={handleAssetClick} />

      <div ref={detailsRef}>
        <GlassCard padding="md">
          <div className="mb-3 flex items-end justify-between">
            <div>
              <div className="eyebrow">Selected asset</div>"""
code = code.replace(target_details_card, replacement_details_card)

# Close the div wrapping details block
target_details_end = """        </GlassCard>
      </div>
    </AgentSection>
  );
}"""
replacement_details_end = """        </GlassCard>
        </div>
      </div>
    </AgentSection>
  );
}"""
code = code.replace(target_details_end, replacement_details_end)

# 6. Append AssetTable and AssetRow components
table_components = """

function AssetTable({ assets, selectedId, onSelect }: { assets: GuardianAsset[], selectedId: string, onSelect: (id: string) => void }) {
  const TIER_ORDER: Record<string, number> = { Critical: 0, Watch: 1, Healthy: 2 };
  const sorted = [...assets].sort((a, b) => TIER_ORDER[a.risk_tier] - TIER_ORDER[b.risk_tier]);
  return (
    <GlassCard padding="md">
      <div className="mb-4 text-[16px] font-semibold">Fleet Inventory</div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-[13px]">
          <thead>
            <tr className="border-b border-white/5 text-[color:var(--color-text-tertiary)]">
              <th className="py-2 pr-4 font-medium uppercase tracking-wider text-[11px]">Asset ID</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">SoH</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">Risk Tier</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">RUL (cycles)</th>
              <th className="py-2 px-4 font-medium uppercase tracking-wider text-[11px]">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(a => (
              <AssetRow key={a.battery_id} asset={a} selected={a.battery_id === selectedId} onSelect={onSelect} />
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
}

function AssetRow({ asset, selected, onSelect }: { asset: GuardianAsset, selected: boolean, onSelect: (id: string) => void }) {
  const [health, setHealth] = useState<GuardianHealth | null>(null);
  useEffect(() => {
    fetchGuardianHealth(asset.battery_id).then(setHealth);
  }, [asset.battery_id]);

  return (
    <tr 
      onClick={() => onSelect(asset.battery_id)}
      className="cursor-pointer border-b border-white/5 transition-colors hover:bg-white/[0.04]"
      style={{ background: selected ? 'rgba(91,95,237,0.1)' : 'transparent' }}
    >
      <td className="py-3 pr-4">
        <div className="font-medium text-white">{asset.battery_id}</div>
        <div className="text-[11px] text-[color:var(--color-text-tertiary)]">{asset.display_name}</div>
      </td>
      <td className="py-3 px-4 tabular-nums text-[14px]">{(asset.current_soh * 100).toFixed(1)}%</td>
      <td className="py-3 px-4"><StatusPill tone={TIER_TONE[asset.risk_tier]}>{asset.risk_tier}</StatusPill></td>
      <td className="py-3 px-4 tabular-nums text-[color:var(--color-text-secondary)] text-[14px]">
        {health ? health.rul_cycles : '...'}
      </td>
      <td className="py-3 px-4">
        {health ? (
          <div className="flex flex-col">
            <span className={health.confidence_level === 'asset_specific' ? 'text-white' : 'text-yellow-400'}>
              {health.confidence_level === 'asset_specific' ? 'asset-specific' : 'population'}
            </span>
            <span className="text-[11px] text-[color:var(--color-text-tertiary)]">± {health.confidence_band_cycles} cycles</span>
          </div>
        ) : '...'}
      </td>
    </tr>
  );
}
"""
code += table_components

with open("platform-new/src/routes/fleet-guardian.tsx", "w") as f:
    f.write(code)
