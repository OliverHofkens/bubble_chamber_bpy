import pytest

from bubble_chamber_bpy.models import Particle


@pytest.mark.parametrize(
    "charges,expected",
    [
        ((0, 0, 0), 0),
        ((1, 0, 0), 1),
        ((0, 0, 1), -1),
        ((0, 1, 0), 0),
        ((1, 1, 1), 0),
        ((5, 0, 1), 4),
    ],
)
def test_total_charge(charges, expected):
    particle = Particle((0, 0, 0), (0, 0, 0), charges, 0, 0)

    assert particle.total_charge == expected


@pytest.mark.parametrize(
    "charges,expected", [((0, 0, 0), 0), ((1, 1, 1), 3), ((5, 5, 5), 15)]
)
def test_mass(charges, expected):
    particle = Particle((0, 0, 0), (0, 0, 0), charges, 0, 0)

    assert particle.mass == expected
