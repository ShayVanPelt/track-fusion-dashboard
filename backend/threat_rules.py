"""
Minimal rule-based threat classifier.

YOUR TASK: implement evaluate() below.

Real systems use far more (IFF, doctrine-based classification, ML
classifiers on kinematic + RF signatures) but the shape is the same:
take a fused track's kinematics and recent history, and emit a
classification + flag. Keep this simple and easy to extend — the goal
is a clean function boundary you could later swap for a trained model
without touching anything else in the pipeline.

Three rules to implement, each appending a human-readable reason
string to `reasons` if it trips:

1. RESTRICTED ZONE — track's (x, y) is within RESTRICTED_ZONE_RADIUS_M
   of RESTRICTED_ZONE_CENTER. Use plain Euclidean distance.

2. SPEED ENVELOPE — a "surface" track exceeding SPEED_THRESHOLD_MS.
   (Air targets are expected to be fast, so this rule should probably
   only apply to kind == "surface" — your call on exact scoping.)

3. ERRATIC TRACK HISTORY — look at the last HEADING_CHANGE_WINDOW
   points in `trail`. Compute:
     - net displacement: straight-line distance from first to last point
     - path length: sum of distances between consecutive points
   A target moving purposefully in roughly one direction has
   net_displacement/path_length close to 1. A target oscillating back
   and forth (or looping) has a much smaller ratio. Flag if path_length
   is non-trivial (e.g. > 50m, to avoid false positives on a nearly
   stationary target) AND the ratio is below HEADING_CHANGE_THRESHOLD's
   equivalent cutoff (pick a ratio threshold, e.g. 0.35, and justify it
   in a comment).
"""
from __future__ import annotations

RESTRICTED_ZONE_CENTER = (0.0, 0.0)   # local x,y metres
RESTRICTED_ZONE_RADIUS_M = 1500.0

SPEED_THRESHOLD_MS = 40.0        # surface contacts faster than this look odd
HEADING_CHANGE_WINDOW = 6        # ticks of trail history to look at
HEADING_CHANGE_THRESHOLD = 70.0  # degrees of net heading swing (if you go that route)


def _distance(a, b) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def evaluate(kind: str, x: float, y: float, speed: float, heading_deg: float,
             trail: list) -> dict:
    """Return {"flagged": bool, "reasons": list[str]}.

    TODO: implement the three rules described in the module docstring.
    """
    reasons = []

    # TODO: rule 1 — restricted zone
    # TODO: rule 2 — speed envelope (surface contacts)
    # TODO: rule 3 — erratic trail history

    return {
        "flagged": len(reasons) > 0,
        "reasons": reasons,
    }
