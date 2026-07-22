import type { ReactNode } from "react";

type Tone = "healthy" | "watch" | "critical" | "neutral" | "accent";

const TONE: Record<Tone, string> = {
  healthy: "#34d399",
  watch: "#fbbf24",
  critical: "#f87171",
  neutral: "#9a9aa8",
  accent: "#5b5fed",
};

export function StatusPill({
  tone = "neutral",
  children,
  dot = true,
}: {
  tone?: Tone;
  children: ReactNode;
  dot?: boolean;
}) {
  const color = TONE[tone];
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider"
      style={{
        background: `color-mix(in oklab, ${color} 12%, transparent)`,
        color,
      }}
    >
      {dot && (
        <span
          className="inline-block h-1.5 w-1.5 rounded-full"
          style={{ background: color }}
        />
      )}
      {children}
    </span>
  );
}
