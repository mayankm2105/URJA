import { Link } from "@tanstack/react-router";

export function Navbar({ liveTimestamp }: { liveTimestamp?: string }) {
  return (
    <header className="sticky top-0 z-40 h-16 border-b border-border-subtle bg-canvas/95 backdrop-blur">
      <div className="mx-auto flex h-full max-w-[1200px] items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2.5 text-text-primary">
          <span
            aria-hidden
            className="grid h-7 w-7 place-items-center rounded-md"
            style={{ background: "linear-gradient(135deg, var(--accent) 0%, #2563EB 100%)" }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z" fill="#07101D" />
            </svg>
          </span>
          <span className="text-[15px] font-bold tracking-tight">EV Fleet APM</span>
        </Link>

        <nav className="flex items-center gap-6 text-[14px]">
          <Link
            to="/"
            className="text-text-secondary transition-colors hover:text-text-primary [&.active]:text-text-primary"
            activeOptions={{ exact: true }}
            activeProps={{ className: "text-text-primary" }}
          >
            Dashboard
          </Link>
          <Link
            to="/about"
            className="text-text-secondary transition-colors hover:text-text-primary"
            activeProps={{ className: "text-text-primary" }}
          >
            About
          </Link>
          {liveTimestamp && (
            <span className="hidden items-center gap-2 rounded-full border border-border-subtle bg-panel px-3 py-1 text-[12px] text-text-tertiary md:inline-flex">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-healthy opacity-60" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-healthy" />
              </span>
              Live · updated {liveTimestamp}
            </span>
          )}
        </nav>
      </div>
    </header>
  );
}

export function Footer({ condensed = false }: { condensed?: boolean }) {
  return (
    <footer className={`mt-24 border-t border-border-subtle ${condensed ? "py-8" : "py-12"}`}>
      <div className="mx-auto flex max-w-[1200px] flex-col gap-4 px-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3 text-[13px] text-text-tertiary">
          <span className="font-semibold text-text-secondary">EV Fleet APM</span>
          <span>·</span>
          <span>Battery Asset Performance Management</span>
        </div>
        <div className="flex items-center gap-5 text-[13px]">
          <Link to="/" className="text-text-secondary hover:text-text-primary">Dashboard</Link>
          <Link to="/about" className="text-text-secondary hover:text-text-primary">About</Link>
          <span className="inline-flex items-center gap-2 text-text-tertiary">
            <span className="h-1.5 w-1.5 rounded-full bg-healthy" />
            Backend verified &amp; tested
          </span>
        </div>
      </div>
    </footer>
  );
}
