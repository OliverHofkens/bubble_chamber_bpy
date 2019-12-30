import colorsys
import math
from contextlib import contextmanager
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
    chamber_bpy.hide_render = True

    # Add a force field to influence the particles:
    bpy.ops.object.effector_add(type="TURBULENCE", radius=size, location=(0, 0, 0))
    field = bpy.context.object
    field.name = "Turbulence and Flow"
    field.field.flow = 8.0
    field.field.strength = 0.0


def create_particles(particles: Sequence[Particle]):
    print("Creating particles")
    for i, p in enumerate(particles):
        get_or_create_particle(p, i)


def create_world():
    world = bpy.data.worlds["World"]
    world.use_nodes = False
    world.color = (0, 0, 0)


def create_renderer():
    scene = bpy.data.scenes["Scene"]
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_bloom = True
    scene.eevee.use_gtao = True
    scene.eevee.use_ssr = True


def create_camera(chamber: BubbleChamber):
    print("Creating camera")
    # Add a path for the camera to track:
    bpy.ops.curve.primitive_nurbs_circle_add(
        radius=np.max(chamber.dimensions), rotation=(math.radians(45), 0, 0)
    )
    path = bpy.context.object
    path.name = "Camera Path"
    camera_curve = bpy.data.curves[0]
    camera_curve.name = "Camera Path Curve"
    camera_curve.eval_time = 0
    camera_curve.keyframe_insert(data_path="eval_time")

    # Create the actual camera, the location is already constrained to the path
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    bpy.context.scene.camera = cam

    # Lock the camera to the path:
    bpy.ops.object.constraint_add(type="FOLLOW_PATH")
    clamp = cam.constraints["Follow Path"]
    clamp.target = path

    # Always track the origin of the chamber:
    bpy.ops.object.constraint_add(type="TRACK_TO")
    tracker = cam.constraints["Track To"]
    tracker.target = bpy.data.objects["Chamber"]
    tracker.track_axis = "TRACK_NEGATIVE_Z"
    tracker.up_axis = "UP_Y"


def create_vapor_particle(name: str, material):
    print("Creating vapor particle")
    bpy.ops.mesh.primitive_cube_add()
    vapor_part = bpy.context.object
    vapor_part.name = name
    vapor_part.hide_viewport = True
    vapor_part.hide_render = True
    vapor_part.data.materials.append(material)


def run_simulation(simulation: Simulation):
    FPS = 30

    simulation.start()
    frame = 0
    scene = bpy.context.scene
    while any(p.is_dirty for p in simulation.particles):
        # Advance the simulation by 1 step:
        simulation.step()

        # Current frame is the total time passed in sim * FPS
        frame = int(simulation.time_passed * FPS)
        scene.frame_set(frame)

        for i, p in enumerate(simulation.particles):
            obj = get_or_create_particle(p, i)

            if p.is_alive:
                set_visibility(obj, True)
                obj.location = p.position
                obj.keyframe_insert(data_path="location")
            elif p.is_dirty:
                p.is_dirty = False
                obj.location = p.position
                obj.keyframe_insert(data_path="location")
                # Hiding the object also hides the particles:
                # set_visibility(obj, False)

                if p.total_charge != 0:
                    set_instancer_visibility(obj, False)
                    obj.particle_systems[0].settings.frame_end = scene.frame_current

    # End of simulation, update animation scene:
    scene.frame_end = frame
    cam_curve = bpy.data.curves["Camera Path Curve"]
    cam_curve.path_duration = frame
    cam_curve.eval_time = frame
    cam_curve.keyframe_insert(data_path="eval_time")


def get_or_create_particle(p: Particle, i: int):
    name = f"Particle {i}"
    obj = bpy.data.objects.get(name)

    if not obj:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01, location=p.position)
        obj = bpy.context.object
        obj.name = name

        # Ensure the particle is visible starting at this frame:
        obj.location = p.position
        obj.keyframe_insert(data_path="location")
        # obj.hide_viewport = False
        # obj.keyframe_insert(data_path="hide_viewport")
        with at_frame(0):
            set_visibility(obj, False)
            set_instancer_visibility(obj, False)
        set_visibility(obj, True)
        set_instancer_visibility(obj, True)

        # Assign the material:
        mat = get_or_create_material(p)
        obj.data.materials.append(mat)

        # Particle system if the particle is charged:
        if p.total_charge != 0:
            bpy.ops.object.particle_system_add()
            particles = obj.particle_systems[0]
            particles.name = f"{name} Particles"
            particles.settings.frame_start = bpy.context.scene.frame_current
            particles.settings.count = 2000
            particles.settings.particle_size = 0.005
            particles.settings.size_random = 1.0
            particles.settings.lifetime = 1000.0
            particles.settings.normal_factor = 0.3
            particles.settings.effector_weights.gravity = 0.0

            vapor_name = particles.name + " Vapor"
            create_vapor_particle(vapor_name, mat)
            particles.settings.render_type = "OBJECT"
            particles.settings.instance_object = bpy.data.objects[vapor_name]

    return obj


def get_or_create_material(p: Particle):
    name = "Material Particle"

    obj = bpy.data.materials.new(name=name)
    obj.use_nodes = True

    # Add an emission node:
    node_tree = obj.node_tree
    material_out = node_tree.nodes["Material Output"]

    # Delete default shader node:
    for n in node_tree.nodes:
        if n != material_out:
            node_tree.nodes.remove(n)

    emission = node_tree.nodes.new(type="ShaderNodeEmission")
    emission.inputs["Color"].default_value = color_for_particle(p)
    emission.inputs["Strength"].default_value = 3.0
    node_tree.links.new(
        emission.outputs[0], node_tree.get_output_node(target="ALL").inputs[0]
    )

    return obj


def color_for_particle(p: Particle, with_alpha: bool = True):
    # charge = p.total_charge
    # hue = 0 if charge >= 0 else 0.60
    # saturation = abs(charge) / (p.mass * 0.8)
    # value = 0.8
    rgb = colorsys.hsv_to_rgb(0.6, 0.6, 0.8)

    if with_alpha:
        alpha = 1.0
        return (*rgb, alpha)
    else:
        return rgb


def set_visibility(obj, vis: bool):
    hide = not vis
    if obj.hide_render != hide:
        obj.hide_render = hide
        obj.keyframe_insert(data_path="hide_render")


def set_instancer_visibility(obj, vis: bool):
    if obj.show_instancer_for_render != vis:
        obj.show_instancer_for_render = vis
        obj.keyframe_insert(data_path="show_instancer_for_render")


@contextmanager
def at_frame(frame: int):
    current_frame = bpy.context.scene.frame_current
    bpy.context.scene.frame_set(frame)
    yield
    bpy.context.scene.frame_set(current_frame)
