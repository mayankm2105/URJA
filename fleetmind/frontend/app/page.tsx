"use client";

import { useEffect, useState } from "react";
import {
  fetchAsset,
  fetchFleet,
  fetchMaintenance,
  type AssetDetail,
  type FleetResponse,
  type MaintenanceResponse,
} from "@/lib/api";
import TopBar, { type View } from "@/components/TopBar";
import FleetBoard from "@/components/FleetBoard";
import AssetDetailView from "@/components/AssetDetail";
import MaintenancePanel from "@/components/MaintenancePanel";
import ValidationView from "@/components/ValidationView";
import ElectrificationView from "@/components/ElectrificationView";

export default function Page() {
  const [fleet, setFleet] = useState<FleetResponse | null>(null);
  const [maintenance, setMaintenance] = useState<MaintenanceResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<AssetDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<View>("fleet");

  // Initial load: fleet + maintenance queue, then select the worst asset.
  useEffect(() => {
    Promise.all([fetchFleet(), fetchMaintenance()])
      .then(([f, m]) => {
        setFleet(f);
        setMaintenance(m);
        if (f.assets.length > 0) setSelectedId(f.assets[0].id);
      })
      .catch((e) => setError(String(e)));
  }, []);

  // Load detail whenever the selection changes.
  useEffect(() => {
    if (!selectedId) return;
    setDetail(null);
    fetchAsset(selectedId, true)
      .then(setDetail)
      .catch((e) => setError(String(e)));
  }, [selectedId]);

  if (error) {
    return (
      <div className="shell">
        <div className="error">
          Could not reach the FleetMind backend.<br />
          {error}
          <br />
          <br />
          Start it with: <code>uvicorn app.main:app --reload --port 8000</code>
        </div>
      </div>
    );
  }

  if (view === "validation" || view === "electrification") {
    return (
      <div className="shell">
        <TopBar fleet={fleet} maintenance={maintenance} view={view} onViewChange={setView} />
        <div className="single-col">
          {view === "validation" ? <ValidationView /> : <ElectrificationView />}
        </div>
      </div>
    );
  }

  return (
    <div className="shell">
      <TopBar fleet={fleet} maintenance={maintenance} view={view} onViewChange={setView} />
      <div className="cols">
        {fleet ? (
          <FleetBoard
            assets={fleet.assets}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        ) : (
          <div className="col loading">Loading fleet…</div>
        )}

        <div className="main">
          {detail ? (
            <AssetDetailView detail={detail} />
          ) : (
            <div className="pane loading">Loading asset…</div>
          )}

          <MaintenancePanel
            detail={detail}
            maintenance={maintenance}
            onSelect={setSelectedId}
          />
        </div>
      </div>
    </div>
  );
}
