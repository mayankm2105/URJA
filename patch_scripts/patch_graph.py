import re

with open("platform-new/src/routes/fleet-guardian.tsx", "r") as f:
    code = f.read()

target = """  const chartData = useMemo(() => {
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

replacement = """  const chartData = useMemo(() => {
    if (!history.length || !health) return [];
    
    const lastCycle = history[history.length - 1].cycle;
    const lastSoh = history[history.length - 1].soh * 100;
    
    const projection: { cycle: number; soh: number | null; capacity: number | null; projected: number | null }[] = [];
    
    let c = lastCycle;
    let s = lastSoh;
    const eol = 70;
    const maxCycles = lastCycle + 120;
    
    while (c < maxCycles && s > eol - 5) {
      c += 1;
      s += (health.slope_blend * 100);
      projection.push({ cycle: c, soh: null, capacity: null, projected: +(s.toFixed(2)) });
    }
    
    return [
      ...history.map((h) => ({ cycle: h.cycle, soh: h.soh * 100, capacity: h.capacity, projected: null })),
      ...projection
    ];
  }, [history, health]);"""

if target in code:
    code = code.replace(target, replacement)

with open("platform-new/src/routes/fleet-guardian.tsx", "w") as f:
    f.write(code)

