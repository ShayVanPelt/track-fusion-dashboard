"""
Synthetic multi-target sensor feed.

Generates "ground truth" tracks moving over a small operating area near
Victoria, BC, then produces noisy position reports the way a real
sensor (radar, AIS, ADS-B) would -- including occasional dropped
detections, which is what makes the Kalman filter's prediction step
actually matter.

Coordinates: we work in a local flat metre grid centered on
REFERENCE_LAT/LON and convert to lat/lon only for display, which is a
fine approximation over an area this small.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field

REFERENCE_LAT = 48.4284   # Victoria, BC
REFERENCE_LON = -123.3656
METERS_PER_DEG_LAT = 111_320.0


def meters_per_deg_lon(lat: float) -> float:
    return 111_320.0 * math.cos(math.radians(lat))


def xy_to_latlon(x: float, y: float) -> tuple[float, float]:
    lat = REFERENCE_LAT + y / METERS_PER_DEG_LAT
    lon = REFERENCE_LON + x / meters_per_deg_lon(REFERENCE_LAT)
    return lat, lon


@dataclass
class SimTarget:
    id: str
    kind: str          # "air", "surface", "unknown"
    x: float
    y: float
    heading_deg: float   # direction of travel, 0 = north
    speed: float         # m/s
    maneuver_prob: float = 0.05
    drop_prob: float = 0.05   # chance a given tick's detection is missed
    erratic: bool = False     # True => behaves like an anomalous contact
    trail: list = field(default_factory=list)

    def step(self, dt: float):
        if self.erratic:
            # Anomalous contact: irregular speed/heading changes,
            # the kind of profile a threat-classification rule should flag.
            if random.random() < 0.3:
                self.heading_deg = (self.heading_deg + random.uniform(-60, 60)) % 360
            if random.random() < 0.3:
                self.speed = max(0.0, self.speed + random.uniform(-15, 20))
        else:
            if random.random() < self.maneuver_prob:
                self.heading_deg = (self.heading_deg + random.uniform(-25, 25)) % 360

        rad = math.radians(self.heading_deg)
        self.x += math.sin(rad) * self.speed * dt
        self.y += math.cos(rad) * self.speed * dt

        self.trail.append((self.x, self.y))
        if len(self.trail) > 60:
            self.trail.pop(0)

    def noisy_measurement(self, meas_std: float = 8.0):
        if random.random() < self.drop_prob:
            return None  # dropped detection this tick
        return (
            self.x + random.gauss(0, meas_std),
            self.y + random.gauss(0, meas_std),
        )


def make_default_targets() -> list[SimTarget]:
    targets = [
        SimTarget(id="TRK-101", kind="air", x=-4000, y=3000,
                  heading_deg=120, speed=90, maneuver_prob=0.03),
        SimTarget(id="TRK-102", kind="surface", x=3500, y=-2000,
                  heading_deg=200, speed=8, maneuver_prob=0.05),
        SimTarget(id="TRK-103", kind="air", x=1000, y=4500,
                  heading_deg=250, speed=70, maneuver_prob=0.04),
        SimTarget(id="TRK-104", kind="surface", x=-3000, y=-3500,
                  heading_deg=45, speed=6, maneuver_prob=0.05),
        SimTarget(id="TRK-999", kind="unknown", x=500, y=500,
                  heading_deg=0, speed=25, erratic=True, drop_prob=0.15),
    ]
    return targets
