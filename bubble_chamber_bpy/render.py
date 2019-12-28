from typing import Sequence

import bpy
import numpy as np

from bubble_chamber_bpy.models import BubbleChamber, Particle
from bubble_chamber_bpy.simulation import Simulation


def clear_all():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.context.scene.frame_set(0)


def create_chamber(chamber: BubbleChamber):
    print("Creating bubble chamber")
    size = np.max(chamber.dimensions)
    bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, 0))
    chamber_bpy = bpy.context.object
    chamber_bpy.name = "Chamber"
    chamber_bpy.display_type = "WIRE"


def create_particles(particles: Sequence[Particle]):
    print("Creating particles")
    for i, p in enumerate(particles):
        get_or_create_particle(p, i)


def create_camera(chamber: BubbleChamber):
    print("Creating camera")
    # TODO: Make this less random:
    bpy.ops.object.camera_add(location=(0, 0, chamber.dimensions[2] * 2))
    cam = bpy.context.object
    bpy.context.scene.camera = cam


def create_light(chamber: BubbleChamber):
    print("Creating light")
    bpy.ops.object.light_add(type="SUN", location=(0, 0, chamber.dimensions[2]))


def run_simulation(simulation: Simulation):
    FPS = 30

    simulation.start()
    frame = 0
    while any(p.is_alive for p in simulation.particles):
        # Advance the simulation by 1 step:
        simulation.step()

        # Current frame is the total time passed in sim * FPS
        frame = int(simulation.time_passed * FPS)
        bpy.context.scene.frame_set(frame)

        for i, p in enumerate(simulation.particles):
            obj = get_or_create_particle(p, i)

            if p.is_alive:
                obj.location = p.position
                obj.keyframe_insert(data_path="location")
            elif p.is_dirty:
                p.is_dirty = False
                obj.location = p.position
                obj.keyframe_insert(data_path="location")
                # obj.hide_viewport = True
                # obj.keyframe_insert(data_path="hide_viewport")
                obj.hide_render = True
                obj.keyframe_insert(data_path="hide_render")


def get_or_create_particle(p: Particle, i: int):
    name = f"Particle {i}"
    obj = bpy.data.objects.get(name)

    if not obj:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=p.position)
        obj = bpy.context.object
        obj.name = name

        # Ensure the particle is visible:
        obj.location = p.position
        obj.keyframe_insert(data_path="location")
        # obj.hide_viewport = False
        # obj.keyframe_insert(data_path="hide_viewport")
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_render")

        # Assign the material:
        mat = get_or_create_material(p)
        obj.data.materials.append(mat)

    return obj


def get_or_create_material(p: Particle):
    name = "Material Particle"

    obj = bpy.data.materials.get(name)

    if not obj:
        obj = bpy.data.materials.new(name=name)
        obj.diffuse_color = (100.0, 100.0, 100.0, 100.0)

    return obj
