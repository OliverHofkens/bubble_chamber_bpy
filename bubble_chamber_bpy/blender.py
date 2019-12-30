"""
isort:skip_file
"""
from pathlib import Path
import site
import subprocess


def find_deps():
    """Add our virtualenv to Blender's PYTHONPATH so we can import dependencies"""
    proj_dir = Path(__file__).parent.parent
    proc = subprocess.run(
        ["pipenv", "--venv"],
        cwd=str(proj_dir),
        check=True,
        capture_output=True,
        text=True,
    )
    venv_path = Path(proc.stdout.strip()) / "lib" / "python3.8" / "site-packages"
    print(f"Importing virtualenv {venv_path}")
    site.addsitedir(str(venv_path))


find_deps()

import bpy
import numpy as np

from bubble_chamber_bpy.models import BubbleChamber, Particle
from bubble_chamber_bpy.simulation import Simulation
from bubble_chamber_bpy import render as r


CHAMBER_SIZE = 20
chamber = BubbleChamber(
    np.array([CHAMBER_SIZE, CHAMBER_SIZE, CHAMBER_SIZE]), np.array([0.0, 0.0, 2.0]), 0.3
)
particles = [
    Particle(
        np.array([-1 * CHAMBER_SIZE / 2, 0.0, 0.0]),
        np.array([5.0, 0.0, 0.0]),
        np.array([5, 5, 5]),
    ),
    Particle(
        np.array([CHAMBER_SIZE / 2, 0.0, CHAMBER_SIZE / 2]),
        np.array([-5.0, 2.0, -2.0]),
        np.array([2, 2, 2]),
    ),
]
simulation = Simulation(chamber, particles, time_modifier=0.5)


r.clear_all()
r.create_world()
r.create_chamber(chamber)
r.create_particles(particles)
r.create_camera(chamber)
r.create_renderer()
r.run_simulation(simulation)
