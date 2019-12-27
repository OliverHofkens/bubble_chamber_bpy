from time import perf_counter
from typing import Sequence

import numpy as np

from bubble_chamber_bpy.models import BubbleChamber, Particle


class Simulation:
    def __init__(self, chamber: BubbleChamber, particles: Sequence[Particle]):
        self.chamber: BubbleChamber = chamber
        self.particles: Sequence[Particle] = particles
        self.clock: float = 0.0

    def start(self):
        self.clock = perf_counter()

    def step(self):
        now = perf_counter()
        tdelta = now - self.clock
        self.clock = now

        for p in self.particles:
            self._update_particle(p, tdelta)

    def _update_particle(self, p: Particle, tdelta: float):
        # Magnetic component of Lorentz force:
        mag_force = p.total_charge * np.cross(p.velocity, self.chamber.magnetic_field)

        # Apply force:
        # F = m.a, so a = F / m
        acceleration = mag_force / p.mass
        p.velocity += acceleration * tdelta

        # Friction:
        p.velocity *= 1.0 - (self.chamber.friction * tdelta)

        # Apply velocity:
        p.position += p.velocity * tdelta
