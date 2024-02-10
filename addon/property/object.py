import bpy

from bpy.types import PropertyGroup, Object
from bpy.props import *

from . utility import names


def sync_state(option, context):
    option.solidify_state = option.solidify


class option(PropertyGroup):
    target: PointerProperty(type=Object)
    shape: BoolProperty()
    slice: BoolProperty()
    applied: BoolProperty()
    applied_cycle: BoolProperty()
    inset: BoolProperty()
    copy: BoolProperty()

    array: BoolProperty()
    array_circle: BoolProperty()

    array_axis: EnumProperty(
        name = names['array_axis'],
        description = 'Default Axis',
        items = [
            ('X', 'X', '\n X axis'),
            ('Y', 'Y', '\n Y axis'),
            ('Z', 'Z', '\n Z axis')],
        default = 'X')

    solidify: BoolProperty(update=sync_state)
    solidify_state: BoolProperty()
    bevel: BoolProperty()
    mirror: BoolProperty()
