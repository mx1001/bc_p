import bpy
from mathutils import Vector, Matrix

from . import addon, math


def duplicate(obj, name='', link=None):
    duplicate = obj.copy()
    duplicate.data = obj.data.copy()

    if name:
        duplicate.name = name
        duplicate.data.name = name

    if link:
        link.objects.link(duplicate)

    return duplicate


def center(obj, matrix=Matrix()):
    return 0.125 * math.vector_sum(bound_coordinates(obj, matrix=matrix))


def bound_coordinates(obj, matrix=Matrix()):
    return [matrix @ Vector(coord) for coord in obj.bound_box]


def apply_transforms(obj):
    obj.data.transform(obj.matrix_world)
    clear_transforms(obj)


def clear_transforms(obj):
    obj.matrix_world = Matrix()


def parent(obj, target):
    obj.parent = target
    obj.matrix_parent_inverse = target.matrix_world.inverted()
