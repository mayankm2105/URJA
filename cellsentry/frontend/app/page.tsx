"use client";

import { useEffect, useMemo, useState } from "react";
import AlertPanel from "@/components/AlertPanel";
import SignalFeed from "@/components/SignalFeed";
import SupplyGraph from "@/components/SupplyGraph";
import TopBar from "@/components/TopBar";
import {
  fetchEvents,
  fetchGraph,
  runScenario,
  type GraphResponse,
  type ScenarioResponse,
  type SignalEvent,
} from "@/lib/api";

export default function Home() {
  const [baseline, setBaseline] = useState<GraphResponse | null>(null);
  const [events, setEvents] = useState<SignalEvent[]>([]);
  const [scenario, setScenario] = useState<ScenarioResponse | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchGraph(), fetchEvents()])
      .then(([g, e]) => {
        setBaseline(g);
        setEvents(e);
      })
      .catch((err) => setError(String(err)));
  }, []);

  const onSelect = (id: string) => {
    setSelected(id);
    setScenarioLoading(true);
    runScenario([id])
      .then(setScenario)
      .catch((err) => setError(String(err)))
      .finally(() => setScenarioLoading(false));
  };

  const onReset = () => {
    setSelected(null);
    setScenario(null);
  };

  const nodes = scenario?.nodes ?? baseline?.nodes ?? [];
  const edges = scenario?.edges ?? baseline?.edges ?? [];

  const hotIds = useMemo(() => {
    const s = new Set<string>();
    if (scenario) {
      for (const n of scenario.nodes) {
        if (n.baseline_risk != null && n.risk - n.baseline_risk >= 1) s.add(n.id);
      }
    }
    return s;
  }, [scenario]);

  return (
    <div className="app">
      <TopBar hasScenario={!!scenario} onReset={onReset} />
      <div className="main">
        <SignalFeed
          events={events}
          selectedId={selected}
          onSelect={onSelect}
          loading={!baseline && !error}
        />

        <section className="graph-pane">
          <div className="graph-title">Supply Graph</div>
          <div className="legend">
            <span>
              <i style={{ background: "#10b981" }} /> Low
            </span>
            <span>
              <i style={{ background: "#ee9800" }} /> Med
            </span>
            <span>
              <i style={{ background: "#ff5d52" }} /> High
            </span>
          </div>

          {error && (
            <div className="center error">
              {error} — is the backend running on :8000?
            </div>
          )}
          {!error && nodes.length === 0 && (
            <div className="center muted">Loading supply graph…</div>
          )}
          {!error && nodes.length > 0 && (
            <SupplyGraph nodes={nodes} edges={edges} hotIds={hotIds} />
          )}
        </section>

        <AlertPanel
          alerts={scenario?.alerts ?? []}
          hasScenario={!!scenario}
          loading={scenarioLoading}
        />
      </div>
    </div>
  );
}
