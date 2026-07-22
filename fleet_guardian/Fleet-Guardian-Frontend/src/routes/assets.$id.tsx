import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useSuspenseQuery, useQuery, queryOptions } from "@tanstack/react-query";
import { useState } from "react";
import { getAssetHealth, getAssetRecommendation, type AssetHealth } from "@/lib/api";
import { RiskBadge } from "@/components/RiskBadge";
import { TrajectoryChart } from "@/components/TrajectoryChart";
import { Navbar, Footer } from "@/components/Chrome";

const healthQuery = (id: string) =>
  queryOptions({
    queryKey: ["health", id],
    queryFn: async () => {
      try {
        return await getAssetHealth(id);
      } catch {
        throw notFound();
      }
    },
    staleTime: 30_000,
  });

const recommendationQuery = (id: string) =>
  queryOptions({
    queryKey: ["recommendation", id],
    queryFn: () => getAssetRecommendation(id),
    staleTime: 60_000,
    retry: 0,
  });

export const Route = createFileRoute("/assets/$id")({
  loader: ({ context, params }) => context.queryClient.ensureQueryData(healthQuery(params.id)),
  component: AssetDetail,
  pendingComponent: () => (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <div className="mx-auto max-w-[1200px] px-6 py-16">
        <div className="skeleton h-4 w-32" />
        <div className="mt-6 skeleton h-16 w-96" />
        <div className="mt-8 skeleton h-40" />
      </div>
    </div>
  ),
  notFoundComponent: () => (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <div className="mx-auto max-w-[720px] px-6 py-24 text-center">
        <p className="eyebrow">Not Found</p>
        <h1 className="mt-2 text-[32px] font-bold">Asset not found</h1>
        <p className="mt-3 text-text-secondary">The asset you're looking for isn't in the fleet.</p>
        <Link to="/" className="mt-6 inline-block rounded-md bg-accent px-5 py-2.5 text-[14px] font-semibold text-canvas hover:bg-accent-hover">
          Back to Fleet
        </Link>
      </div>
    </div>
  ),
  errorComponent: ({ error }) => (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <div className="mx-auto max-w-[720px] px-6 py-24 text-center">
        <p className="eyebrow">Error</p>
        <h1 className="mt-2 text-[32px] font-bold">Something went wrong</h1>
        <p className="mt-3 text-text-secondary">{error.message}</p>
      </div>
    </div>
  ),
});

function AssetDetail() {
  const { id } = Route.useParams();
  const { data: asset } = useSuspenseQuery(healthQuery(id));
  const ts = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar liveTimestamp={ts} />

      <div className="border-b border-border-subtle">
        <div className="mx-auto max-w-[1200px] px-6 py-3">
          <Link to="/" className="inline-flex items-center gap-1.5 text-[13px] text-text-secondary hover:text-text-primary">
            <span aria-hidden>←</span> Back to Fleet
          </Link>
        </div>
      </div>

      <main className="mx-auto max-w-[1200px] px-6 pt-10 pb-8">
        {/* Hero */}
        <p className="eyebrow">Asset · <span className="mono normal-case tracking-normal text-text-secondary">{asset.id}</span></p>
        <div className="mt-2 grid grid-cols-[minmax(0,1fr)_auto] items-start gap-4 sm:flex sm:flex-wrap sm:items-center sm:justify-between">
          <h1 className="min-w-0 truncate text-[32px] font-bold tracking-tight sm:text-[36px]">{asset.name}</h1>
          <div className="shrink-0"><RiskBadge tier={asset.risk_tier} size="lg" /></div>
        </div>

        <div className="mt-8 rounded-xl border border-border-subtle bg-panel p-6 sm:p-8">
          <p className="eyebrow">State of Health</p>
          <p
            className="mono mt-3 font-semibold tracking-tight leading-none text-text-primary"
            style={{ fontSize: "clamp(56px, 10vw, 72px)", letterSpacing: "-0.02em" }}
          >
            {asset.soh.toFixed(1)}%
          </p>
          <p className="mt-5 text-[15px] text-text-secondary">
            RUL ≈ <span className="mono text-text-primary">{asset.rul_cycles}</span> cycles ·{" "}
            Confidence:{" "}
            <span className={asset.confidence_level === "asset_specific" ? "text-text-primary" : "text-watch"}>
              {asset.confidence_level === "asset_specific" ? "asset-specific" : "population estimate"}
            </span>
          </p>

          {asset.confidence_level === "low_population_estimate" && (
            <div className="mt-4 inline-flex items-start gap-2 rounded-md border border-watch/25 bg-watch-bg px-3 py-2 text-[13px] text-watch">
              <span aria-hidden className="mt-0.5">⚠</span>
              <span>Fewer than 10 recorded cycles — using fleet-wide fallback estimate.</span>
            </div>
          )}
        </div>

        {/* Chart */}
        <section className="mt-12">
          <h2 className="text-[22px] font-semibold">Capacity Fade Trajectory</h2>
          <p className="mt-1 text-[13px] text-text-secondary">
            Actual capacity history with projected fade to the 70% end-of-life threshold.
          </p>

          <div className="mt-6 rounded-xl border border-border-subtle bg-panel p-6">
            <TrajectoryChart history={asset.history} slope={asset.slope_blend} />
            <div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2 text-[12px] text-text-secondary">
              <LegendItem swatch={<span className="inline-block h-0.5 w-6 bg-accent" />} label="Actual capacity" />
              <LegendItem
                swatch={
                  <svg width="24" height="4" aria-hidden>
                    <line x1="0" y1="2" x2="24" y2="2" stroke="var(--text-tertiary)" strokeWidth="2" strokeDasharray="4 4" />
                  </svg>
                }
                label="Projected fade"
              />
              <LegendItem
                swatch={
                  <svg width="24" height="4" aria-hidden>
                    <line x1="0" y1="2" x2="24" y2="2" stroke="var(--critical)" strokeWidth="2" strokeDasharray="6 5" />
                  </svg>
                }
                label="70% end-of-life threshold"
              />
            </div>
          </div>
        </section>

        {/* Risk & Confidence tiles */}
        <section className="mt-12">
          <h2 className="text-[22px] font-semibold">Risk &amp; Confidence Detail</h2>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatTile label="SoH current" value={`${asset.soh.toFixed(1)}%`} />
            <StatTile label="RUL (cycles)" value={String(asset.rul_cycles)} />
            <StatTile label="Confidence band" value={`± ${asset.confidence_band.toFixed(1)}%`} />
            <StatTile label="Slope (SoH / cycle)" value={asset.slope_blend.toFixed(3)} tone="critical" />
          </div>
        </section>

        {/* Anomaly flags */}
        <section className="mt-12">
          <h2 className="text-[22px] font-semibold">Active Anomaly Flags</h2>
          <div className="mt-6 rounded-xl border border-border-subtle bg-panel p-6">
            {asset.anomaly_flags.length === 0 ? (
              <div className="flex items-center gap-3 text-[14px] text-text-secondary">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-healthy-bg text-healthy">
                  <svg width="12" height="12" viewBox="0 0 10 10" fill="none">
                    <path d="M2 5.5l2 2 4-5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
                No active anomaly flags — sensor telemetry within nominal bands.
              </div>
            ) : (
              <ul className="divide-y divide-border-subtle">
                {asset.anomaly_flags.map((f) => (
                  <li key={f.type} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
                    <span
                      className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${
                        f.severity === "critical" ? "bg-critical" : "bg-watch"
                      }`}
                    />
                    <div className="min-w-0">
                      <p className={`text-[14px] font-semibold ${f.severity === "critical" ? "text-critical" : "text-watch"}`}>
                        {f.label}
                      </p>
                      <p className="mt-0.5 text-[13px] text-text-secondary">{f.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        {/* Explainability panel */}
        <ExplainabilityPanel asset={asset} />
      </main>

      <Footer condensed />
    </div>
  );
}

function StatTile({ label, value, tone }: { label: string; value: string; tone?: "critical" | "healthy" }) {
  const c = tone === "critical" ? "text-critical" : tone === "healthy" ? "text-healthy" : "text-text-primary";
  return (
    <div className="rounded-xl border border-border-subtle bg-panel p-5">
      <p className="eyebrow">{label}</p>
      <p className={`mono mt-3 text-[28px] font-semibold leading-none tracking-tight ${c}`}>{value}</p>
    </div>
  );
}

function LegendItem({ swatch, label }: { swatch: React.ReactNode; label: string }) {
  return (
    <span className="inline-flex items-center gap-2">
      {swatch}
      <span>{label}</span>
    </span>
  );
}

function ExplainabilityPanel({ asset }: { asset: AssetHealth }) {
  const { data: rec, isLoading, isError } = useQuery(recommendationQuery(asset.id));
  const [showWeights, setShowWeights] = useState(false);

  return (
    <section className="mt-12">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-[22px] font-semibold">What the Agent Sees</h2>
        <p className="text-[12px] text-text-tertiary">AI-generated explanation · Groq</p>
      </div>

      <div className="mt-4 rounded-xl bg-panel-raised p-6 sm:p-8" style={{ borderLeft: "4px solid var(--accent)" }}>
        {isLoading && (
          <div className="space-y-3">
            <div className="skeleton h-4 w-24" />
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-[92%]" />
            <div className="mt-4 skeleton h-4 w-28" />
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-[88%]" />
          </div>
        )}

        {isError && !isLoading && (
          <p className="text-[14px] text-text-secondary">
            Explanation unavailable right now — the numeric health data above is unaffected.
          </p>
        )}

        {rec && !isLoading && (
          <div className="space-y-5 text-[15px] leading-[1.65] text-text-primary">
            <div>
              <h3 className="mb-1.5 text-[13px] font-semibold uppercase tracking-[0.06em] text-accent">Diagnosis</h3>
              <p>{rec.diagnosis}</p>
            </div>
            <div>
              <h3 className="mb-1.5 text-[13px] font-semibold uppercase tracking-[0.06em] text-accent">Likely Cause</h3>
              <p>{rec.likely_cause}</p>
            </div>
            <div>
              <h3 className="mb-1.5 text-[13px] font-semibold uppercase tracking-[0.06em] text-accent">Recommended Action</h3>
              <p>{rec.recommended_action}</p>
            </div>
          </div>
        )}

        <div className="mt-6 border-t border-border-subtle pt-4">
          <button
            type="button"
            onClick={() => setShowWeights((v) => !v)}
            className="inline-flex items-center gap-2 text-[13px] font-semibold text-text-secondary transition-colors hover:text-text-primary"
            aria-expanded={showWeights}
          >
            <span
              aria-hidden
              className="inline-block transition-transform"
              style={{ transform: showWeights ? "rotate(90deg)" : "rotate(0deg)" }}
            >
              ▸
            </span>
            {showWeights ? "Hide rule weights" : "Show rule weights"}
          </button>

          {showWeights && (
            <dl className="mono mt-4 grid grid-cols-1 gap-x-8 gap-y-2 text-[13px] sm:grid-cols-2">
              <WeightRow k="slope_short" v={asset.slope_short.toFixed(4)} />
              <WeightRow k="slope_long" v={asset.slope_long.toFixed(4)} />
              <WeightRow k="slope_blend" v={asset.slope_blend.toFixed(4)} />
              <WeightRow k="blend_weight_short" v={asset.blend_weight_short.toFixed(2)} />
              <WeightRow k="blend_weight_long" v={asset.blend_weight_long.toFixed(2)} />
              <WeightRow k="thermal_factor" v={asset.thermal_factor.toFixed(3)} />
              <WeightRow k="dod_factor" v={asset.dod_factor.toFixed(3)} />
              <WeightRow k="confidence_band" v={`± ${asset.confidence_band.toFixed(2)}%`} />
            </dl>
          )}
        </div>
      </div>
    </section>
  );
}

function WeightRow({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-border-subtle/60 pb-1.5">
      <dt className="text-text-tertiary">{k}</dt>
      <dd className="text-text-primary">{v}</dd>
    </div>
  );
}
