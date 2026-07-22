import { createFileRoute, Link } from "@tanstack/react-router";
import { Navbar, Footer } from "@/components/Chrome";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About · EV Fleet APM" },
      {
        name: "description",
        content:
          "How the EV Fleet APM dashboard estimates battery state of health, remaining useful life, and risk tier using dual-window slope extrapolation on NASA battery data.",
      },
      { property: "og:title", content: "About · EV Fleet APM" },
      {
        property: "og:description",
        content: "Data sources, RUL methodology, and confidence model behind the EV Fleet APM dashboard.",
      },
    ],
  }),
  component: About,
});

function About() {
  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />

      <main className="mx-auto max-w-[720px] px-6 pt-16 pb-8">
        <p className="eyebrow">About</p>
        <h1 className="mt-2 text-[32px] font-bold tracking-tight sm:text-[36px]">About This Dashboard</h1>

        <div className="mt-6 space-y-5 text-[15px] leading-[1.7] text-text-secondary">
          <p>
            <span className="text-text-primary">EV Fleet APM</span> is the operator-facing view for a Battery Asset
            Performance Management agent that monitors industrial EV batteries — the packs powering freight, mining,
            and intra-plant logistics vehicles. It answers one question at a glance:{" "}
            <span className="text-text-primary">which vehicle needs attention today, and why?</span>
          </p>
          <p>
            Remaining useful life is estimated deterministically. For each asset we compute two capacity-fade slopes:
            a short-window slope over the most recent cycles, and a long-window slope across the full history. These
            are blended and extrapolated forward until the projected state of health crosses the 70% end-of-life
            threshold. The result is a cycle count — no black-box regression, no opaque neural network scoring the
            operator can't audit.
          </p>
          <p>
            The narrative explanations on each asset page come from a Groq-hosted large language model that reads the
            same numeric features the risk tier is derived from. The AI layer is presentational — it explains the
            deterministic scoring in plain language. If the model call fails, the numeric health data continues to
            render unaffected.
          </p>
          <p>
            The demo runs against the{" "}
            <span className="text-text-primary">NASA Battery Degradation Dataset</span>, a well-known set of
            accelerated-aging discharge cycles collected at the NASA Prognostics Center of Excellence.
          </p>
        </div>

        <div className="mt-10 rounded-xl border border-border-subtle bg-panel p-6">
          <p className="eyebrow">Methodology</p>
          <h2 className="mt-2 text-[18px] font-semibold">How confidence works</h2>
          <p className="mt-3 text-[14px] leading-[1.65] text-text-secondary">
            When an asset has enough recorded cycles to fit its own slope reliably, we report{" "}
            <span className="text-text-primary">asset-specific</span> confidence with a tight ± band derived from the
            residuals of its own trajectory. When cycle history is thin (typically under ten cycles), we fall back to
            a <span className="text-watch">population estimate</span> — the median slope across the fleet — and widen
            the confidence band accordingly. Both cases surface the same fields; the confidence label tells you which
            regime is in effect.
          </p>
        </div>

        <div className="mt-8 rounded-xl border border-border-subtle bg-panel p-6">
          <p className="eyebrow">Scope</p>
          <h2 className="mt-2 text-[18px] font-semibold">What this build is (and isn't)</h2>
          <p className="mt-3 text-[14px] leading-[1.65] text-text-secondary">
            This is a focused hackathon demo — three screens, one agent, no login. The wider platform envisions
            additional agents for fleet electrification readiness, EV supply chain risk, and net-zero tracking; none
            of those are wired here. What you see on the Dashboard and Asset pages is the full surface area of the
            APM agent.
          </p>
        </div>

        <div className="mt-10 flex flex-wrap items-center gap-3">
          <Link
            to="/"
            className="inline-flex items-center rounded-md bg-accent px-5 py-2.5 text-[14px] font-semibold text-canvas transition-colors hover:bg-accent-hover"
          >
            View Fleet Dashboard
          </Link>
          <span className="inline-flex items-center gap-2 rounded-full border border-border-subtle bg-panel px-3 py-1.5 text-[12px] text-text-tertiary">
            <span className="h-1.5 w-1.5 rounded-full bg-healthy" />
            Backend verified &amp; tested
          </span>
        </div>
      </main>

      <Footer />
    </div>
  );
}
