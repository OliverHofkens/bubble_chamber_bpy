import random
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Particle:
    position: np.ndarray
    velocity: np.ndarray
    charges: np.ndarray
    decays_after: float = field(init=False)
    lifetime: float = 0.0
    is_alive: bool = True
    is_dirty: bool = True

    def __post_init__(self):
        # Generate a decay time for this particle:
        self.decays_after = random.uniform(0.5, 5.0)

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
