"""
isort:skip_file
"""
import site
import subprocess
from pathlib import Path
from typing import Sequence


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

import numpy as np

import bpy
from bubble_chamber_bpy.models import BubbleChamber, Particle
from bubble_chamber_bpy.simulation import Simulation

chamber = BubbleChamber(np.array([100.0, 100.0, 100.0]), np.array([0.0, 0.0, 2.0]), 0.3)
particles = [
    Particle(
        np.array([-100.0, 0.0, 0.0]),
        np.array([10.0, 0.0, 0.0]),
        np.array([10, 20, 10]),
        0.0,
        5.0,
    )
]
simulation = Simulation(chamber, particles)


def setup(simulation: Simulation):
    clear_all()
    _create_chamber(simulation.chamber)
    _create_particles(simulation.particles)


def clear_all():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def _create_chamber(chamber: BubbleChamber):
    print("Creating bubble chamber")
    size = np.max(chamber.dimensions)
    bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, 0))
    chamber_bpy = bpy.context.object
    chamber_bpy.name = "Chamber"
    chamber_bpy.display_type = "WIRE"


def _create_particles(particles: Sequence[Particle]):
    print("Creating particles")
    for i, p in enumerate(particles):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=p.position)
        p_bpy = bpy.context.object
        p_bpy.name = f"Particle {i}"


setup(simulation)
