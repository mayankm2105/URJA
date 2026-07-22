import re

with open("platform-new/src/lib/carbon.ts", "r") as f:
    code = f.read()

# Add Fleet interface
fleet_interface = """export interface Fleet {
  id: number;
  name: string;
}

"""
code = fleet_interface + code

# Update fetchEmissions
old_fetch = """export function fetchEmissions(): Promise<EmissionPoint[]> {
  return getJSON<EmissionPoint[]>("/emissions/timeseries");
}"""
new_fetch = """export function fetchEmissions(fleetId?: number | string): Promise<EmissionPoint[]> {
  const q = fleetId && fleetId !== 'all' ? `?fleet_id=${fleetId}` : '';
  return getJSON<EmissionPoint[]>(`/emissions/timeseries${q}`);
}

export function fetchFleets(): Promise<Fleet[]> {
  return getJSON<Fleet[]>("/fleet");
}"""

if old_fetch in code:
    code = code.replace(old_fetch, new_fetch)
else:
    # Just in case the URI was slightly different
    code = re.sub(r'export function fetchEmissions\(\): Promise<EmissionPoint\[\]> \{\s*return getJSON<EmissionPoint\[\]>\("/emissions[^"]*"\);\s*\}', new_fetch, code)

with open("platform-new/src/lib/carbon.ts", "w") as f:
    f.write(code)

