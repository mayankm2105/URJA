import re

with open("platform-new/src/routes/carbonpulse.tsx", "r") as f:
    code = f.read()

# Add leaflet css and js imports
# Wait, we can just import L from 'leaflet' and import 'leaflet/dist/leaflet.css'
target_import = """import { AgentPage } from "@/components/urja/AgentPage";"""
replacement_import = """import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useRef } from 'react';
import { AgentPage } from "@/components/urja/AgentPage";"""
if "import L from 'leaflet';" not in code:
    code = code.replace(target_import, replacement_import)

target_map = """function IndiaMap({ routes }: { routes: RouteRow[] }) {
  // Simple equirectangular projection over an India bounding box.
  const W = 560, H = 520;
  const LON_MIN = 68, LON_MAX = 97;
  const LAT_MIN = 8, LAT_MAX = 36;
  const proj = (lat: number, lon: number) => ({
    x: ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * W,
    y: H - ((lat - LAT_MIN) / (LAT_MAX - LAT_MIN)) * H,
  });
  const colorFor = (r: RouteRow) =>
    r.is_electrified ? "#34d399" : r.monthly_co2_tons > 150 ? "#f87171" : "#fbbf24";
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      <defs>
        <radialGradient id="mapbg" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stopColor="rgba(91,95,237,0.12)" />
          <stop offset="100%" stopColor="rgba(15,17,23,0)" />
        </radialGradient>
      </defs>
      <rect x="0" y="0" width={W} height={H} fill="url(#mapbg)" rx="12" />
      {/* Approx India outline */}
      <path
        d="M180 40 L260 30 L340 60 L420 90 L470 160 L490 240 L470 320 L420 400 L360 470 L300 495 L240 470 L200 410 L170 340 L140 260 L130 180 L150 100 Z"
        fill="rgba(255,255,255,0.02)"
        stroke="rgba(255,255,255,0.12)"
        strokeWidth={1}
      />
      {routes.map((r) => {
        const a = proj(r.origin_lat, r.origin_lon);
        const b = proj(r.dest_lat, r.dest_lon);
        const c = colorFor(r);
        return (
          <g key={r.id}>
            <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={c} strokeWidth={2} strokeOpacity={0.75} />
            <circle cx={a.x} cy={a.y} r={4} fill={c} />
            <circle cx={b.x} cy={b.y} r={4} fill={c} />
            <text x={a.x + 6} y={a.y - 6} fill="#9a9aa8" fontSize={9}>{r.origin_city}</text>
            <text x={b.x + 6} y={b.y - 6} fill="#9a9aa8" fontSize={9}>{r.dest_city}</text>
          </g>
        );
      })}
    </svg>
  );
}"""

replacement_map = """function IndiaMap({ routes }: { routes: RouteRow[] }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInst = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    if (!mapInst.current) {
      mapInst.current = L.map(mapRef.current).setView([22.0, 78.0], 4);
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: "abcd",
        maxZoom: 20
      }).addTo(mapInst.current);
    }
    
    // Clear existing layers except tile layer
    mapInst.current.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.CircleMarker) {
        mapInst.current?.removeLayer(layer);
      }
    });

    const colorFor = (r: RouteRow) =>
      r.is_electrified ? "#34d399" : r.monthly_co2_tons > 150 ? "#f87171" : "#fbbf24";

    routes.forEach(r => {
      const c = colorFor(r);
      const origin = [r.origin_lat, r.origin_lon] as [number, number];
      const dest = [r.dest_lat, r.dest_lon] as [number, number];

      // Draw line
      L.polyline([origin, dest], {
        color: c,
        weight: 2,
        opacity: 0.6,
        dashArray: r.is_electrified ? "5,5" : undefined
      }).addTo(mapInst.current!);

      // Draw origin marker
      L.circleMarker(origin, {
        radius: 5,
        fillColor: c,
        color: "#fff",
        weight: 1,
        fillOpacity: 1
      }).addTo(mapInst.current!).bindTooltip(r.origin_city);

      // Draw dest marker
      L.circleMarker(dest, {
        radius: 5,
        fillColor: c,
        color: "#fff",
        weight: 1,
        fillOpacity: 1
      }).addTo(mapInst.current!).bindTooltip(r.dest_city);
    });

  }, [routes]);

  return <div ref={mapRef} className="w-full h-[520px] rounded-[12px] overflow-hidden" />;
}"""
code = code.replace(target_map, replacement_map)

with open("platform-new/src/routes/carbonpulse.tsx", "w") as f:
    f.write(code)

