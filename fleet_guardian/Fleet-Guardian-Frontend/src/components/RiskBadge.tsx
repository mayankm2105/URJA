import type { RiskTier } from "@/lib/api";

export function RiskBadge({ tier, size = "sm" }: { tier: RiskTier; size?: "sm" | "lg" }) {
  const map = {
    Healthy: { fg: "text-healthy", bg: "bg-healthy-bg", dot: "bg-healthy" },
    Watch: { fg: "text-watch", bg: "bg-watch-bg", dot: "bg-watch" },
    Critical: { fg: "text-critical", bg: "bg-critical-bg", dot: "bg-critical" },
  }[tier];
  const pad = size === "lg" ? "px-4 py-1.5 text-[13px]" : "px-3 py-1 text-[12px]";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full ${pad} font-semibold uppercase tracking-[0.06em] ${map.bg} ${map.fg}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${map.dot}`} />
      {tier}
    </span>
  );
}
