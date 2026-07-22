"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AssetDetail } from "@/lib/api";
import { bandColor } from "@/lib/colors";

interface Row {
  efc: number;
  observed?: number;
  predicted?: number;
}

export default function SohChart({ detail }: { detail: AssetDetail }) {
  const eol = 80;
  const band = detail.summary.soh_band;

  // Merge observed history and forward projection onto one EFC axis.
  const rows: Row[] = detail.history.map((p) => ({
    efc: Math.round(p.efc),
    observed: p.soh_observed != null ? +(p.soh_observed * 100).toFixed(2) : undefined,
  }));
  detail.projection.forEach((p) => {
    rows.push({
      efc: Math.round(p.efc),
      predicted: p.soh_predicted != null ? +(p.soh_predicted * 100).toFixed(2) : undefined,
    });
  });

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <LineChart data={rows} margin={{ top: 8, right: 16, bottom: 18, left: -8 }}>
          <CartesianGrid stroke="#1e2747" strokeDasharray="3 3" />
          <XAxis
            dataKey="efc"
            type="number"
            domain={["dataMin", "dataMax"]}
            tick={{ fill: "#5a6493", fontSize: 11 }}
            stroke="#1e2747"
            label={{
              value: "Equivalent Full Cycles",
              position: "insideBottom",
              offset: -10,
              fill: "#5a6493",
              fontSize: 11,
            }}
          />
          <YAxis
            domain={[38, 100]}
            ticks={[40, 60, 80, 100]}
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
            formatter={(v: number, name: string) => [
              `${v}%`,
              name === "observed" ? "Observed SoH" : "Projected SoH",
            ]}
            labelFormatter={(l) => `${l} EFC`}
          />
          <ReferenceLine
            y={eol}
            stroke="#ff5d52"
            strokeDasharray="6 4"
            label={{
              value: "End-of-Life knee (80%)",
              fill: "#ff5d52",
              fontSize: 10,
              position: "insideTopRight",
            }}
          />
          <Line
            dataKey="observed"
            stroke={bandColor(band)}
            strokeWidth={2}
            dot={{ r: 1.5, fill: bandColor(band) }}
            connectNulls
            isAnimationActive={false}
            name="observed"
          />
          <Line
            dataKey="predicted"
            stroke="#5b8cff"
            strokeWidth={2}
            strokeDasharray="6 4"
            dot={false}
            connectNulls
            isAnimationActive={false}
            name="predicted"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
