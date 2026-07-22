"use client";

export default function TopBar({
  hasScenario,
  onReset,
}: {
  hasScenario: boolean;
  onReset: () => void;
}) {
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-logo" aria-hidden>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2 4 5v6c0 5 3.4 8.5 8 11 4.6-2.5 8-6 8-11V5l-8-3Z"
              fill="rgba(16,185,129,0.15)"
              stroke="#10b981"
              strokeWidth="1.5"
              strokeLinejoin="round"
            />
            <path d="M12.7 6.5 9 13h2.6l-1 4.5 4.4-6.6H12l.7-4.4Z" fill="#10b981" />
          </svg>
        </span>
        <div>
          <div className="brand-name">CellSentry</div>
          <div className="brand-sub">Battery Supply-Chain Risk Intelligence</div>
        </div>
      </div>
      <div className="topbar-right">
        {hasScenario && (
          <button className="btn-ghost" onClick={onReset}>
            Reset view
          </button>
        )}
        <span className="status-pill">
          <span className="dot" /> Live · Neo4j
        </span>
      </div>
    </header>
  );
}
