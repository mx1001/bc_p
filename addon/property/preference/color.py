import bpy

from bpy.types import PropertyGroup
from bpy.props import *

from ... property.utility import names


class bc(PropertyGroup):

    cut: FloatVectorProperty(
        name = names['cut'],
        description = '\n Color of the shape when cutting',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        # default = (0.604, 0.064, 0.064, 0.1))
        default = (0.448, 0.147, 0.147, 0.4))

    slice: FloatVectorProperty(
        name = names['slice'],
        description = '\n Color of the shape when slicing',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        # default = (0.604, 0.422, 0.064, 0.1))
        default = (0.604, 0.557, 0.228, 0.5))

    intersect: FloatVectorProperty(
        name = names['intersect'],
        description = '\n Color of the shape when intersecting',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        # default = (0.236, 0.064, 0.604, 0.1))
        default = (0.593, 0.321, 0.158, 0.6))

    inset: FloatVectorProperty(
        name = names['inset'],
        description = '\n Color of the shape when insetting',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        # default = (0.236, 0.064, 0.604, 0.1))
        default = (0.391, 0.223, 0.692, 0.5))

    join: FloatVectorProperty(
        name = names['join'],
        description = '\n Color of the shape when joining',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        # default = (0.217, 0.604, 0.064, 0.1))
        default = (0.286, 0.604, 0.133, 0.4))

    make: FloatVectorProperty(
        name = names['make'],
        description = '\n Color of the shape when making',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        # default = (0.604, 0.604, 0.604, 0.1))
        default = (0.604, 0.604, 0.604, 0.5))

    knife: FloatVectorProperty(
        name = names['knife'],
        description = '\n Color of the shape when using knife',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        # default = (0.29, 0.52, 1.0, 0.1))
        default = (0.238, 0.411, 0.787, 0.4))

    extract: FloatVectorProperty(
        name = names['extract'],
        description = '\n Color of the shape when extracting',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.033, 0.033, 0.033, 0.3))

    negative: FloatVectorProperty(
        name = names['negative'],
        description = '\n Color of the shape when behind a mesh object',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.214, 0.214, 0.214, 0.1))

    # bbox: FloatVectorProperty(
    #     name = names['bbox'],
    #     description = '\n Color of the shapes bound region',
    #     size = 4,
    #     min = 0,
    #     max = 1,
    #     subtype='COLOR',
    #     default = (0.1, 0.1, 0.1, 0.033))

    wire: FloatVectorProperty(
        name = names['wire'],
        description = '\n Color of the shape\'s wire',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.0, 0.0, 0.0, 0.5))

    grid: FloatVectorProperty(
        name = names['grid'],
        description = '\n Color of the grid',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.2, 0.2, 0.2, 0.2))

    grid_use_mode: BoolProperty(
        name = names['grid_use_mode'],
        description = '\n Change the grid to match the shape mode',
        default = True)

    grid_wire: FloatVectorProperty(
        name = names['grid_wire'],
        description = '\n Color of the grid\'s wire',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1.0, 1.0, 1.0, 0.33))

    show_shape_wire: FloatVectorProperty(
        name = names['show_shape_wire'],
        description = '\n Color of the shape\'s wire when the object is to be shown',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.23, 0.7, 0.15, 0.33))

    snap_point: FloatVectorProperty(
        name = names['snap_point'],
        description = '\n Color of snapping points',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1.0, 1.0, 1.0, 0.4))

    snap_point_highlight: FloatVectorProperty(
        name = names['snap_point_highlight'],
        description = '\n Color of snapping points highlighted',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1.0, 0.02, 0.0, 0.7))

    dot: FloatVectorProperty(
        name = names['dot'],
        description = '\n Color of operation dots',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.0, 0.0,0.0, 0.33))

    dot_bevel: FloatVectorProperty(
        name = names['dot_bevel'],
        description = '\n Color of bevel operation dots',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.2, 0.3,1.0, 0.4))

    dot_highlight: FloatVectorProperty(
        name = names['dot_highlight'],
        description = '\n Color operation dots highlighted',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1.0, 1.0, 1.0, 0.65))

    reduce_opacity_editmode: BoolProperty(
        name = names['reduce_opacity_editmode'],
        description = '\n Reduce opacity of shapes when in edit mode',
        default = True)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')



def draw(preference, context, layout):
    label_row(preference.color, 'cut', layout.row())
    label_row(preference.color, 'slice', layout.row())
    label_row(preference.color, 'intersect', layout.row())
    label_row(preference.color, 'inset', layout.row())
    label_row(preference.color, 'join', layout.row())
    label_row(preference.color, 'make', layout.row())
    label_row(preference.color, 'knife', layout.row())
    label_row(preference.color, 'extract', layout.row())
    label_row(preference.color, 'wire', layout.row())
    label_row(preference.color, 'negative', layout.row())

    row = layout.row()
    split = row.split(factor=0.5)
    split.label(text=names['grid'])
    sub = split.row(align=True)
    sub.prop(preference.color, 'grid', text='')
    sub.prop(preference.color, 'grid_use_mode', text='', icon='UV_SYNC_SELECT')

    label_row(preference.color, 'grid_wire', layout.row())
    label_row(preference.color, 'show_shape_wire', layout.row())
    label_row(preference.color, 'snap_point', layout.row())
    label_row(preference.color, 'snap_point_highlight', layout.row())
    label_row(preference.color, 'dot', layout.row())
    label_row(preference.color, 'dot_bevel', layout.row())
    label_row(preference.color, 'dot_highlight', layout.row())
    label_row(preference.color, 'reduce_opacity_editmode', layout.row())
