import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
  children: ReactNode;
};

export const UButton = forwardRef<HTMLButtonElement, Props>(function UButton(
  { className, variant = "primary", children, ...rest },
  ref,
) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-full px-7 py-3.5 text-[15px] font-medium transition-all duration-200 ease-out active:scale-[0.98]";
  const styles =
    variant === "primary"
      ? "text-white hover:scale-[1.02]"
      : "text-[color:var(--color-text-primary)] hover:scale-[1.02]";
  const inline =
    variant === "primary"
      ? {
          background: "#5b5fed",
          boxShadow: "0 0 0 rgba(91,95,237,0)",
        }
      : {
          background: "transparent",
          border: "1px solid rgba(255,255,255,0.15)",
        };
  return (
    <button
      ref={ref}
      className={cn(base, styles, className)}
      style={inline}
      onMouseEnter={(e) => {
        if (variant === "primary") {
          e.currentTarget.style.background = "#7b7fff";
          e.currentTarget.style.boxShadow = "0 0 24px rgba(91,95,237,0.45)";
        } else {
          e.currentTarget.style.borderColor = "rgba(255,255,255,0.35)";
        }
      }}
      onMouseLeave={(e) => {
        if (variant === "primary") {
          e.currentTarget.style.background = "#5b5fed";
          e.currentTarget.style.boxShadow = "0 0 0 rgba(91,95,237,0)";
        } else {
          e.currentTarget.style.borderColor = "rgba(255,255,255,0.15)";
        }
      }}
      {...rest}
    >
      {children}
    </button>
  );
});
