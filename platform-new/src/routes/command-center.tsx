import { createFileRoute, Link } from "@tanstack/react-router";
import {
  AlertTriangle,
  ArrowRight,
  ChevronRight,
  Boxes,
  Wrench,
  ShoppingCart,
  Leaf,
} from "lucide-react";
import { GlassCard } from "@/components/urja/GlassCard";
import { StatCard } from "@/components/urja/StatCard";
import { StatusPill } from "@/components/urja/StatusPill";
import { PageShell, PageHeader } from "@/components/urja/PageShell";
import { PLATFORM_STATS, NEWS_EVENTS } from "@/lib/urja-mock";
import { fetchAllActions, type ActionItem } from "@/lib/actions";
import { fetchGuardianSummary } from "@/lib/guardian";
import { fetchFleet } from "@/lib/fleet";
import { fetchCarbonDashboard } from "@/lib/carbon";

export const Route = createFileRoute("/command-center")({
  head: () => ({
    meta: [
      { title: "Command Center — Urja" },
      { name: "description", content: "Unified cross-agent overview for the industrial EV fleet." },
    ],
  }),
  loader: async () => {
    const [actionsRes, guardianRes, fleetRes, carbonRes] = await Promise.allSettled([
      fetchAllActions(),
      fetchGuardianSummary(),
      fetchFleet(),
      fetchCarbonDashboard()
    ]);

    let stats = {
      fleetAvgSoH: PLATFORM_STATS.fleetAvgSoH,
      assetsMonitored: PLATFORM_STATS.assetsMonitored,
      needsAttention: PLATFORM_STATS.needsAttention,
      tonnesCO2Tracked: PLATFORM_STATS.tonnesCO2Tracked
    };

    if (guardianRes.status === "fulfilled") {
      stats.assetsMonitored = guardianRes.value.total_assets;
      stats.needsAttention = guardianRes.value.critical_count;
    }
    if (fleetRes.status === "fulfilled") {
      stats.fleetAvgSoH = fleetRes.value.meta.fleet_soh_avg * 100;
    }
    if (carbonRes.status === "fulfilled") {
      stats.tonnesCO2Tracked = carbonRes.value.scope1_ytd_tons + carbonRes.value.scope3_ytd_tons;
    }

    return {
      actions: actionsRes.status === "fulfilled" ? actionsRes.value : [],
      stats
    };
  },
  component: CommandCenter,
});

const SOURCE_TONE: Record<string, "healthy" | "watch" | "critical" | "accent" | "neutral"> = {
  GUARDIAN: "critical",
  SUPPLY: "watch",
  "NET ZERO": "healthy",
  ELECTRIFY: "accent",
};

const TRACE = [
  { step: 1, label: "Material", desc: "Cobalt · Tier-2 supplier flagged", icon: Boxes },
  { step: 2, label: "Repairs", desc: "3 batteries scheduled this week", icon: Wrench },
  { step: 3, label: "Buying", desc: "14 diesel units ready to swap", icon: ShoppingCart },
  { step: 4, label: "Carbon", desc: "-812 tCO₂ vs baseline", icon: Leaf },
];

function CommandCenter() {
  const { actions, stats } = Route.useLoaderData();

  return (
    <PageShell orbs="subtle">
      <div className="mx-auto max-w-[1280px] px-6 py-16">
        <PageHeader
          eyebrow="Command Center"
          title="The whole picture."
          subtitle="Cross-agent oversight of supply, assets, and carbon — with a prioritised action list rolled up from every agent."
        />

        {/* KPI row */}
        <div className="fade-up grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Fleet Average SoH"
            value={stats.fleetAvgSoH}
            suffix="%"
            decimals={1}
            status={{ tone: "healthy", label: "Healthy" }}
          />
          <StatCard
            label="Assets Monitored"
            value={stats.assetsMonitored}
            hint="1,158 healthy · 89 watch · 37 critical"
          />
          <StatCard
            label="Needs Attention"
            value={stats.needsAttention}
            status={{ tone: "critical", label: "Action" }}
          />
          <StatCard
            label="Tonnes CO₂ Tracked"
            value={stats.tonnesCO2Tracked}
            hint="YTD, Scope 1 + 3"
          />
        </div>

        {/* News strip */}
        <div className="mt-16">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <div className="eyebrow">News → Impact</div>
              <h2 className="mt-2 text-[24px] font-semibold">Signal from the market</h2>
            </div>
          </div>
          <div className="flex snap-x gap-4 overflow-x-auto pb-2">
            {NEWS_EVENTS.map((n) => (
              <GlassCard
                key={n.id}
                padding="md"
                className="w-[320px] shrink-0 snap-start"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[12px] text-[color:var(--color-text-tertiary)]">
                    {n.date}
                  </span>
                  <StatusPill tone={n.severity}>{n.severity}</StatusPill>
                </div>
                <div className="mt-3 text-[15px] font-medium leading-[1.4]">
                  {n.title}
                </div>
                <div className="mt-3 text-[13px] text-[color:var(--color-text-secondary)]">
                  {n.impact}
                </div>
              </GlassCard>
            ))}
          </div>
        </div>

        {/* Trace */}
        <div className="mt-16">
          <div className="mb-4">
            <div className="eyebrow">Material → Carbon target</div>
            <h2 className="mt-2 text-[24px] font-semibold">The four-step trace</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-4">
            {TRACE.map((t, i) => {
              const Icon = t.icon;
              return (
                <div key={t.step} className="relative">
                  <GlassCard padding="md">
                    <div className="flex items-center gap-3">
                      <span
                        className="flex h-8 w-8 items-center justify-center rounded-full text-[13px] font-semibold"
                        style={{ background: "rgba(91,95,237,0.15)", color: "#7b7fff" }}
                      >
                        {t.step}
                      </span>
                      <Icon className="h-5 w-5 text-[color:var(--color-text-secondary)]" />
                    </div>
                    <div className="mt-4 text-[17px] font-semibold">{t.label}</div>
                    <div className="mt-1 text-[13px] text-[color:var(--color-text-secondary)]">
                      {t.desc}
                    </div>
                  </GlassCard>
                  {i < TRACE.length - 1 && (
                    <ArrowRight className="pointer-events-none absolute right-[-14px] top-1/2 z-10 hidden h-5 w-5 -translate-y-1/2 text-[color:var(--color-accent)] md:block" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Action list */}
        <div className="mt-16">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <div className="eyebrow">Prioritised</div>
              <h2 className="mt-2 text-[24px] font-semibold">What to do next</h2>
            </div>
            <Link
              to="/chat"
              className="text-[13px] text-[color:var(--color-text-secondary)] hover:text-[color:var(--color-text-primary)]"
            >
              Ask Urja →
            </Link>
          </div>
          <div className="flex flex-col gap-3">
            {actions.map((a) => (
              <Link to={a.link as any} key={a.id} className="block">
                <GlassCard
                  padding="md"
                  className="glass-hover flex cursor-pointer items-center gap-4 transition-colors"
                >
                <div
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px]"
                  style={{
                    background:
                      a.tone === "critical"
                        ? "rgba(248,113,113,0.14)"
                        : a.tone === "watch"
                          ? "rgba(251,191,36,0.14)"
                          : "rgba(52,211,153,0.14)",
                    color:
                      a.tone === "critical"
                        ? "#f87171"
                        : a.tone === "watch"
                          ? "#fbbf24"
                          : "#34d399",
                  }}
                >
                  <AlertTriangle className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-[15px] font-medium">{a.title}</div>
                  <div className="mt-0.5 truncate text-[13px] text-[color:var(--color-text-secondary)]">
                    {a.desc}
                  </div>
                </div>
                <StatusPill tone={SOURCE_TONE[a.source] ?? "neutral"}>{a.source}</StatusPill>
                <ChevronRight className="h-5 w-5 text-[color:var(--color-text-tertiary)]" />
                </GlassCard>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </PageShell>
  );
}
