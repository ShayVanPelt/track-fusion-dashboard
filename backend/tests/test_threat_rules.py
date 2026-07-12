"""
YOUR TASK: fill in the TODOs. These tests define what each threat rule
in threat_rules.py should actually do — write the implementation to
satisfy these, not the other way around.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from threat_rules import evaluate, RESTRICTED_ZONE_RADIUS_M, SPEED_THRESHOLD_MS


def test_track_outside_zone_and_within_speed_is_not_flagged():
    """A slow surface track, far from the restricted zone, with no
    trail history, should not be flagged at all."""
    # TODO: call evaluate(...) with values that should NOT trip any rule
    # TODO: assert result["flagged"] is False and reasons == []
    raise NotImplementedError


def test_track_inside_restricted_zone_is_flagged():
    """A track positioned at/near RESTRICTED_ZONE_CENTER should be
    flagged with a reason mentioning the zone."""
    # TODO: call evaluate(...) with x, y inside the zone radius
    # TODO: assert flagged is True and a reason mentions "restricted zone"
    raise NotImplementedError


def test_fast_surface_contact_is_flagged():
    """A 'surface' track moving faster than SPEED_THRESHOLD_MS, far from
    the zone, should be flagged for its speed — not the zone."""
    # TODO: pick a position far outside RESTRICTED_ZONE_RADIUS_M
    # TODO: speed = SPEED_THRESHOLD_MS + some margin
    # TODO: assert flagged is True, reason mentions speed
    raise NotImplementedError


def test_erratic_trail_history_is_flagged():
    """A trail that oscillates back and forth (low net displacement,
    long path length) should trip the erratic-track rule, even if
    position/speed alone look fine."""
    # TODO: construct a `trail` list of (x, y) points that zig-zag
    # rather than moving purposefully in one direction
    # TODO: assert flagged is True
    raise NotImplementedError
