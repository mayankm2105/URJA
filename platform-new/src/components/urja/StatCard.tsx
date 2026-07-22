import { useEffect, useRef, useState } from "react";
import { GlassCard } from "./GlassCard";
import { StatusPill } from "./StatusPill";

type Props = {
  label: string;
  value: number;
  suffix?: string;
  prefix?: string;
  decimals?: number;
  status?: { tone: "healthy" | "watch" | "critical"; label: string };
  hint?: string;
};

export function StatCard({ label, value, suffix, prefix, decimals = 0, status, hint }: Props) {
  const [display, setDisplay] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    if (!ref.current) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting && !started.current) {
            started.current = true;
            const dur = 1200;
            const start = performance.now();
            const step = (t: number) => {
              const p = Math.min(1, (t - start) / dur);
              const eased = 1 - Math.pow(1 - p, 3);
              setDisplay(value * eased);
              if (p < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
          }
        });
      },
      { threshold: 0.3 },
    );
    io.observe(ref.current);
    return () => io.disconnect();
  }, [value]);

  const formatted =
    decimals > 0
      ? display.toFixed(decimals)
      : Math.round(display).toLocaleString("en-US");

  return (
    <GlassCard padding="md">
      <div ref={ref} className="flex flex-col gap-3">
        <span className="eyebrow">{label}</span>
        <div className="text-stat text-[color:var(--color-text-primary)]">
          {prefix}
          {formatted}
          {suffix && <span className="ml-1 text-[24px] text-[color:var(--color-text-secondary)]">{suffix}</span>}
        </div>
        <div className="flex items-center justify-between">
          {hint && <span className="text-[13px] text-[color:var(--color-text-secondary)]">{hint}</span>}
          {status && <StatusPill tone={status.tone}>{status.label}</StatusPill>}
        </div>
      </div>
    </GlassCard>
  );
}
