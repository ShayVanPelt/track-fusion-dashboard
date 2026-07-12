# Track Fusion — Common Operating Picture (Blueprint)

Skeleton for a real-time multi-target tracking dashboard: simulated sensor
detections get fused with a Kalman filter into stable tracks, run through a
rule-based threat classifier, and streamed live to a map-based HUD.

The **frontend is already built** (`frontend/index.html`) — a dark
ops-console map with rotating heading markers, live trails, and a sidebar
HUD. Don't touch it; everything you build in the backend just needs to
match the JSON schema documented in `backend/main.py`.

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
                                                  │ (already built)   │
                                                  └──────────────────┘
```

## Build checklist (4 weeks)

### Week 1 — core tracking engine
- [ ] `simulator.py`: implement `SimTarget.step()` (motion model,
      maneuvering vs. erratic behavior) and `.noisy_measurement()`
      (gaussian noise + dropped detections)
- [ ] `simulator.py`: implement `make_default_targets()` — a handful of
      air/surface/unknown targets
- [ ] `kalman.py`: implement `predict()` and `update()` — the actual
      Kalman filter math (see the docstring for the five equations)
- [ ] `tests/test_kalman.py`: implement the two behavioral tests —
      error shrinks over time, and coasting-through-a-drop extrapolates
      forward
- [ ] Sanity check: run the simulator + filter together in a throwaway
      script and print positions for a few ticks before wiring anything else

### Week 2 — fusion + classification
- [ ] `threat_rules.py`: implement the three rules (zone, speed,
      erratic trail) — see the module docstring for the exact logic
- [ ] `tests/test_threat_rules.py`: implement all four tests
- [ ] Edge cases worth adding once the basics pass: a target crossing
      in and out of the zone over time; a maneuvering-but-not-erratic
      target that shouldn't false-positive on the erratic-trail rule

### Week 3 — live delivery
- [ ] `main.py`: implement `TrackFusionEngine.tick()` — wire
      simulator → kalman → threat_rules together per target
- [ ] `main.py`: implement the `/ws/tracks` WebSocket loop — send the
      one-time config message, then stream tracks every `DT` seconds
- [ ] Open `http://127.0.0.1:8000` and confirm markers move, trails
      draw, and the sidebar updates. Open devtools console if nothing
      renders — a schema mismatch will fail silently on the frontend

### Week 4 — polish + write-up
- [ ] Get `flake8` and `pytest` both passing locally (CI already
      wired up in `.github/workflows/ci.yml` — it'll run automatically
      on push)
- [ ] Push to GitHub, confirm CI is green
- [ ] Write a short doc (or expand this README) connecting each design
      decision — why constant-velocity KF, why rule-based classification,
      why WebSocket — back to the real ISR/C2 systems this mirrors. This
      is what makes the project an interview talking point, not just a repo

## Running it

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open **http://127.0.0.1:8000**.

### Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
flake8 . --max-line-length=100 --exclude=tests --extend-ignore=E203,W503
```

## Possible extensions (after the core is working)

- Interacting Multiple Model (IMM) filter for better maneuvering-target
  tracking than a plain constant-velocity model
- Swap the rule-based classifier for a trained model and compare
  precision/recall against the rules
- Multiple simulated sensors per target, fused together (true
  multi-sensor fusion, not single-sensor smoothing)
- Docker Compose for one-command startup
