import re

with open("platform-new/src/routes/carbonpulse.tsx", "r") as f:
    code = f.read()

# 1. Update imports
target_import = """  fetchCarbonValidation,
  type CarbonDashboard,
  type EmissionPoint,"""
replacement_import = """  fetchCarbonValidation,
  fetchFleets,
  type CarbonDashboard,
  type EmissionPoint,
  type Fleet,"""
code = code.replace(target_import, replacement_import)

# 2. Update DashboardTab
target_dashboard = """function DashboardTab() {
  const [d, setD] = useState<CarbonDashboard | null>(null);
  const [ts, setTs] = useState<EmissionPoint[]>([]);
  useEffect(() => {
    fetchCarbonDashboard().then(setD);
    fetchEmissions().then(setTs);
  }, []);
  if (!d) return null;
  return (
    <AgentSection>
      <SectionTitle eyebrow="Overview" title="Fleet-wide net zero snapshot" />"""

replacement_dashboard = """function DashboardTab() {
  const [d, setD] = useState<CarbonDashboard | null>(null);
  const [ts, setTs] = useState<EmissionPoint[]>([]);
  const [fleets, setFleets] = useState<Fleet[]>([]);
  const [fleetId, setFleetId] = useState<string>("all");

  useEffect(() => {
    fetchFleets().then(setFleets);
    fetchCarbonDashboard().then(setD);
  }, []);

  useEffect(() => {
    fetchEmissions(fleetId).then(setTs);
  }, [fleetId]);

  if (!d) return null;
  return (
    <AgentSection>
      <div className="flex items-center justify-between">
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
code = code.replace(target_dashboard, replacement_dashboard)

# 3. AdvisorTab height
target_advisor_1 = """          <div className="flex-1 space-y-3 overflow-y-auto pr-1" style={{ maxHeight: 480 }}>"""
replacement_advisor_1 = """          <div className="flex-1 space-y-3 overflow-y-auto pr-1" style={{ height: "70vh" }}>"""
code = code.replace(target_advisor_1, replacement_advisor_1)

target_advisor_2 = """        <GlassCard padding="md">
          <div className="mb-3 text-[16px] font-semibold">AI Electrification Priorities</div>
          <div className="flex flex-col gap-3">"""
replacement_advisor_2 = """        <GlassCard padding="md">
          <div className="mb-3 text-[16px] font-semibold">AI Electrification Priorities</div>
          <div className="flex flex-col gap-3 overflow-y-auto pr-1" style={{ height: "70vh" }}>"""
code = code.replace(target_advisor_2, replacement_advisor_2)

with open("platform-new/src/routes/carbonpulse.tsx", "w") as f:
    f.write(code)

