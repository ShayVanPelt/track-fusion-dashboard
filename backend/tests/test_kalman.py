"""
YOUR TASK: these tests define what "correct" means for kalman.py.
Fill in the TODOs — don't just make them pass trivially, make them
actually exercise the behavior described.
"""
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kalman import KalmanTracker


def test_filter_converges_to_constant_velocity_track():
    """A target moving in a straight line at constant velocity, observed
    with noise, should be tracked with shrinking position error as more
    measurements arrive — i.e. the filter should outperform just using
    the raw noisy measurement directly.

    TODO:
    1. Simulate ~40 ticks of a target moving at constant (vx, vy).
    2. Each tick, generate a noisy measurement (true position + gaussian
       noise) and call tracker.step(measurement).
    3. Track the error (distance between tracker.position and true
       position) at each tick.
    4. Assert the average error over the last ~10 ticks is smaller than
       the average error over the first ~5 ticks.
    """
    raise NotImplementedError


def test_coasting_without_measurement_extrapolates_forward():
    """When a detection is dropped (step(None)), the tracker should still
    move its estimate forward using the motion model instead of
    freezing in place.

    TODO:
    1. Feed the tracker a couple of measurements moving in +x direction.
    2. Call tracker.step(None) — a dropped detection.
    3. Assert the estimated position moved further in +x, rather than
       staying exactly where it was.
    """
    raise NotImplementedError


def test_speed_and_heading_are_nonnegative_and_bounded():
    """Sanity check on the derived speed/heading properties."""
    tracker = KalmanTracker(x0=0.0, y0=0.0)
    tracker.step(np.array([5.0, 5.0]))
    assert tracker.speed >= 0
    assert 0 <= tracker.heading_deg < 360
