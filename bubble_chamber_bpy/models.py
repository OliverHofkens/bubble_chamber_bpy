from dataclasses import dataclass

import numpy as np


@dataclass
class Particle:
    position: np.ndarray
    velocity: np.ndarray
    charges: np.ndarray
    lifetime: float
    decays_after: float

    @property
    def total_charge(self) -> int:
        return self.charges[0] - self.charges[2]

    @property
    def mass(self) -> int:
        return np.sum(self.charges)


@dataclass
class BubbleChamber:
    dimensions: np.ndarray
    magnetic_field: np.ndarray
    friction: float
