"""
Minimal rule-based classifier.

Real systems use far more (IFF, doctrine-based classification, ML
classifiers on kinematic + RF signatures) but the shape is the same:
take a fused track's kinematics and recent history, and emit a
classification + flag. This is intentionally simple and easy to
extend -- swap `evaluate()` for a model later without touching
anything else in the pipeline.
"""
from __future__ import annotations

RESTRICTED_ZONE_CENTER = (0.0, 0.0)   # local x,y metres
RESTRICTED_ZONE_RADIUS_M = 1500.0

SPEED_THRESHOLD_MS = 40.0        # surface contacts faster than this look odd
HEADING_CHANGE_WINDOW = 6        # ticks of trail history to look at
HEADING_CHANGE_THRESHOLD = 70.0  # degrees of net heading swing


def _distance(a, b) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def evaluate(kind: str, x: float, y: float, speed: float, heading_deg: float,
             trail: list) -> dict:
    reasons = []

    if kind == "surface" and speed > SPEED_THRESHOLD_MS:
        reasons.append("surface contact exceeding expected speed envelope")

    if _distance((x, y), RESTRICTED_ZONE_CENTER) < RESTRICTED_ZONE_RADIUS_M:
        reasons.append("inside restricted zone")

    if len(trail) >= HEADING_CHANGE_WINDOW:
        recent = trail[-HEADING_CHANGE_WINDOW:]
        dx = recent[-1][0] - recent[0][0]
        dy = recent[-1][1] - recent[0][1]
        # crude erraticism proxy: net displacement small relative to
        # path length implies a lot of back-and-forth movement
        path_len = sum(
            _distance(recent[i], recent[i + 1]) for i in range(len(recent) - 1)
        )
        net_disp = (dx ** 2 + dy ** 2) ** 0.5
        if path_len > 50 and net_disp / path_len < 0.35:
            reasons.append("erratic / non-ballistic track history")

    return {
        "flagged": len(reasons) > 0,
        "reasons": reasons,
    }
