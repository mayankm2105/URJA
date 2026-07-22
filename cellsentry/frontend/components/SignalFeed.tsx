"use client";

import type { SignalEvent } from "@/lib/api";
import { severityBand } from "@/lib/colors";

export default function SignalFeed({
  events,
  selectedId,
  onSelect,
  loading,
}: {
  events: SignalEvent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  loading: boolean;
}) {
  return (
    <aside className="panel panel-left">
      <div className="panel-head">
        <h2>Disruption Signals</h2>
        <span className="count">{events.length}</span>
      </div>
      {loading && <div className="muted small">Loading signals…</div>}
      <ul className="signal-list">
        {events.map((e) => {
          const band = severityBand(e.severity);
          return (
            <li
              key={e.id}
              className={`signal ${selectedId === e.id ? "selected" : ""}`}
              onClick={() => onSelect(e.id)}
            >
              <div className="signal-top">
                <span className="signal-date">{e.date}</span>
                <span className={`chip chip-${band}`}>{e.severity}</span>
              </div>
              <div className="signal-headline">{e.headline}</div>
              <div className="signal-source">Source: {e.source.name}</div>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
