import { GlassCard } from "@/components/urja/GlassCard";
import { StatCard } from "@/components/urja/StatCard";
import { StatusPill } from "@/components/urja/StatusPill";
import { UAreaChart, HeatGrid } from "@/components/urja/UChart";
import { makeSeries, makeHeat, type Severity } from "@/lib/urja-mock";
import type { ReactNode } from "react";

export function SectionTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="mb-5">
      <div className="eyebrow">{eyebrow}</div>
      <h2 className="mt-1.5 text-[22px] font-semibold">{title}</h2>
    </div>
  );
}

export function TwoColKpi({
  items,
}: {
  items: { label: string; value: number; suffix?: string; decimals?: number; hint?: string; status?: { tone: Severity; label: string } }[];
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {items.map((k) => (
        <StatCard key={k.label} {...k} />
      ))}
    </div>
  );
}

export function ChartCard({
  eyebrow,
  title,
  threshold,
  seed = 20,
}: {
  eyebrow: string;
  title: string;
  threshold?: number;
  seed?: number;
}) {
  return (
    <GlassCard padding="md">
      <div className="mb-2 flex items-end justify-between">
        <div>
          <div className="eyebrow">{eyebrow}</div>
          <div className="mt-1 text-[16px] font-semibold">{title}</div>
        </div>
      </div>
      <UAreaChart data={makeSeries(24, seed, 4, 0.15)} threshold={threshold} />
    </GlassCard>
  );
}

export function ListCard({
  title,
  rows,
}: {
  title: string;
  rows: { label: string; value: string; tone?: Severity }[];
}) {
  return (
    <GlassCard padding="md">
      <div className="mb-3 text-[16px] font-semibold">{title}</div>
      <div className="flex flex-col divide-y divide-white/5">
        {rows.map((r) => (
          <div key={r.label} className="flex items-center justify-between py-3">
            <span className="text-[14px] text-[color:var(--color-text-secondary)]">
              {r.label}
            </span>
            <div className="flex items-center gap-3">
              <span className="text-[14px] font-medium">{r.value}</span>
              {r.tone && <StatusPill tone={r.tone}>{r.tone}</StatusPill>}
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}

export function HeatCard({ title, count = 84 }: { title: string; count?: number }) {
  return (
    <GlassCard padding="md">
      <div className="mb-4 flex items-center justify-between">
        <div className="text-[16px] font-semibold">{title}</div>
        <div className="flex items-center gap-2">
          <StatusPill tone="healthy">Healthy</StatusPill>
          <StatusPill tone="watch">Watch</StatusPill>
          <StatusPill tone="critical">Critical</StatusPill>
        </div>
      </div>
      <HeatGrid cells={makeHeat(count)} />
    </GlassCard>
  );
}

export function AgentSection({ children }: { children: ReactNode }) {
  return <div className="fade-up flex flex-col gap-6">{children}</div>;
}
