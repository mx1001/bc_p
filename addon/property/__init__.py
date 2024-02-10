import bpy

from mathutils import Vector, Matrix
from bpy.utils import register_class, unregister_class
from bpy.types import PropertyGroup, Object, Collection
from bpy.props import *

from . import data, last, object, scene, snap, preference
from . utility import update
from ... utility import addon


class new:
    datablock = {
        'targets': [],
        'wire_targets': [],
        'overrides': [],
        'dimensions': Vector((0, 0, 0)),
        'slices': [],
        'operator': None,
        'duplicate': None,
        'plane': None,
        'box': None,
        'modifier': {
            'bevel': []}}

    ray_cast = {
        'location': Vector((0, 0, 0)),
        'normal': Vector((0, 0, 0))}

    start = {
        'alignment': '',
        'mouse': Vector(),
        'matrix': Matrix(),
        'mode': 'CUT',
        'operation': 'NONE',
        'location': Vector(),
        'extrude': 0.0,
        'offset': 0.0,
        'displace': 0.0}

    geo = {
        'points': [],
        'verts': [],
        'edges': [],
        'faces': [],
        'indices': {
            'extrusion': [],
            'bot_edge': [],
            'top_edge': [],
            'mid_edge': []}}

    mouse = {
        'location': Vector(),
        'intersect': Vector()}

    view3d = {
        'origin': Vector(),
        'location': Vector()}

    verts = [
        Vector((-1.0,   -1.0,   -0.04)),  Vector((1.0,    -1.0,   -0.04)),
        Vector((-1.0,    1.0,   -0.04)),  Vector((1.0,     1.0,   -0.04)),
        Vector((-0.859,  0.859, -0.04)),  Vector((-0.859, -0.859, -0.04)),
        Vector((0.859,  -0.859, -0.04)),  Vector((0.859,   0.859, -0.04)),
        Vector((-0.657,  0.657, -0.04)),  Vector((-0.657, -0.657, -0.04)),
        Vector((0.657,  -0.657, -0.04)),  Vector((-0.307,  0.307, -0.04)),
        Vector((0.307,  -0.307, -0.04)),  Vector((0.307,   0.307, -0.04)),
        Vector((0.213,   0.213, -0.04)),  Vector((-0.213,  0.213, -0.04)),
        Vector((0.213,  -0.213, -0.04)),  Vector((-1.056, -1.056, -0.366)),
        Vector((-1.056, -1.056,  0.05)),  Vector((-1.056,  1.056, -0.366)),
        Vector((-1.056,  1.056,  0.05)),  Vector((1.056,  -1.056, -0.366)),
        Vector((1.056,  -1.056,  0.05)),  Vector((1.056,   1.056, -0.366)),
        Vector((1.056,   1.056,  0.05)),  Vector((1.0,    -1.0,   -0.366)),
        Vector((-1.0,   -1.0,   -0.366)), Vector((0.859,  -0.859, -0.366)),
        Vector((-0.859, -0.859, -0.366)), Vector((0.307,  -0.307, -0.366)),
        Vector((0.657,  -0.657, -0.366)), Vector((-0.657, -0.657, -0.366)),
        Vector((0.213,  -0.213, -0.366)), Vector((-0.213,  0.213, -0.366)),
        Vector((-0.307,  0.307, -0.366)), Vector((0.307,   0.307, -0.366)),
        Vector((0.213,   0.213, -0.366)), Vector((-0.657,  0.657, -0.366)),
        Vector((0.307,   0.129, -0.366)), Vector((0.859,   0.859, -0.366)),
        Vector((-0.859,  0.859, -0.366)), Vector((-1.0,    1.0,   -0.366)),
        Vector((1.0,     1.0,   -0.366))]

    edges = [
        (4,  5),  (5,  6),  (6,  7),  (7,  4),
        (2,  0),  (0,  1),  (1,  3),  (3,  2),
        (19, 41), (4,  2),  (1,  6),  (14, 15),
        (12, 13), (13, 11), (15, 11), (8,  9),
        (11, 8),  (9,  10), (10, 12), (12, 16),
        (14, 16), (19, 17), (17, 18), (18, 20),
        (20, 19), (23, 19), (20, 24), (24, 23),
        (21, 23), (24, 22), (22, 21), (17, 21),
        (22, 18), (26, 25), (27, 28), (30, 29),
        (31, 30), (32, 33), (35, 34), (33, 36),
        (34, 37), (37, 31), (29, 38), (38, 35),
        (40, 39), (28, 40), (39, 27), (25, 42),
        (41, 26), (42, 41), (9,  31), (1,  25),
        (13, 35), (6,  27), (3,  42), (15, 33),
        (8,  37), (0,  26), (12, 29), (5,  28),
        (10, 30), (2,  41), (14, 36), (7,  39),
        (11, 34), (4,  40), (25, 21), (30, 27),
        (37, 40), (16, 15), (36, 32), (16, 32)]

    faces = [
        (15, 16, 12, 10, 9, 8, 11), (26, 25, 21, 17, 19, 41),
        (6, 1, 0, 2, 4, 5), (4, 2, 3, 1, 6, 7),
        (4, 40, 28, 5), (5, 28, 27, 6), (6, 27, 39, 7),
        (7, 39, 40, 4), (0, 26, 41, 2), (1, 25, 26, 0),
        (3, 42, 25, 1), (2, 41, 42, 3), (14, 36, 33, 15),
        (15, 33, 32, 16), (13, 35, 38, 29, 12), (11, 34, 35, 13),
        (9, 31, 37, 8), (8, 37, 34, 11), (10, 30, 31, 9),
        (12, 29, 30, 10), (16, 32, 36, 14), (17, 18, 20, 19),
        (19, 20, 24, 23), (23, 24, 22, 21), (21, 22, 18, 17),
        (19, 23, 21, 25, 42, 41), (24, 20, 18, 22),
        (13, 12, 16, 14, 15, 11), (30, 29, 38, 35, 34, 37, 40, 39, 27),
        (33, 36, 32), (27, 28, 40, 37, 31, 30)]


class option(PropertyGroup):
    # running: BoolProperty()
    addon: StringProperty(default=addon.name)


classes = [
    data.option,
    last.option,
    object.option,
    snap.option,
    scene.option,
    option]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.bc = PointerProperty(type=option)
    bpy.types.Object.bc = PointerProperty(type=object.option)
    bpy.types.Mesh.bc = PointerProperty(type=data.option)
    bpy.types.Lattice.bc = PointerProperty(type=data.option)
    bpy.types.Scene.bc = PointerProperty(type=scene.option)


def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.WindowManager.bc
    del bpy.types.Object.bc
    del bpy.types.Mesh.bc
    del bpy.types.Lattice.bc
    del bpy.types.Scene.bc
