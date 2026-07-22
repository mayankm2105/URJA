import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Zap } from "lucide-react";

const NAV = [
  { to: "/", label: "Home" },
  { to: "/command-center", label: "Command Center" },
  { to: "/chat", label: "Chatbot" },
  { to: "/cellsentry", label: "CellSentry" },
  { to: "/fleetmind", label: "FleetMind" },
  { to: "/carbonpulse", label: "CarbonPulse" },
  { to: "/fleet-guardian", label: "Fleet Guardian" },
] as const;

export function TopBar() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={{
        height: 72,
        background: scrolled ? "rgba(10,10,15,0.7)" : "transparent",
        backdropFilter: scrolled ? "blur(16px)" : "none",
        borderBottom: scrolled ? "1px solid rgba(255,255,255,0.06)" : "1px solid transparent",
      }}
    >
      <div className="mx-auto flex h-full max-w-[1280px] items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <span
            className="flex h-8 w-8 items-center justify-center rounded-lg"
            style={{
              background: "linear-gradient(135deg, #5b5fed 0%, #3e8ef7 100%)",
              boxShadow: "0 0 20px rgba(91,95,237,0.5)",
            }}
          >
            <Zap className="h-4 w-4 text-white" strokeWidth={2.5} />
          </span>
          <span className="text-[17px] font-semibold tracking-tight">Urja</span>
        </Link>

        <nav className="hidden items-center gap-1 lg:flex">
          {NAV.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="rounded-full px-3 py-1.5 text-[13px] text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
              activeProps={{
                style: {
                  color: "var(--color-text-primary)",
                  background: "rgba(255,255,255,0.06)",
                },
              }}
              activeOptions={{ exact: item.to === "/" }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div
          className="flex items-center gap-2 rounded-full px-3 py-1.5 text-[11px] font-medium uppercase tracking-wider"
          style={{
            background: "color-mix(in oklab, #34d399 12%, transparent)",
            color: "#34d399",
          }}
        >
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#34d399] opacity-60" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-[#34d399]" />
          </span>
          4 Services Live
        </div>
      </div>
    </header>
  );
}
