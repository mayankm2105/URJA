export function TrajectoryChart({
  history,
  projectionCycles = 80,
  slope,
  eol = 70,
}: {
  history: { cycle: number; soh: number }[];
  projectionCycles?: number;
  slope: number; // negative
  eol?: number;
}) {
  const width = 800;
  const height = 320;
  const padL = 44;
  const padR = 16;
  const padT = 16;
  const padB = 32;

  const lastCycle = history[history.length - 1]?.cycle ?? 0;
  const lastSoh = history[history.length - 1]?.soh ?? 100;

  // Build projection until it hits eol or projectionCycles
  const projection: { cycle: number; soh: number }[] = [];
  let c = lastCycle;
  let s = lastSoh;
  const maxCycles = lastCycle + projectionCycles + 60;
  while (c < maxCycles && s > eol - 5) {
    projection.push({ cycle: c, soh: s });
    c += 1;
    s += slope;
  }
  projection.push({ cycle: c, soh: s });

  const all = [...history, ...projection];
  const minX = 0;
  const maxX = Math.max(...all.map((d) => d.cycle));
  const minY = Math.min(60, eol - 2, ...all.map((d) => d.soh));
  const maxY = 100;

  const nx = (x: number) => ((x - minX) / (maxX - minX || 1)) * (width - padL - padR) + padL;
  const ny = (y: number) => padT + (1 - (y - minY) / (maxY - minY || 1)) * (height - padT - padB);

  const path = (arr: { cycle: number; soh: number }[]) =>
    arr.map((p, i) => `${i === 0 ? "M" : "L"}${nx(p.cycle).toFixed(1)},${ny(p.soh).toFixed(1)}`).join(" ");

  const gridYs = [70, 80, 90, 100];
  const gridXStep = Math.ceil(maxX / 6);
  const gridXs: number[] = [];
  for (let x = 0; x <= maxX; x += gridXStep) gridXs.push(x);

  const areaPath =
    `M${nx(history[0].cycle).toFixed(1)},${ny(minY).toFixed(1)} ` +
    history.map((p) => `L${nx(p.cycle).toFixed(1)},${ny(p.soh).toFixed(1)}`).join(" ") +
    ` L${nx(history[history.length - 1].cycle).toFixed(1)},${ny(minY).toFixed(1)} Z`;

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[560px]" role="img" aria-label="Capacity fade trajectory">
        <defs>
          <linearGradient id="areaFade" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.18" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Gridlines */}
        {gridYs.map((y) => (
          <g key={`gy-${y}`}>
            <line x1={padL} x2={width - padR} y1={ny(y)} y2={ny(y)} stroke="var(--chart-grid)" strokeWidth={1} />
            <text x={padL - 8} y={ny(y) + 4} textAnchor="end" fontSize="11" fill="var(--text-tertiary)" fontFamily="var(--font-mono)">
              {y}%
            </text>
          </g>
        ))}
        {gridXs.map((x) => (
          <g key={`gx-${x}`}>
            <line x1={nx(x)} x2={nx(x)} y1={padT} y2={height - padB} stroke="var(--chart-grid)" strokeWidth={1} opacity="0.5" />
            <text x={nx(x)} y={height - padB + 16} textAnchor="middle" fontSize="11" fill="var(--text-tertiary)" fontFamily="var(--font-mono)">
              {x}
            </text>
          </g>
        ))}

        {/* EOL threshold */}
        <line
          x1={padL}
          x2={width - padR}
          y1={ny(eol)}
          y2={ny(eol)}
          stroke="var(--critical)"
          strokeWidth={1.5}
          strokeDasharray="6 5"
          opacity={0.7}
        />
        <text x={width - padR} y={ny(eol) - 6} textAnchor="end" fontSize="11" fill="var(--critical)" fontFamily="var(--font-sans)">
          70% EOL threshold
        </text>

        {/* Area under actual line */}
        <path d={areaPath} fill="url(#areaFade)" />

        {/* Actual */}
        <path d={path(history)} fill="none" stroke="var(--accent)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        {/* Projection */}
        <path
          d={path(projection)}
          fill="none"
          stroke="var(--text-tertiary)"
          strokeWidth={2}
          strokeDasharray="4 4"
          strokeLinecap="round"
        />

        {/* X-axis label */}
        <text x={(width + padL - padR) / 2} y={height - 6} textAnchor="middle" fontSize="11" fill="var(--text-tertiary)">
          Cycle
        </text>
      </svg>
    </div>
  );
}
