import bpy

from bpy.types import PropertyGroup, Object, Collection
from bpy.props import *

from . import last, snap
from . utility import update


def custom_object(option, obj):
    return obj.type in {'MESH', 'FONT'}


class option(PropertyGroup):
    running: BoolProperty()
    q_bevel: BoolProperty()
    location: FloatVectorProperty()
    mirror_axis: IntVectorProperty(default=(0, 0, 0))
    mirror_axis_flip: IntVectorProperty(default=(0, 0, 0))
    stored_collection: PointerProperty(type=Collection)
    stored_shape: PointerProperty(type=Object)
    rotated_inside: IntProperty()

    axis: EnumProperty(
        items = [
            ('NONE', 'None', 'Use default behavior'),
            ('X', 'X', 'Modal Shortcut: X'),
            ('Y', 'Y', 'Modal Shortcut: Y'),
            ('Z', 'Z', 'Modal Shortcut: Z')],
        default = 'NONE')
    flip: BoolProperty()

    # TODO: break into bools
    start_operation: EnumProperty(
        name = 'Start Operation',
        description = '\n Start with the previously used settings of operation',
        update = update.change_start_operation,
        items = [
            ('NONE', 'None', '\n Default State (no modifier)', 'REC', 0),
            ('ARRAY', 'Array', '\n Starts drawing with Array active', 'MOD_ARRAY', 1),
            ('SOLIDIFY', 'Solidify', '\n Starts drawing with Solidify active', 'MOD_SOLIDIFY', 2),
            ('BEVEL', 'Bevel', '\n Starts drawing with Bevel active', 'MOD_BEVEL', 3),
            ('MIRROR', 'Mirror', '\n Starts drawing with Mirror active', 'MOD_MIRROR', 4)],
        default = 'NONE')

    cyclic: BoolProperty(
        name = 'Cyclic',
        description = '\n Connect the final point of the NGon with the first point',
        default = True)

    original_active: PointerProperty(type=Object)
    lattice: PointerProperty(type=Object)
    slice: PointerProperty(type=Object)
    inset: PointerProperty(type=Object)
    plane: PointerProperty(type=Object)
    empty: PointerProperty(type=Object)

    snap: PointerProperty(type=snap.option)
    last: PointerProperty(type=last.option)

    collection: PointerProperty(
        name = 'Collection',
        description = '\n Assign collection for shape objects',
        update = update.store_collection,
        type = Collection)

    shape: PointerProperty(
        name = 'Shape',
        description = '\n Assign shape object',
        poll = custom_object,
        update = update.store_shape,
        type = Object)
