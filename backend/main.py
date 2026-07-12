"""
Track-fusion dashboard backend.

YOUR TASK: implement TrackFusionEngine.tick() and the /ws/tracks
WebSocket loop below.

Goal: run the simulated feed, fuse each target's noisy detections with
its own KalmanTracker, run the fused state through the threat
classifier, and stream the result to the frontend (already built —
don't touch frontend/index.html) over a WebSocket.

Run with:
    uvicorn main:app --reload --port 8000
Then open http://127.0.0.1:8000 (the frontend is served automatically).

IMPORTANT — the frontend expects this exact JSON shape, so match it:

  On connect, send ONE config message:
    {
      "type": "config",
      "restricted_zone": {"lat": <float>, "lon": <float>, "radius_m": <float>}
    }

  Then repeatedly (every DT seconds) send:
    {
      "type": "tracks",
      "tracks": [
        {
          "id": "TRK-101",
          "kind": "air",                 # air | surface | unknown
          "lat": 48.45,
          "lon": -123.41,
          "speed_ms": 61.8,
          "heading_deg": 114.3,
          "coasting": false,             # true if no detection this tick
          "flagged": false,
          "reasons": [],                 # list[str], from threat_rules
          "trail": [[lat, lon], ...]      # recent history, most recent last
        },
        ...
      ]
    }

Any field missing or misnamed will silently break the map/sidebar, so
check the browser devtools console if things don't render.
"""
from __future__ import annotations
import asyncio
import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from kalman import KalmanTracker
from simulator import make_default_targets, xy_to_latlon
from threat_rules import evaluate, RESTRICTED_ZONE_CENTER, RESTRICTED_ZONE_RADIUS_M

app = FastAPI(title="Track Fusion Dashboard")

DT = 0.5  # seconds between ticks — keep in sync with KalmanTracker(dt=...)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


class TrackFusionEngine:
    def __init__(self):
        self.targets = make_default_targets()
        # TODO: build one KalmanTracker per target, keyed by target.id
        self.trackers = {}

    def tick(self) -> list[dict]:
        """Advance the simulation by one tick and return a list of
        fused-track dicts matching the WebSocket schema above.

        TODO, per target:
        1. target.step(DT) — advance ground truth
        2. meas = target.noisy_measurement() — may be None
        3. tracker.step(np.array(meas) if meas is not None else None)
        4. Read tracker.position / .speed / .heading_deg
        5. Convert fused (x, y) -> (lat, lon) via xy_to_latlon
        6. Run threat_rules.evaluate(...) on the FUSED state (not the
           raw target) — you're classifying what the system believes,
           not the ground truth
        7. Build and append the track dict (see schema above). Convert
           target.trail (local x/y) to lat/lon for the "trail" field —
           reuse xy_to_latlon per point, and only send the last ~20.
        """
        raise NotImplementedError


engine = TrackFusionEngine()

# TODO: compute the restricted zone's lat/lon once at startup
# (xy_to_latlon(*RESTRICTED_ZONE_CENTER)) for the config message.
RESTRICTED_ZONE_LATLON = None


@app.websocket("/ws/tracks")
async def tracks_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        # TODO: send the one-time "config" message (see schema above)

        while True:
            # TODO: tracks = engine.tick()
            # TODO: await websocket.send_text(json.dumps({"type": "tracks", "tracks": tracks}))
            # TODO: await asyncio.sleep(DT)
            raise NotImplementedError
    except WebSocketDisconnect:
        pass


# Serve the static frontend (index.html, etc.) at the root path.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
