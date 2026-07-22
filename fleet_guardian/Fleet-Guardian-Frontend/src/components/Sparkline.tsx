export function Sparkline({
  data,
  width = 140,
  height = 36,
  stroke = "var(--accent)",
}: {
  data: { cycle: number; soh: number }[];
  width?: number;
  height?: number;
  stroke?: string;
}) {
  if (data.length < 2) return null;
  const xs = data.map((d) => d.cycle);
  const ys = data.map((d) => d.soh);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys) - 1;
  const maxY = Math.max(...ys) + 1;
  const nx = (x: number) => ((x - minX) / (maxX - minX || 1)) * (width - 4) + 2;
  const ny = (y: number) => height - 2 - ((y - minY) / (maxY - minY || 1)) * (height - 4);
  const d = data.map((p, i) => `${i === 0 ? "M" : "L"}${nx(p.cycle).toFixed(1)},${ny(p.soh).toFixed(1)}`).join(" ");
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="block">
      <path d={d} fill="none" stroke={stroke} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
