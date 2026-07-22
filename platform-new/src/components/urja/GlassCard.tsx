import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function GlassCard({
  className,
  children,
  padding = "lg",
  ...rest
}: HTMLAttributes<HTMLDivElement> & { children: ReactNode; padding?: "sm" | "md" | "lg" }) {
  const pad = padding === "lg" ? "p-6 md:p-8" : padding === "md" ? "p-5 md:p-6" : "p-4";
  return (
    <div
      className={cn(
        "glass relative overflow-hidden rounded-[20px]",
        pad,
        className,
      )}
      {...rest}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px"
        style={{
          background:
            "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%)",
        }}
      />
      {children}
    </div>
  );
}
