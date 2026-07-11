import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kalman import KalmanTracker


def test_filter_converges_to_constant_velocity_track():
    """A target moving in a straight line at constant velocity, observed
    with noise, should be tracked with shrinking position error as more
    measurements arrive."""
    rng = np.random.default_rng(42)
    true_vx, true_vy = 10.0, 5.0
    x, y = 0.0, 0.0
    tracker = KalmanTracker(x0=0.0, y0=0.0, dt=0.5)

    errors = []
    for _ in range(40):
        x += true_vx * 0.5
        y += true_vy * 0.5
        z = np.array([x + rng.normal(0, 4), y + rng.normal(0, 4)])
        tracker.step(z)
        est_x, est_y = tracker.position
        errors.append(((est_x - x) ** 2 + (est_y - y) ** 2) ** 0.5)

    # Later error should be smaller on average than early error --
    # i.e. the filter is actually learning the motion, not just
    # passing through raw noisy measurements.
    early_avg = sum(errors[:5]) / 5
    late_avg = sum(errors[-10:]) / 10
    assert late_avg < early_avg


def test_coasting_without_measurement_extrapolates_forward():
    """When a detection is dropped, the tracker should still move its
    estimate forward using the motion model instead of freezing."""
    tracker = KalmanTracker(x0=0.0, y0=0.0, dt=1.0)
    tracker.step(np.array([10.0, 0.0]))
    tracker.step(np.array([20.0, 0.0]))
    pos_before = tracker.position

    tracker.step(None)  # dropped detection
    pos_after = tracker.position

    assert pos_after[0] > pos_before[0]


def test_speed_and_heading_are_nonnegative_and_bounded():
    tracker = KalmanTracker(x0=0.0, y0=0.0)
    tracker.step(np.array([5.0, 5.0]))
    assert tracker.speed >= 0
    assert 0 <= tracker.heading_deg < 360
