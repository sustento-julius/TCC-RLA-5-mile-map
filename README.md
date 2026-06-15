# TCC R6 Project Area Planner — Los Angeles

An interactive map tool for planning a **Transformative Climate Communities (TCC) Round 6**
project area in Los Angeles. It plots 51 affordable-housing properties from three operators
and helps find the optimal contiguous **≤ 5.0 sq mi** zone (the TCC R6 urban implementation
grant hard limit, Final Guidelines §1.2).

**Live tool:** https://sustento-julius.github.io/TCC-RLA-5-mile-map/

## What it does

- **Map** of LA (Leaflet + OpenStreetMap) with all 51 properties as colored markers
  — ELACC (coral), LTSC (green), Esperanza (blue). Hover any marker for name, address, and operator.
- **🧩 Auto-build district** — computes a contiguous, gerrymander-style zone that connects the
  most properties within 5 sq mi. Priority: **ELACC first, then LTSC, then Esperanza.**
  A **corridor-width slider** trades coverage against compactness and rebuilds live.
- **✏️ Draw by hand** — click to drop boundary points for any custom shape; drag points to refine.
- **Live stats** — area in sq mi, properties inside by operator, total, and an over-limit warning.

Area and point-in-polygon counts use geodesic math (Turf.js); the auto-builder grows a minimum
corridor network (nearest-neighbor) and buffers it into one continuous polygon.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The complete, self-contained tool (no build step). |
| `properties.json` | The 51 properties with geocoded coordinates. |
| `geocode.py` | Script that geocoded the addresses via OpenStreetMap / Nominatim. |

## Running locally

It's a single static file — just open `index.html` in a browser (needs internet for the map
tiles and the Leaflet/Turf CDN). Or serve it: `python3 -m http.server` then visit the page.

## Notes

- Marker positions are address-level geocodes from OpenStreetMap; spot-check any property sitting
  right on a zone boundary before relying on a borderline in/out call.
- Esperanza's South L.A. cluster sits well southwest of the ELACC/LTSC Boyle Heights–Koreatown
  corridor: a realistic compact zone captures ELACC + nearby LTSC only, while a very thin
  gerrymandered corridor can technically thread all three under 5 sq mi.
