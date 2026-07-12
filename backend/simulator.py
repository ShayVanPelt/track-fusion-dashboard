"""
Synthetic multi-target sensor feed.

YOUR TASK: implement SimTarget.step() and SimTarget.noisy_measurement(),
and fill in make_default_targets() with a handful of targets.

Goal: generate "ground truth" tracks moving over a small area, then
produce noisy position reports the way a real sensor (radar, AIS,
ADS-B) would — including occasionally DROPPING a detection entirely.
The dropped-detection behavior is what makes the Kalman filter's
predict-without-update path actually matter, so don't skip it.

Coordinates: work in a local flat metre grid centered on
REFERENCE_LAT/LON and convert to lat/lon only for display — fine as an
approximation over an area this small (a few km).
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
    """Convert local metre-grid coordinates to lat/lon for map display."""
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
    maneuver_prob: float = 0.05   # chance per tick of a random heading change
    drop_prob: float = 0.05       # chance a given tick's detection is missed
    erratic: bool = False         # True => behaves like an anomalous contact
    trail: list = field(default_factory=list)

    def step(self, dt: float):
        """Advance ground-truth position by dt seconds.

        TODO:
        1. If self.erratic, randomly perturb heading/speed more
           aggressively than a normal target (this is what should later
           trip the "erratic track" threat rule).
           Otherwise, occasionally perturb heading using maneuver_prob
           (small realistic course changes).
        2. Convert heading_deg + speed into an (x, y) displacement over
           dt and update self.x, self.y.
           Hint: dx = sin(heading_rad) * speed * dt,
                 dy = cos(heading_rad) * speed * dt
           (heading 0 = north, so sin/cos are swapped vs. standard math angle)
        3. Append (self.x, self.y) to self.trail, and cap its length
           (e.g. keep only the last 60 points) so it doesn't grow forever.
        """
        raise NotImplementedError

    def noisy_measurement(self, meas_std: float = 8.0):
        """Return a noisy (x, y) position report, or None if this tick's
        detection was dropped (simulating a real sensor miss).

        TODO:
        1. Roll against self.drop_prob — if it hits, return None.
        2. Otherwise return (self.x + gaussian noise, self.y + gaussian
           noise) using meas_std as the noise standard deviation.
        """
        raise NotImplementedError


def make_default_targets() -> list[SimTarget]:
    """
    TODO: return a list of SimTarget instances to populate the demo.

    Suggested starting set (feel free to change positions/speeds):
      - 2-3 "air" targets: faster (60-100 m/s), moderate maneuver_prob
      - 1-2 "surface" targets: slower (5-10 m/s)
      - 1 "unknown" target with erratic=True and a higher drop_prob —
        this is the one your threat classifier should catch later.

    Spread starting positions out a few km (thousands of metres) from
    (0, 0) in different directions so they're visually distinct on the
    map once converted to lat/lon.
    """
    raise NotImplementedError
