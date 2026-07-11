# Track Fusion — Common Operating Picture

A real-time multi-target tracking dashboard: simulated sensor detections are
fused with a Kalman filter into stable tracks, run through a rule-based
threat classifier, and streamed live to a map-based HUD.

This is a small-scale version of the "sensor fusion + common operating
picture" pattern used in real ISR (intelligence, surveillance,
reconnaissance) and maritime/air domain awareness systems — the same
architectural shape you'd find behind a naval combat system's tactical
display or an airspace-monitoring console, built here with synthetic
data end to end.

![status](https://img.shields.io/badge/status-in--development-yellow)

## What it does

- Simulates 5 targets (air/surface/unknown) moving over a small area,
  each producing **noisy, occasionally-dropped** position reports —
  the way a real radar or AIS feed behaves, not a clean ground-truth feed.
- Fuses each target's detections independently with a **constant-velocity
  Kalman filter**, so a track keeps a stable, predicted position even
  when a detection is missed (coasting).
- Runs each fused track through a small **rule-based threat classifier**
  (restricted-zone entry, anomalous speed, erratic heading history) and
  flags anything suspicious.
- Streams the fused picture over a **WebSocket** to a live map dashboard
  styled like an ops console: track markers rotate with heading, flagged
  tracks turn red, and a sidebar shows live telemetry per track.

## Architecture

```
 ┌─────────────────┐     noisy detections      ┌──────────────────┐
 │  simulator.py    │ ─────────────────────────▶│  kalman.py        │
 │  synthetic       │                            │  per-track        │
 │  sensor targets  │                            │  KalmanTracker    │
 └─────────────────┘                            └─────────┬─────────┘
                                                            │ fused state
                                                            ▼
                                                  ┌──────────────────┐
                                                  │ threat_rules.py   │
                                                  │ zone / speed /    │
                                                  │ erratic-track     │
                                                  │ classification    │
                                                  └─────────┬─────────┘
                                                            │ flagged tracks
                                                            ▼
                                                  ┌──────────────────┐
                                                  │  main.py          │
                                                  │  FastAPI +        │
                                                  │  WebSocket /ws/   │
                                                  │  tracks           │
                                                  └─────────┬─────────┘
                                                            │ JSON over WS
                                                            ▼
                                                  ┌──────────────────┐
                                                  │ frontend/         │
                                                  │ index.html        │
                                                  │ Leaflet map + HUD │
                                                  └──────────────────┘
```

Each stage is intentionally decoupled: swap `simulator.py` for a real feed
(AIS, ADS-B, a radar API) or `threat_rules.py` for a trained classifier
without touching anything downstream.

## Running it

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open **http://127.0.0.1:8000** in a browser — the dashboard is served
directly by the backend.

### Running tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
flake8 . --max-line-length=100 --exclude=tests --extend-ignore=E203,W503
```

CI runs both on every push via `.github/workflows/ci.yml`.

## Roadmap (built over 4 weeks)

- **Week 1 — core tracking engine.** Synthetic multi-target simulator with
  realistic sensor noise and dropped detections; constant-velocity Kalman
  filter per track; unit tests proving the filter actually reduces error
  over raw measurements and correctly coasts through missed detections.
- **Week 2 — fusion + classification.** Wire simulator → filter → threat
  rules into one pipeline; add the restricted-zone / speed-envelope /
  erratic-track heuristics; expand test coverage around edge cases
  (target enters/exits zone, maneuvering targets).
- **Week 3 — live delivery + frontend.** FastAPI WebSocket endpoint
  streaming fused state; Leaflet-based map dashboard with rotating
  heading markers, live trails, and a sidebar HUD showing per-track
  telemetry and flag reasons.
- **Week 4 — polish + write-up.** CI (lint + test) via GitHub Actions,
  architecture diagram and README, and a short write-up connecting each
  design decision back to the real-world sensor-fusion / C2 systems it's
  modeled after — this is what turns a side project into an interview
  talking point.

## Possible extensions

- Swap the constant-velocity model for an Interacting Multiple Model
  (IMM) filter to better track maneuvering targets.
- Replace the rule-based classifier with a trained model (e.g. gradient
  boosted trees on kinematic features) and compare precision/recall
  against the rules.
- Add a second simulated sensor per target and fuse multiple detections
  per tick (true multi-sensor fusion, not just single-sensor smoothing).
- Containerize with Docker Compose for one-command startup.
