import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from "recharts";

type Point = { x: string | number; y: number };

export function UAreaChart({
  data,
  threshold,
  height = 220,
  color = "#5b5fed",
}: {
  data: Point[];
  threshold?: number;
  height?: number;
  color?: string;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="uarea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.45} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
        <XAxis
          dataKey="x"
          stroke="#5c5c68"
          tick={{ fill: "#9a9aa8", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          stroke="#5c5c68"
          tick={{ fill: "#9a9aa8", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{
            background: "rgba(15,17,23,0.95)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 12,
            fontSize: 12,
          }}
          labelStyle={{ color: "#f5f5f7" }}
        />
        {threshold != null && (
          <ReferenceLine
            y={threshold}
            stroke="#f87171"
            strokeDasharray="4 4"
            strokeOpacity={0.7}
          />
        )}
        <Area
          type="monotone"
          dataKey="y"
          stroke={color}
          strokeWidth={2}
          fill="url(#uarea)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function HeatGrid({
  cells,
  cols = 12,
}: {
  cells: { tone: "healthy" | "watch" | "critical"; intensity?: number }[];
  cols?: number;
}) {
  const color = (t: string) =>
    t === "healthy" ? "#34d399" : t === "watch" ? "#fbbf24" : "#f87171";
  return (
    <div
      className="grid gap-1.5"
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(0,1fr))` }}
    >
      {cells.map((c, i) => (
        <div
          key={i}
          className="aspect-square rounded-[4px]"
          style={{
            background: color(c.tone),
            opacity: 0.3 + (c.intensity ?? 0.7) * 0.7,
          }}
        />
      ))}
    </div>
  );
}
