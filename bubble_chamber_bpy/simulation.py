from time import perf_counter
from typing import List, Sequence

import numpy as np

from bubble_chamber_bpy.models import BubbleChamber, Particle


class Simulation:
    def __init__(
        self,
        chamber: BubbleChamber,
        particles: Sequence[Particle],
        time_modifier: float = 1.0,
    ):
        self.chamber: BubbleChamber = chamber
        self.particles: Sequence[Particle] = particles
        self.clock: float = 0.0
        self.time_passed: float = 0.0
        self.time_modifier = time_modifier
        self.new_part_buffer: List[Particle] = []

    def start(self):
        self.clock = perf_counter()

    def step(self):
        now = perf_counter()
        tdelta = (now - self.clock) * self.time_modifier
        self.time_passed += tdelta
        self.clock = now

        for p in self.particles:
            self._update_particle(p, tdelta)
        if self.new_part_buffer:
            self.particles.extend(self.new_part_buffer)
            self.new_part_buffer = []

    def _update_particle(self, p: Particle, tdelta: float):
        # Update lifetime
        p.lifetime += tdelta
        if p.lifetime >= p.decays_after:
            p.is_alive = False

            # Decay into smaller particles
            if p.mass > 1:
                self.split_particle(p)
        else:
            # Magnetic component of Lorentz force:
            mag_force = p.total_charge * np.cross(
                p.velocity, self.chamber.magnetic_field
            )

            # Apply force:
            # F = m.a, so a = F / m
            acceleration = mag_force / p.mass
            p.velocity += acceleration * tdelta

            # Friction:
            p.velocity *= 1.0 - (self.chamber.friction * tdelta)

            # Apply velocity:
            p.position += p.velocity * tdelta

    def split_particle(self, p: Particle):
        if p.mass == 1:
            return

        while p.mass > 1:
            new_charge = np.around(
                np.random.random(p.charges.shape) * p.charges
            ).astype("int64")

            if np.any(new_charge >= 1):
                p.charges -= new_charge
                self.new_part_buffer.append(
                    Particle(np.copy(p.position), np.copy(p.velocity), new_charge)
                )

        # Add the last remaining particle:
        self.new_part_buffer.append(
            Particle(np.copy(p.position), np.copy(p.velocity), np.copy(p.charges))
        )
        print(f"{p} split into {self.new_part_buffer}")
