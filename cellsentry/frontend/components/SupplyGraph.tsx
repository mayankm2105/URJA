"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import type { GraphEdge, GraphNode } from "@/lib/api";
import { bandColor, HOT } from "@/lib/colors";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

const TYPE_SIZE: Record<string, number> = {
  product: 11,
  pack: 9,
  cell: 8,
  material: 6,
  raw_material: 6,
  supplier: 5,
  country: 4,
};

function endId(end: unknown): string {
  return typeof end === "object" && end !== null ? (end as { id: string }).id : (end as string);
}

export default function SupplyGraph({
  nodes,
  edges,
  hotIds,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  hotIds: Set<string>;
}) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ w: 800, h: 600 });

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setDims({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    setDims({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, []);

  const graphData = useMemo(
    () => ({ nodes: nodes.map((n) => ({ ...n })), links: edges.map((e) => ({ ...e })) }),
    [nodes, edges],
  );

  const linkHot = (l: any) => hotIds.has(endId(l.source)) && hotIds.has(endId(l.target));

  return (
    <div ref={wrapRef} style={{ width: "100%", height: "100%" }}>
      <ForceGraph2D
        width={dims.w}
        height={dims.h}
        graphData={graphData}
        nodeId="id"
        linkSource="source"
        linkTarget="target"
        dagMode="td"
        dagLevelDistance={52}
        backgroundColor="rgba(0,0,0,0)"
        cooldownTicks={90}
        d3VelocityDecay={0.3}
        linkColor={(l: any) => (linkHot(l) ? HOT : "rgba(148,163,184,0.22)")}
        linkWidth={(l: any) => (linkHot(l) ? 2.5 : 1)}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={(l: any) => (linkHot(l) ? 3 : 0)}
        linkDirectionalParticleWidth={2.5}
        linkDirectionalParticleColor={() => HOT}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, scale: number) => {
          const r = TYPE_SIZE[node.type] ?? 5;
          const hot = hotIds.has(node.id);
          ctx.save();
          if (hot) {
            ctx.shadowColor = HOT;
            ctx.shadowBlur = 18;
          }
          ctx.beginPath();
          ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
          ctx.fillStyle = bandColor(node.risk_band);
          ctx.fill();
          ctx.restore();

          ctx.lineWidth = hot ? 1.8 : 0.6;
          ctx.strokeStyle = hot ? "#ffd0cc" : "rgba(2,6,23,0.7)";
          ctx.beginPath();
          ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
          ctx.stroke();

          const fontSize = Math.max(11 / scale, 3);
          ctx.font = `${fontSize}px Inter, system-ui, sans-serif`;
          ctx.fillStyle = hot ? "#ffe9e7" : "#cdd5e6";
          ctx.textAlign = "center";
          ctx.textBaseline = "top";
          ctx.fillText(node.label, node.x, node.y + r + 1.5);
        }}
        nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
          const r = (TYPE_SIZE[node.type] ?? 5) + 3;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
          ctx.fill();
        }}
      />
    </div>
  );
}
