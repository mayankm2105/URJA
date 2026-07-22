import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { queryOptions } from "@tanstack/react-query";
import { getFleetHealth, type AssetHealth, type RiskTier } from "@/lib/api";
import { RiskBadge } from "@/components/RiskBadge";
import { Sparkline } from "@/components/Sparkline";
import { Navbar, Footer } from "@/components/Chrome";

const fleetQuery = queryOptions({
  queryKey: ["fleet-health"],
  queryFn: () => getFleetHealth(),
  staleTime: 30_000,
});

export const Route = createFileRoute("/")({
  loader: ({ context }) => context.queryClient.ensureQueryData(fleetQuery),
  component: FleetDashboard,
  pendingComponent: () => (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <div className="mx-auto max-w-[1200px] px-6 py-16">
        <div className="skeleton h-8 w-56" />
        <div className="mt-6 skeleton h-14 w-96" />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          <div className="skeleton h-40" />
          <div className="skeleton h-40" />
          <div className="skeleton h-40" />
        </div>
      </div>
    </div>
  ),
  errorComponent: ({ error }) => (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <div className="mx-auto max-w-[720px] px-6 py-24 text-center">
        <p className="eyebrow">Error</p>
        <h1 className="mt-2 text-[32px] font-bold">Fleet data unavailable</h1>
        <p className="mt-3 text-text-secondary">{error.message}</p>
      </div>
    </div>
  ),
});

const TIER_ORDER: Record<RiskTier, number> = { Critical: 0, Watch: 1, Healthy: 2 };

function FleetDashboard() {
  const { data } = useSuspenseQuery(fleetQuery);
  const sorted = [...data].sort((a, b) => TIER_ORDER[a.risk_tier] - TIER_ORDER[b.risk_tier]);
  const avgSoh = data.reduce((s, a) => s + a.soh, 0) / data.length;
  const counts = { Healthy: 0, Watch: 0, Critical: 0 } as Record<RiskTier, number>;
  data.forEach((a) => counts[a.risk_tier]++);
  const needsAttention = counts.Critical + counts.Watch;
  const fleetTier: RiskTier = avgSoh >= 78 ? "Healthy" : avgSoh >= 70 ? "Watch" : "Critical";
  const ts = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar liveTimestamp={ts} />

      <main className="mx-auto max-w-[1200px] px-6 pt-12 pb-8">
        <p className="eyebrow">Fleet Overview</p>
        <h1 className="mt-2 text-[32px] font-bold leading-tight tracking-tight sm:text-[36px]">
          Fleet Battery Health
        </h1>
        <p className="mt-3 max-w-[640px] text-[15px] text-text-secondary">
          Live state-of-health, remaining useful life, and risk tier across every monitored EV battery in the fleet.
        </p>

        {/* Hero stat row */}
        <section className="mt-10 grid gap-6 md:grid-cols-3">
          <HeroStatCard
            label="Fleet average SoH"
            value={`${avgSoh.toFixed(1)}%`}
            badge={<RiskBadge tier={fleetTier} />}
            caption="Weighted mean across all monitored assets"
          />
          <HeroStatCard
            label="Assets monitored"
            value={String(data.length)}
            caption={
              <span className="flex flex-wrap items-center gap-x-3 gap-y-1">
                <BreakdownDot color="bg-healthy" label={`${counts.Healthy} Healthy`} />
                <BreakdownDot color="bg-watch" label={`${counts.Watch} Watch`} />
                <BreakdownDot color="bg-critical" label={`${counts.Critical} Critical`} />
              </span>
            }
          />
          <HeroStatCard
            label="Needs attention"
            value={String(needsAttention)}
            valueTone={needsAttention > 0 ? "critical" : "healthy"}
            caption={
              needsAttention > 0
                ? `${counts.Critical} critical, ${counts.Watch} on watch`
                : "All assets within tolerance"
            }
          />
        </section>

        {/* Heatmap */}
        <section className="mt-16">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 className="text-[22px] font-semibold">Fleet Health Heatmap</h2>
              <p className="mt-1 text-[13px] text-text-secondary">Ranked by risk tier — Critical first.</p>
            </div>
          </div>

          <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {sorted.map((a) => (
              <HeatmapCard key={a.id} asset={a} />
            ))}
          </div>
        </section>

        {/* Full list table */}
        <section className="mt-16">
          <h2 className="text-[22px] font-semibold">All Assets</h2>
          <p className="mt-1 text-[13px] text-text-secondary">
            Full fleet inventory with SoH, RUL, and confidence detail.
          </p>

          <div className="mt-6 overflow-hidden rounded-xl border border-border-subtle bg-panel">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-left">
                <thead>
                  <tr className="border-b border-border-subtle">
                    {["Asset ID", "SoH %", "Risk Tier", "RUL (cycles)", "Confidence", "Last Cycle", ""].map((h) => (
                      <th
                        key={h}
                        className="px-5 py-3 text-[11px] font-semibold uppercase tracking-[0.08em] text-text-tertiary"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((a) => (
                    <tr
                      key={a.id}
                      className="group border-b border-border-subtle last:border-b-0 transition-colors hover:bg-panel-raised"
                    >
                      <td className="px-5 py-4">
                        <Link
                          to="/assets/$id"
                          params={{ id: a.id }}
                          className="mono text-[14px] font-medium text-text-primary hover:text-accent"
                        >
                          {a.id}
                        </Link>
                        <div className="text-[12px] text-text-tertiary">{a.name}</div>
                      </td>
                      <td className="mono px-5 py-4 text-[15px]">{a.soh.toFixed(1)}%</td>
                      <td className="px-5 py-4"><RiskBadge tier={a.risk_tier} /></td>
                      <td className="mono px-5 py-4 text-[15px] text-text-secondary">{a.rul_cycles}</td>
                      <td className="px-5 py-4">
                        <ConfidenceLabel level={a.confidence_level} band={a.confidence_band} />
                      </td>
                      <td className="mono px-5 py-4 text-[13px] text-text-tertiary">#{a.last_cycle}</td>
                      <td className="px-5 py-4 text-right">
                        <Link
                          to="/assets/$id"
                          params={{ id: a.id }}
                          className="inline-flex items-center gap-1 text-[13px] text-text-secondary transition-colors group-hover:text-accent"
                          aria-label={`Open ${a.id}`}
                        >
                          <span>Open</span>
                          <span aria-hidden>→</span>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>

      <Footer condensed />
    </div>
  );
}

function HeroStatCard({
  label,
  value,
  badge,
  caption,
  valueTone,
}: {
  label: string;
  value: string;
  badge?: React.ReactNode;
  caption: React.ReactNode;
  valueTone?: "healthy" | "critical";
}) {
  const tone =
    valueTone === "critical" ? "text-critical" : valueTone === "healthy" ? "text-healthy" : "text-text-primary";
  return (
    <div className="rounded-xl border border-border-subtle bg-panel p-6">
      <div className="flex items-start justify-between gap-3">
        <p className="eyebrow">{label}</p>
        {badge}
      </div>
      <p className={`mono mt-4 text-[52px] font-semibold leading-none tracking-tight ${tone}`}>{value}</p>
      <div className="mt-4 text-[13px] text-text-secondary">{caption}</div>
    </div>
  );
}

function BreakdownDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`h-1.5 w-1.5 rounded-full ${color}`} />
      <span className="text-text-secondary">{label}</span>
    </span>
  );
}

function HeatmapCard({ asset }: { asset: AssetHealth }) {
  const stroke =
    asset.risk_tier === "Critical" ? "var(--critical)" : asset.risk_tier === "Watch" ? "var(--watch)" : "var(--accent)";
  const spark = asset.history.slice(-15);
  return (
    <Link
      to="/assets/$id"
      params={{ id: asset.id }}
      className="group flex flex-col rounded-xl border border-border-subtle bg-panel p-5 transition-colors hover:border-accent"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="eyebrow">Asset</p>
          <h3 className="mt-1 truncate text-[16px] font-semibold">{asset.id}</h3>
        </div>
        <RiskBadge tier={asset.risk_tier} />
      </div>

      <p className="mono mt-4 text-[32px] font-semibold leading-none tracking-tight text-text-primary">
        {asset.soh.toFixed(1)}%
      </p>
      <p className="mt-2 text-[13px] text-text-secondary">
        RUL ≈ <span className="mono text-text-primary">{asset.rul_cycles}</span> cycles
      </p>

      <div className="mt-4 flex items-end justify-between">
        <Sparkline data={spark} stroke={stroke} />
        <span className="text-[11px] text-text-tertiary mono">#{asset.last_cycle}</span>
      </div>
    </Link>
  );
}

function ConfidenceLabel({
  level,
  band,
}: {
  level: "asset_specific" | "low_population_estimate";
  band: number;
}) {
  const isAsset = level === "asset_specific";
  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex h-5 w-5 items-center justify-center rounded-full ${
          isAsset ? "bg-healthy-bg text-healthy" : "bg-watch-bg text-watch"
        }`}
        aria-hidden
      >
        {isAsset ? (
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 5.5l2 2 4-5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : (
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M5 2v3.5M5 7.5v.6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
        )}
      </span>
      <div className="text-[13px]">
        <div className={isAsset ? "text-text-primary" : "text-watch"}>
          {isAsset ? "Asset-specific" : "Population estimate"}
        </div>
        <div className="mono text-[11px] text-text-tertiary">± {band.toFixed(1)}%</div>
      </div>
    </div>
  );
}
