import bpy

from bpy.types import PropertyGroup
from bpy.props import *

from . utility import update
from ... operator.shape.utility import change
from ... property.utility import names


class bc(PropertyGroup):

    offset: FloatProperty(
        name = names['offset'],
        description = 'Shape offset along z axis',
        update = change.offset,
        precision = 3,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.005)

    lazorcut_limit: FloatProperty(
        name = names['lazorcut_limit'],
        description = '\n How thin the shape must be before triggering a lazorcut cut',
        precision = 3,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.005)

    lazorcut_depth: FloatProperty(
        name = names['lazorcut_depth'],
        description = 'Extent to extend the cutters depth when using Accucut (Behavior) Lazorcut',
        precision = 3,
        min = 0,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0)

    circle_vertices: IntProperty(
        name = names['circle_vertices'],
        description = '\n Bevel segments',
        update = change.circle_vertices,
        min = 1,
        soft_max = 32,
        max = 128,
        default = 32)

    inset_thickness: FloatProperty(
        name = names['inset_thickness'],
        description = '\n Shape inset thickness',
        update = change.inset_thickness,
        precision = 4,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.02)

    array_count: IntProperty(
        name = names['array_count'],
        description = '\n Array count',
        update = change.array_count,
        min = 1,
        soft_max = 32,
        default = 2)

    solidify_thickness: FloatProperty(
        name = names['solidify_thickness'],
        description = '\n Shape solidify thickness',
        update = change.solidify_thickness,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        precision = 4,
        default = 0.01)

    bevel_width: FloatProperty(
        name = names['bevel_width'],
        description = '\n Bevel width',
        update = change.bevel_width,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        min = 0,
        precision = 3,
        default = 0.02)

    bevel_segments: IntProperty(
        name = names['bevel_segments'],
        description = '\n Bevel segments',
        update = change.bevel_segments,
        min = 1,
        soft_max = 20,
        max = 100,
        default = 6)

    bevel_segments_default: IntProperty(
        name = names['bevel_segments'],
        description = '\n Bevel segments default value',
        # update = change.bevel_segments, # TODO: exec set bevel segments
        min = 1,
        soft_max = 20,
        max = 100,
        default = 6)

    quad_bevel: BoolProperty(
        name = names['quad_bevel'],
        description = '\n Use two bevel modifiers to achieve better corner topology',
        update = change.quad_bevel,
        default = True)

    straight_edges: BoolProperty(
        name = names['straight_edges'],
        description = '\n Use a series of bevel modifiers to provide straight edge flow in corners',
        update = change.straight_edges,
        default = False)

    rotate_axis: EnumProperty(
        name = names['rotate_axis'],
        description = 'Default Axis',
        items = [
            ('X', 'X', '\n X axis'),
            ('Y', 'Y', '\n Y axis'),
            ('Z', 'Z', '\n Z axis')],
        default = 'Z')

    array_axis: EnumProperty(
        name = names['array_axis'],
        description = 'Default Axis',
        items = [
            ('X', 'X', '\n X axis'),
            ('Y', 'Y', '\n Y axis'),
            ('Z', 'Z', '\n Z axis')],
        default = 'X')

    array_around_cursor: BoolProperty(
        name = names['array_around_cursor'],
        description = '\n Use the 3D Cursor when Circle Arraying',
        default = False)

    cycle_all: BoolProperty(
        name = names['cycle_all'],
        description = '\n Do not skip cutters available in the collection when cycling',
        default = True)

    wedge: BoolProperty(
        name = names['wedge'],
        description = '\n Use a wedge when line box cutting',
        default = False)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.shape, 'offset', layout.row())
    label_row(preference.shape, 'lazorcut_limit', layout.row())

    layout.separator()

    label_row(preference.shape, 'rotate_axis', layout.row())

    layout.separator()


    label_row(preference.shape, 'circle_vertices', layout.row())

    layout.separator()

    label_row(preference.shape, 'inset_thickness', layout.row())

    layout.separator()

    label_row(preference.shape, 'array_count', layout.row())
    label_row(preference.shape, 'array_axis', layout.row())
    # label_row(preference.shape, 'array_around_cursor', layout.row())

    layout.separator()

    label_row(preference.shape, 'solidify_thickness', layout.row())

    layout.separator()

    label_row(preference.shape, 'bevel_width', layout.row())
    # label_row(preference.shape, 'bevel_segments', layout.row())
    label_row(preference.shape, 'bevel_segments_default', layout.row(), label=names['bevel_segments'])
    label_row(preference.shape, 'quad_bevel', layout.row())
    label_row(preference.shape, 'straight_edges', layout.row())
