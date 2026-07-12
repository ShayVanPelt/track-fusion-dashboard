"""
Constant-velocity Kalman filter for 2D target tracking.

YOUR TASK: implement predict() and update() below.

State vector: x = [x, y, vx, vy]   (position + velocity)
Measurement:  z = [x, y]           (noisy position report from a sensor)

This is the standard linear Kalman filter. Five equations to implement,
in two groups:

  PREDICT (project state forward by dt, no measurement involved):
      x = F @ x
      P = F @ P @ F.T + Q

  UPDATE (fold in a new noisy measurement):
      y = z - H @ x                      # innovation (residual)
      S = H @ P @ H.T + R                # innovation covariance
      K = P @ H.T @ inv(S)               # Kalman gain
      x = x + K @ y
      P = (I - K @ H) @ P

Where:
  F = state transition matrix (constant-velocity motion model)
  H = measurement matrix (we only observe position, not velocity)
  Q = process noise covariance (how much you trust the motion model)
  R = measurement noise covariance (how noisy the sensor is)
  P = state covariance (how uncertain the current estimate is)

HINTS:
- F should encode: x_new = x + vx*dt, y_new = y + vy*dt, velocities unchanged.
  That's a 4x4 matrix with 1s on the diagonal and `dt` in two spots.
- H should map [x, y, vx, vy] -> [x, y]. It's a 2x4 matrix.
- Start with Q and R as simple diagonal matrices (e.g. Q = q * I,
  R = meas_var * I) and tune from there once things work.
- Initialize P as something like eye(4) * 50 — fairly uncertain at first.

TEST TARGET (see tests/test_kalman.py):
  1. Tracking error should shrink as more measurements arrive, vs. just
     using the raw noisy measurement directly.
  2. When step() is called with z=None (a dropped detection), the
     tracker should still move forward using the motion model alone
     (predict, no update) rather than freezing in place.
"""
from __future__ import annotations
import numpy as np


class KalmanTracker:
    def __init__(self, x0: float, y0: float, dt: float = 0.5,
                 process_var: float = 0.5, meas_var: float = 4.0):
        self.dt = dt

        # TODO: state vector [x, y, vx, vy]
        self.x = None

        # TODO: state transition matrix F (4x4, constant-velocity model)
        self.F = None

        # TODO: measurement matrix H (2x4, we only observe position)
        self.H = None

        # TODO: process noise covariance Q (4x4)
        # Simple version: Q = process_var * np.eye(4)
        # Better version: derive from the discretized white-noise-acceleration
        # model (look this up if you want the "correct" textbook Q).
        self.Q = None

        # TODO: measurement noise covariance R (2x2)
        self.R = None

        # TODO: initial state covariance P (4x4) — start fairly uncertain
        self.P = None

    def predict(self) -> np.ndarray:
        """Project the state forward by dt using the motion model only.
        No measurement involved. Updates self.x and self.P in place."""
        # TODO: self.x = self.F @ self.x
        # TODO: self.P = self.F @ self.P @ self.F.T + self.Q
        raise NotImplementedError

    def update(self, z: np.ndarray) -> np.ndarray:
        """Fold a new noisy measurement z=[x,y] into the current estimate."""
        # TODO: innovation, innovation covariance, Kalman gain
        # TODO: update self.x and self.P
        raise NotImplementedError

    def step(self, z: np.ndarray | None) -> np.ndarray:
        """Predict, then update only if a measurement is available this
        tick. This is what makes "coasting" through a dropped detection
        work: predict() always runs, update() is conditional."""
        self.predict()
        if z is not None:
            self.update(z)
        return self.x

    @property
    def position(self) -> tuple[float, float]:
        return float(self.x[0]), float(self.x[1])

    @property
    def velocity(self) -> tuple[float, float]:
        return float(self.x[2]), float(self.x[3])

    @property
    def speed(self) -> float:
        vx, vy = self.velocity
        return float(np.hypot(vx, vy))

    @property
    def heading_deg(self) -> float:
        vx, vy = self.velocity
        return float((np.degrees(np.arctan2(vx, vy)) + 360) % 360)
