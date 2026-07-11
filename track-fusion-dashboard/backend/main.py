"""
Track-fusion dashboard backend.

Runs a simulated multi-sensor feed, fuses each target's noisy
detections with a per-track Kalman filter, applies a simple threat
classifier, and streams the fused picture to any connected browser
over a WebSocket.

Run with:
    uvicorn main:app --reload --port 8000
Then open frontend/index.html (served automatically at /).
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

DT = 0.5  # seconds between ticks

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


class TrackFusionEngine:
    def __init__(self):
        self.targets = make_default_targets()
        self.trackers = {
            t.id: KalmanTracker(t.x, t.y, dt=DT) for t in self.targets
        }

    def tick(self) -> list[dict]:
        out = []
        for t in self.targets:
            t.step(DT)
            meas = t.noisy_measurement()
            tracker = self.trackers[t.id]
            if meas is not None:
                tracker.step(np.array(meas))
            else:
                tracker.step(None)

            fx, fy = tracker.position
            speed = tracker.speed
            heading = tracker.heading_deg
            lat, lon = xy_to_latlon(fx, fy)

            classification = evaluate(
                kind=t.kind, x=fx, y=fy, speed=speed,
                heading_deg=heading, trail=t.trail,
            )

            trail_latlon = [xy_to_latlon(px, py) for px, py in t.trail[-20:]]

            out.append({
                "id": t.id,
                "kind": t.kind,
                "lat": lat,
                "lon": lon,
                "speed_ms": round(speed, 1),
                "heading_deg": round(heading, 1),
                "coasting": meas is None,  # true when no detection this tick
                "flagged": classification["flagged"],
                "reasons": classification["reasons"],
                "trail": [[la, lo] for la, lo in trail_latlon],
            })
        return out


engine = TrackFusionEngine()

RESTRICTED_ZONE_LATLON = xy_to_latlon(*RESTRICTED_ZONE_CENTER)


@app.websocket("/ws/tracks")
async def tracks_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        # Send static config (zone overlay etc.) once up front
        await websocket.send_text(json.dumps({
            "type": "config",
            "restricted_zone": {
                "lat": RESTRICTED_ZONE_LATLON[0],
                "lon": RESTRICTED_ZONE_LATLON[1],
                "radius_m": RESTRICTED_ZONE_RADIUS_M,
            },
        }))
        while True:
            tracks = engine.tick()
            await websocket.send_text(json.dumps({
                "type": "tracks",
                "tracks": tracks,
            }))
            await asyncio.sleep(DT)
    except WebSocketDisconnect:
        pass


# Serve the static frontend (index.html, etc.) at the root path.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
