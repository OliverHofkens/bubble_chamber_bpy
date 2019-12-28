import numpy as np
import pytest

from bubble_chamber_bpy.models import BubbleChamber, Particle
from bubble_chamber_bpy.simulation import Simulation


@pytest.fixture
def chamber():
    return BubbleChamber(np.array([10, 10, 10]), np.array([0.0, 0.0, 2.0]), 0.3)


def particle_with_charge(pos, neut, neg):
    return Particle(
        np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]), np.array([pos, neut, neg])
    )


def test_particle_with_mass_one_doesnt_split(chamber):
    sim = Simulation(chamber, [])
    p = particle_with_charge(1, 0, 0)
    sim.split_particle(p)

    assert len(sim.new_part_buffer) == 0


def test_particle_with_mass_two_splits_in_two(chamber):
    sim = Simulation(chamber, [])
    p = particle_with_charge(1, 1, 0)
    sim.split_particle(p)

    assert len(sim.new_part_buffer) == 2

    for new_p in sim.new_part_buffer:
        assert np.array_equal(new_p.position, p.position)
        assert np.array_equal(new_p.velocity, p.velocity)
