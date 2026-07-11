"""
Constant-velocity Kalman filter for 2D target tracking.

State vector: [x, y, vx, vy]
Measurement:  [x, y]  (noisy position report from a "sensor")

This is the same core model used in real radar/track-fusion systems to
smooth noisy detections into a stable track and predict where a target
will be between updates.
"""
from __future__ import annotations
import numpy as np


class KalmanTracker:
    def __init__(self, x0: float, y0: float, dt: float = 0.5,
                 process_var: float = 0.5, meas_var: float = 4.0):
        self.dt = dt

        # State: [x, y, vx, vy]
        self.x = np.array([x0, y0, 0.0, 0.0], dtype=float)

        # State transition (constant velocity model)
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

        # We only measure position
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ])

        # Process noise (how much we trust the motion model)
        q = process_var
        self.Q = q * np.array([
            [dt**4/4, 0, dt**3/2, 0],
            [0, dt**4/4, 0, dt**3/2],
            [dt**3/2, 0, dt**2, 0],
            [0, dt**3/2, 0, dt**2],
        ])

        # Measurement noise (how noisy the sensor is)
        self.R = meas_var * np.eye(2)

        # Initial covariance: fairly unsure at first
        self.P = np.eye(4) * 50.0

    def predict(self) -> np.ndarray:
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x

    def update(self, z: np.ndarray) -> np.ndarray:
        y = z - self.H @ self.x  # innovation
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain
        self.x = self.x + K @ y
        identity = np.eye(4)
        self.P = (identity - K @ self.H) @ self.P
        return self.x

    def step(self, z: np.ndarray | None) -> np.ndarray:
        """Predict, then update if a measurement is available this tick
        (models a sensor that occasionally drops a detection)."""
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
