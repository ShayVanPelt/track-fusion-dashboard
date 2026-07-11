import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from threat_rules import evaluate, RESTRICTED_ZONE_RADIUS_M, SPEED_THRESHOLD_MS


def test_track_outside_zone_and_within_speed_is_not_flagged():
    result = evaluate(
        kind="surface", x=10_000, y=10_000,
        speed=5.0, heading_deg=90, trail=[],
    )
    assert result["flagged"] is False
    assert result["reasons"] == []


def test_track_inside_restricted_zone_is_flagged():
    result = evaluate(
        kind="air", x=0, y=0,
        speed=20.0, heading_deg=90, trail=[],
    )
    assert result["flagged"] is True
    assert any("restricted zone" in r for r in result["reasons"])


def test_fast_surface_contact_is_flagged():
    far_from_zone = RESTRICTED_ZONE_RADIUS_M * 5
    result = evaluate(
        kind="surface", x=far_from_zone, y=far_from_zone,
        speed=SPEED_THRESHOLD_MS + 5, heading_deg=0, trail=[],
    )
    assert result["flagged"] is True
    assert any("speed envelope" in r for r in result["reasons"])


def test_erratic_trail_history_is_flagged():
    far_from_zone = RESTRICTED_ZONE_RADIUS_M * 5
    # A trail that oscillates back and forth: low net displacement,
    # long path length -> should trip the "erratic" heuristic.
    trail = [
        (far_from_zone, far_from_zone),
        (far_from_zone + 50, far_from_zone),
        (far_from_zone, far_from_zone),
        (far_from_zone + 50, far_from_zone),
        (far_from_zone, far_from_zone),
        (far_from_zone + 10, far_from_zone),
    ]
    result = evaluate(
        kind="unknown", x=far_from_zone + 10, y=far_from_zone,
        speed=10.0, heading_deg=0, trail=trail,
    )
    assert result["flagged"] is True
