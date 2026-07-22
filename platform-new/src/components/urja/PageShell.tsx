import type { ReactNode } from "react";
import { AmbientOrbs } from "./AmbientOrbs";

export function PageShell({
  children,
  orbs = "subtle",
}: {
  children: ReactNode;
  orbs?: "hero" | "subtle" | "none";
}) {
  return (
    <div className="relative min-h-screen pt-[72px]">
      {orbs !== "none" && <AmbientOrbs variant={orbs === "hero" ? "hero" : "subtle"} />}
      <div className="relative">{children}</div>
    </div>
  );
}

export function PageHeader({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="fade-up mb-10 max-w-3xl">
      <div className="eyebrow mb-3">{eyebrow}</div>
      <h1
        className="text-[40px] font-semibold leading-[1.1] tracking-[-0.01em] md:text-[48px]"
      >
        {title}
      </h1>
      {subtitle && (
        <p className="mt-4 text-[17px] leading-[1.6] text-[color:var(--color-text-secondary)]">
          {subtitle}
        </p>
      )}
    </div>
  );
}
