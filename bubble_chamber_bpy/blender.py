"""
isort:skip_file
"""
from pathlib import Path
import site
import subprocess
from random import uniform, randint


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

from bubble_chamber_bpy.models import BubbleChamber, Particle
from bubble_chamber_bpy.simulation import Simulation
from bubble_chamber_bpy import render as r


CHAMBER_SIZE = 20
chamber = BubbleChamber(
    [CHAMBER_SIZE, CHAMBER_SIZE, CHAMBER_SIZE], [0.0, 0.0, 2.0], 0.3
)
# Let's spawn a particle in every corner of the chamber, flying inward
particles = [
    Particle(
        [x * CHAMBER_SIZE / 2, y * CHAMBER_SIZE / 2, z * CHAMBER_SIZE / 2],
        [uniform(-5.0, -2.0) * x, uniform(-5.0, -2.0) * y, uniform(-5.0, -2.0) * z],
        [randint(1, 5), randint(1, 5), randint(1, 5)],
    )
    for x in (-1, 1)
    for y in (-1, 1)
    for z in (-1, 1)
]
simulation = Simulation(chamber, particles, time_modifier=0.5)


r.clear_all()
r.create_world()
r.create_chamber(chamber)
r.create_particles(particles)
r.create_camera(chamber)
r.create_renderer()
r.run_simulation(simulation)
