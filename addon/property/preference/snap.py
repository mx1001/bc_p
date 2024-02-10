import bpy

from bpy.types import PropertyGroup
from bpy.props import *

from ... property.utility import names

last_grid_unit = 0
def even_grid_units(snap, context):
    global last_grid_unit

    if not last_grid_unit:
        last_grid_unit = snap.grid_units

    if snap.grid_units != 0 and snap.grid_units % 2 != 0:
        if last_grid_unit <= snap.grid_units:
            snap['grid_units'] = snap.grid_units + 1
        else:
            snap['grid_units'] = snap.grid_units - 1

    last_grid_unit = snap.grid_units


def enable_snap_grid(snap, context):
    enable_snap(snap, snap.grid)


def enable_snap_verts(snap, context):
    enable_snap(snap, snap.verts)


def enable_snap_edges(snap, context):
    enable_snap(snap, snap.edges)


def enable_snap_faces(snap, context):
    enable_snap(snap, snap.faces)


def enable_snap(snap, prop):
    if not snap.enable and prop:
        snap.enable = True

    if not snap.grid and not snap.verts and not snap.edges and not snap.faces:
        snap.enable = False


class bc(PropertyGroup):
    enable: BoolProperty(
        name = 'Snap',
        description = '\n Snap points when holding CTRL',
        default = False)

    incremental: BoolProperty(
        name = 'Snap Incremental',
        description = '\n Snap to increments',
        default = False)

    increment: FloatProperty(
        name = 'Increment Amount',
        description = '\n Snap increment amount',
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.25)

    increment_lock: BoolProperty(
        name = 'Increment Lock',
        description = '\n Snap increment without holding CTRL',
        default = False)

    angle_lock: BoolProperty(
        name = 'Angle Lock',
        description = '\n Snap angle lock without holding CTRL',
        default = False)

    # smart_grid_increment: IntProperty(
    #     name = 'Smart Grid Increment Amount',
    #     description = 'Smart Grid increment amount',
    #     min = 2,
    #     soft_max = 50,
    #     max = 100,
    #     default =5)

    # snap_smart_grid: BoolProperty(
    #     name = 'Snap Smart Grid',
    #     description = 'Snap to face grid',
    #     default = False)

    grid: BoolProperty(
        name = 'Snap Grid',
        description = '\n Display and snap to grid',
        update = enable_snap_grid,
        default = False)

    grid_units: IntProperty(
        name = 'Grid Units Span',
        description = '\n Number of grid rows and columns to display.\n'
                      ' Note - At the cost of performance',
        update = even_grid_units,
        min = 0,
        soft_max = 20,
        max = 100,
        default = 10)

    grid_off_face: BoolProperty(
        name = 'Grid Off Face',
        description = '\n Do not actively change the snap target face when the grid and other snap types are active simultaneously',
        default = False)

    grid_relative_size: BoolProperty(
        name = 'Grid Relative Size',
        description = '\n Size grid relative to target when applicable',
        default = False)

    verts: BoolProperty(
        name = 'Snap Vertices',
        description = '\n Snap to verts',
        update = enable_snap_verts,
        default = True)

    edges: BoolProperty(
        name = 'Snap Edges',
        description = '\n Snap to mid points of edges',
        update = enable_snap_edges,
        default = True)

    faces: BoolProperty(
        name = 'Snap Faces',
        description = '\n Snap to face centers',
        update = enable_snap_faces,
        default = True)

    fade_distance: FloatProperty(
        name = 'Fade Distance',
        description = '\n Distance to Fade snapping points',
        soft_min = 0.1,
        soft_max = 10,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 1.4)

    rotate_angle: IntProperty(
        name = names['rotate_angle'],
        description = '\n Snap angle when rotating',
        min = 1,
        soft_max = 90,
        max = 360,
        subtype = 'ANGLE',
        default = 15)

    ngon_angle: IntProperty(
        name = names['ngon_angle'],
        description = '\n Snap angle when using ngon',
        min = 1,
        soft_max = 45,
        max = 180,
        subtype = 'ANGLE',
        default = 15)

    line_box_angle: IntProperty(
        name = names['line_box_angle'],
        description = '\n Snap angle when using line_box',
        min = 1,
        max = 45,
        subtype = 'ANGLE',
        default = 15)
