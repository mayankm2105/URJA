import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  ShieldCheck,
  Truck,
  Leaf,
  Activity,
  Boxes,
  Battery,
  Zap,
  Route as RouteIcon,
} from "lucide-react";
import { AmbientOrbs } from "@/components/urja/AmbientOrbs";
import { GlassCard } from "@/components/urja/GlassCard";
import { StatCard } from "@/components/urja/StatCard";
import { UButton } from "@/components/urja/UButton";
import { PLATFORM_STATS } from "@/lib/urja-mock";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Urja — Industrial EV Intelligence" },
      {
        name: "description",
        content:
          "One command platform unifying supply chain, fleet, carbon, and battery health intelligence for industrial EVs.",
      },
    ],
  }),
  component: Home,
});

const AGENTS = [
  {
    name: "CellSentry",
    href: "/cellsentry" as const,
    icon: ShieldCheck,
    line: "Supply chain risk and traceability across battery materials.",
    tags: ["Supply Chain", "Cell Quality"],
  },
  {
    name: "FleetMind",
    href: "/fleetmind" as const,
    icon: Truck,
    line: "Diesel-to-electric transition planning and procurement.",
    tags: ["Electrify", "Readiness Index"],
  },
  {
    name: "CarbonPulse",
    href: "/carbonpulse" as const,
    icon: Leaf,
    line: "Scope 1/3 accounting versus SBTi with route analytics.",
    tags: ["Net Zero", "Does It Work", "Battery Proof"],
  },
  {
    name: "Fleet Guardian",
    href: "/fleet-guardian" as const,
    icon: Activity,
    line: "Cycle-level RUL, anomaly detection, LLM maintenance reasoning.",
    tags: ["Fleet Health", "Asset Guardian", "Depot Charging"],
  },
];

const FLOW = [
  { label: "Supply", agent: "CellSentry", icon: Boxes },
  { label: "Assets", agent: "Fleet Guardian", icon: Battery },
  { label: "Electrify", agent: "FleetMind", icon: Zap },
  { label: "Carbon", agent: "CarbonPulse", icon: Leaf },
];

function Home() {
  return (
    <div className="relative">
      {/* HERO */}
      <section className="relative flex min-h-[92vh] items-center overflow-hidden pt-24">
        <AmbientOrbs variant="hero" />
        <div className="relative mx-auto max-w-[1280px] px-6 text-center">
          <div className="eyebrow fade-up">ET AI Hackathon 2026 · Industrial EV Intelligence</div>
          <h1
            className="fade-up mx-auto mt-6 max-w-4xl text-[44px] font-semibold leading-[1.05] tracking-[-0.02em] md:text-[64px]"
            style={{ animationDelay: "0.05s" }}
          >
            One command platform for the industrial{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #7b7fff 0%, #3e8ef7 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              EV lifecycle.
            </span>
          </h1>
          <p
            className="fade-up mx-auto mt-6 max-w-2xl text-[18px] leading-[1.6] text-[color:var(--color-text-secondary)]"
            style={{ animationDelay: "0.1s" }}
          >
            Urja unifies four specialised agents — supply chain risk, fleet
            electrification, carbon accounting, and battery health — into a single
            operating layer for net-zero industrial fleets.
          </p>
          <div
            className="fade-up mt-10 flex flex-wrap items-center justify-center gap-3"
            style={{ animationDelay: "0.15s" }}
          >
            <Link to="/command-center">
              <UButton>
                Enter Command Center <ArrowRight className="h-4 w-4" />
              </UButton>
            </Link>
            <a href="#agents">
              <UButton variant="secondary">Explore the Agents</UButton>
            </a>
          </div>
        </div>
      </section>

      {/* STAT STRIP */}
      <section className="relative mx-auto max-w-[1280px] px-6 py-24">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Assets Monitored" value={PLATFORM_STATS.assetsMonitored} />
          <StatCard
            label="Fleet Average SoH"
            value={PLATFORM_STATS.fleetAvgSoH}
            suffix="%"
            decimals={1}
            status={{ tone: "healthy", label: "Healthy" }}
          />
          <StatCard
            label="Tonnes CO₂ Tracked"
            value={PLATFORM_STATS.tonnesCO2Tracked}
            hint="Scope 1 + 3"
          />
          <StatCard
            label="Supply Chain Nodes"
            value={PLATFORM_STATS.supplyChainNodes}
            hint="34 edges monitored"
          />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="relative mx-auto max-w-[1280px] px-6 py-24">
        <div className="mb-14 max-w-2xl">
          <div className="eyebrow">How Urja works</div>
          <h2 className="mt-3 text-[32px] font-semibold leading-[1.1] tracking-[-0.01em] md:text-[40px]">
            Supply · Assets · Buying · Carbon.
          </h2>
          <p className="mt-4 text-[17px] text-[color:var(--color-text-secondary)]">
            A continuous loop. Signals from every stage feed the next — and every
            action rolls up to the net-zero target.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {FLOW.map((step, i) => {
            const Icon = step.icon;
            return (
              <div key={step.label} className="relative">
                <GlassCard>
                  <div
                    className="mb-4 flex h-10 w-10 items-center justify-center rounded-[10px]"
                    style={{
                      background: "rgba(91,95,237,0.14)",
                      color: "#7b7fff",
                    }}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="eyebrow">Step {i + 1}</div>
                  <div className="mt-2 text-[22px] font-semibold">{step.label}</div>
                  <div className="mt-2 text-[13px] text-[color:var(--color-text-secondary)]">
                    Powered by {step.agent}
                  </div>
                </GlassCard>
                {i < FLOW.length - 1 && (
                  <div className="pointer-events-none absolute right-[-14px] top-1/2 z-10 hidden -translate-y-1/2 md:block">
                    <ArrowRight className="h-5 w-5 text-[color:var(--color-text-tertiary)]" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* AGENTS */}
      <section id="agents" className="relative mx-auto max-w-[1280px] px-6 py-24">
        <div className="mb-14 max-w-2xl">
          <div className="eyebrow">Four Agents · One Platform</div>
          <h2 className="mt-3 text-[32px] font-semibold leading-[1.1] tracking-[-0.01em] md:text-[40px]">
            Specialised intelligence, unified surface.
          </h2>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {AGENTS.map((a) => {
            const Icon = a.icon;
            return (
              <Link key={a.name} to={a.href} className="group block">
                <GlassCard className="glass-hover h-full transition-all group-hover:scale-[1.01]">
                  <div className="flex items-start justify-between">
                    <div
                      className="flex h-12 w-12 items-center justify-center rounded-[12px]"
                      style={{
                        background: "linear-gradient(135deg, rgba(91,95,237,0.2), rgba(62,142,247,0.15))",
                        color: "#7b7fff",
                      }}
                    >
                      <Icon className="h-6 w-6" />
                    </div>
                    <ArrowRight className="h-5 w-5 text-[color:var(--color-text-tertiary)] transition-transform group-hover:translate-x-1 group-hover:text-[color:var(--color-text-primary)]" />
                  </div>
                  <h3 className="mt-6 text-[22px] font-semibold">{a.name}</h3>
                  <p className="mt-2 text-[15px] leading-[1.55] text-[color:var(--color-text-secondary)]">
                    {a.line}
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    {a.tags.map((t) => (
                      <span
                        key={t}
                        className="rounded-full border border-white/10 px-2.5 py-1 text-[11px] uppercase tracking-wider text-[color:var(--color-text-secondary)]"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </GlassCard>
              </Link>
            );
          })}
        </div>
      </section>

      {/* CLOSING CTA */}
      <section className="relative mx-auto max-w-[1280px] px-6 py-24">
        <div className="relative overflow-hidden rounded-[24px]">
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(135deg, rgba(91,95,237,0.22) 0%, rgba(62,142,247,0.18) 50%, transparent 100%)",
            }}
          />
          <GlassCard className="relative">
            <div className="flex flex-col items-start justify-between gap-8 md:flex-row md:items-center">
              <div className="max-w-xl">
                <div className="eyebrow">Ready</div>
                <h2 className="mt-2 text-[28px] font-semibold leading-[1.15] tracking-[-0.01em] md:text-[36px]">
                  See every risk, asset, and tonne of CO₂ in one view.
                </h2>
              </div>
              <Link to="/command-center">
                <UButton>
                  Open Command Center <ArrowRight className="h-4 w-4" />
                </UButton>
              </Link>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative border-t border-white/5 py-10">
        <div className="mx-auto flex max-w-[1280px] flex-col items-start justify-between gap-6 px-6 md:flex-row md:items-center">
          <div className="flex items-center gap-2">
            <span
              className="flex h-7 w-7 items-center justify-center rounded-lg"
              style={{ background: "linear-gradient(135deg, #5b5fed, #3e8ef7)" }}
            >
              <RouteIcon className="h-3.5 w-3.5 text-white" />
            </span>
            <span className="text-[14px] font-semibold">Urja</span>
          </div>
          <nav className="flex flex-wrap gap-x-5 gap-y-2 text-[13px] text-[color:var(--color-text-secondary)]">
            <Link to="/command-center">Command Center</Link>
            <Link to="/chat">Chatbot</Link>
            <Link to="/cellsentry">CellSentry</Link>
            <Link to="/fleetmind">FleetMind</Link>
            <Link to="/carbonpulse">CarbonPulse</Link>
            <Link to="/fleet-guardian">Fleet Guardian</Link>
          </nav>
          <div className="text-[12px] text-[color:var(--color-text-tertiary)]">
            Built for ET AI Hackathon 2026 · PS3
          </div>
        </div>
      </footer>
    </div>
  );
}
