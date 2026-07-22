import re

with open("platform-new/src/routes/fleetmind.tsx", "r") as f:
    code = f.read()

# Update state and data fetching in ElectrifyTab
fetch_old = """function ElectrifyTab() {
  const [elecData, setElecData] = useState<ElectrificationResponse | null>(null);
  useEffect(() => {
    fetchElectrification().then(setElecData);
  }, []);"""
  
fetch_new = """function ElectrifyTab() {
  const [elecData, setElecData] = useState<ElectrificationResponse | null>(null);
  const [enriched, setEnriched] = useState<Record<string, ElecCandidate>>({});
  
  useEffect(() => {
    fetchElectrification().then(async (data) => {
      setElecData(data);
      try {
        const details = await Promise.all(data.candidates.map(c => fetchElecCandidate(c.id, true)));
        const map: Record<string, ElecCandidate> = {};
        for (const d of details) map[d.id] = d;
        setEnriched(map);
      } catch(e) {
        console.error("Failed to fetch detailed AI briefs", e);
      }
    });
  }, []);"""

code = code.replace(fetch_old, fetch_new)

# Insert the Operational profile text and AI brief at the bottom of the card
card_end_old = """              </div>
            </div>
          </GlassCard>
        ))}"""

card_end_new = """              </div>
            </div>
            
            {/* Operational profile text added from standalone */}
            <div className="mt-4 text-[12px] leading-relaxed text-[color:var(--color-text-secondary)]">
              {c.daily_km} km/day · {c.payload_kg} kg payload · {c.dwell_hours} h depot dwell ·
              {c.returns_to_depot ? " returns to depot" : " no depot return"} ·
              {c.route_fixed ? " fixed route" : " variable route"}.
            </div>

            {/* AI Brief fetched via fetchElecCandidate */}
            {enriched[c.id]?.brief && (
              <div className="mt-3 rounded-[12px] border border-[rgba(91,95,237,0.25)] bg-[rgba(91,95,237,0.06)] p-3">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-hover)]">Procurement Recommendation · AI Agent</div>
                <div className="mt-1 text-[12px] leading-relaxed text-[color:var(--color-text-secondary)]">
                  {enriched[c.id].brief}
                </div>
              </div>
            )}
          </GlassCard>
        ))}"""

code = code.replace(card_end_old, card_end_new)

with open("platform-new/src/routes/fleetmind.tsx", "w") as f:
    f.write(code)
