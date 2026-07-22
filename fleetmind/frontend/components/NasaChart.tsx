"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { NasaCell } from "@/lib/api";

const CELL_COLORS: Record<string, string> = {
  B0005: "#5b8cff",
  B0006: "#ff5d52",
  B0007: "#10b981",
  B0018: "#ee9800",
};

export default function NasaChart({ cells }: { cells: NasaCell[] }) {
  // Merge all cells onto one cycle axis: { cycle, B0005, B0006, ... } in % SoH.
  const byCycle = new Map<number, Record<string, number>>();
  for (const cell of cells) {
    for (const p of cell.series) {
      const row = byCycle.get(p.efc) ?? { cycle: p.efc };
      row[cell.id] = +(p.soh_observed * 100).toFixed(2);
      byCycle.set(p.efc, row);
    }
  }
  const data = Array.from(byCycle.values()).sort((a, b) => a.cycle - b.cycle);

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 18, left: -8 }}>
          <CartesianGrid stroke="#1e2747" strokeDasharray="3 3" />
          <XAxis
            dataKey="cycle"
            type="number"
            domain={["dataMin", "dataMax"]}
            tick={{ fill: "#5a6493", fontSize: 11 }}
            stroke="#1e2747"
            label={{
              value: "Discharge cycle",
              position: "insideBottom",
              offset: -10,
              fill: "#5a6493",
              fontSize: 11,
            }}
          />
          <YAxis
            domain={[50, 100]}
            ticks={[50, 60, 70, 80, 90, 100]}
            allowDataOverflow
            tick={{ fill: "#5a6493", fontSize: 11 }}
            stroke="#1e2747"
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              background: "#0f1530",
              border: "1px solid #2a3566",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "#8b96c0" }}
            formatter={(v: number, name: string) => [`${v}%`, name]}
            labelFormatter={(l) => `cycle ${l}`}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: "#8b96c0" }} />
          <ReferenceLine
            y={80}
            stroke="#ff5d52"
            strokeDasharray="6 4"
            label={{
              value: "End-of-Life knee (80%)",
              fill: "#ff5d52",
              fontSize: 10,
              position: "insideTopRight",
            }}
          />
          {cells.map((cell) => (
            <Line
              key={cell.id}
              dataKey={cell.id}
              name={cell.label}
              stroke={CELL_COLORS[cell.id] ?? "#8b96c0"}
              strokeWidth={2}
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
