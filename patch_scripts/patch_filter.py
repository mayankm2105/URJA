with open("platform-new/src/routes/carbonpulse.tsx", "r") as f:
    code = f.read()

target1 = """      <div className="flex items-center justify-between">
        <SectionTitle eyebrow="Overview" title="Fleet-wide net zero snapshot" />
        <select
          value={fleetId}
          onChange={(e) => setFleetId(e.target.value)}
          className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[13px] text-white outline-none focus:border-[rgba(91,95,237,0.5)]"
        >
          <option value="all">All Fleets Combined</option>
          {fleets.map(f => (
            <option key={f.id} value={f.id}>{f.name}</option>
          ))}
        </select>
      </div>"""
replacement1 = """      <SectionTitle eyebrow="Overview" title="Fleet-wide net zero snapshot" />"""
if target1 in code:
    code = code.replace(target1, replacement1)

target2 = """      <GlassCard padding="md">
        <div className="mb-3">
          <div className="eyebrow">Monthly trajectory</div>
          <div className="mt-1 text-[16px] font-semibold">Scope 1 vs SBTi target vs CO₂ saved by EVs</div>
        </div>"""
replacement2 = """      <GlassCard padding="md">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <div className="eyebrow">Monthly trajectory</div>
            <div className="mt-1 text-[16px] font-semibold">Scope 1 vs SBTi target vs CO₂ saved by EVs</div>
          </div>
          <select
            value={fleetId}
            onChange={(e) => setFleetId(e.target.value)}
            className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[13px] text-white outline-none focus:border-[rgba(91,95,237,0.5)]"
          >
            <option value="all">All Fleets Combined</option>
            {fleets.map(f => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        </div>"""
if target2 in code:
    code = code.replace(target2, replacement2)

with open("platform-new/src/routes/carbonpulse.tsx", "w") as f:
    f.write(code)
