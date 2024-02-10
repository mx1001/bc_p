import bpy

from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty

from . utility import update
from ... property.utility import names
from ... sound import time_code

class bc(PropertyGroup):

    tab: StringProperty(
        name = names['tab'],
        description = '\n Tab to display BoxCutter in',
        update = update.tab,
        default = 'BoxCutter')

    simple_topbar: BoolProperty(
        name = names['simple_topbar'],
        description = '\n Display Topbar in a simpler state',
        update = update.simple_topbar,
        default = True)

    snap: BoolProperty(
        name = names['snap'],
        description = '\n Display snap options in topbar',
        default = True)

    destructive_menu: BoolProperty(
        name = names['destructive_menu'],
        description = '\n Display menu for destructive behavior in topbar',
        default = True)

    mode_label: BoolProperty(
        name = names['mode_label'],
        description = '\n Display label for mode in topbar',
        default = True)

    shape_label: BoolProperty(
        name = names['shape_label'],
        description = '\n Display label for shape in topbar',
        default = True)

    operation_label: BoolProperty(
        name = names['operation_label'],
        description = '\n Display label for operation in topbar',
        default = True)

    surface_label: BoolProperty(
        name = names['surface_label'],
        description = '\n Display label for surface in topbar',
        default = True)

    wire_only: BoolProperty(
        name = names['wire_only'],
        description = '\n Display only wires for shapes',
        default = False)

    wire_width: IntProperty(
        name = names['wire_width'],
        description = '\n Width of drawn wire in pixels (DPI Factored)',
        subtype = 'PIXEL',
        default = 1)

    stipple_width: IntProperty(
        name = names['stipple_width'],
        description = '\n Width of drawn stipple wire in pixels (DPI Factored)',
        subtype = 'PIXEL',
        default = 2)

    thick_wire: BoolProperty(
        name = names['thick_wire'],
        description = '\n Increases the thickness of wires when displaying wires only',
        default = False)

    wire_size_factor: IntProperty(
        name = 'Size Multiplier',
        description = '\n Multiplier for thick wire setting',
        min = 2,
        soft_max = 5,
        default = 2)

    snap_dot_size: IntProperty(
        name = 'Snap Dot Size',
        description = '\n Snap dot size for snapping points',
        subtype = 'PIXEL',
        soft_min = 5,
        soft_max = 50,
        default = 5)

    dots: BoolProperty(
        name = names['dots'],
        description = '\n Display dots manipulator when in lock state',
        default = True)

    dot_size: IntProperty(
        name = 'Dot Size',
        description = '\n Operation dot size',
        subtype = 'PIXEL',
        soft_min = 5,
        soft_max = 50,
        default = 10)

    snap_dot_factor: IntProperty(
        name = 'Detection Size Factor',
        description = '\n Detection Size Factor',
        soft_min = 1,
        soft_max = 20,
        default = 2)

    dot_factor: IntProperty(
        name = 'Detection Size Factor',
        description = '\n Detection Size Factor',
        soft_min = 1,
        soft_max = 20,
        default = 2)

    dot_size_ngon: IntProperty(
        name = 'Dot Size Ngon',
        description = '\n Ngon dot size',
        subtype = 'PIXEL',
        soft_min = 5,
        soft_max = 50,
        default = 6)

    bounds: BoolProperty(
        name = names['bounds'],
        description = '\n Draw the bound box during the modal',
        default = True)

    topbar_pad: BoolProperty(
        name = 'Topbar Padding',
        description = '\n Add space between elements in the topbar',
        default = True)

    pad_menus: BoolProperty(
        name = 'Pad Menus',
        description = '\n Add padding around right most menu elements in the topbar',
        default = True)

    padding: IntProperty(
        name = 'Padding',
        description = '\n Padding amount to use in the topbar\n\n'
                      ' NOTE: If too high for your window the topbar will hide/collapse\n\n'
                      ' Manually enter numbers above 3',
        # min = 1,
        min = 0,
        soft_max = 3,
        default = 0)

    middle_pad: IntProperty(
        name = 'Middle',
        description = '\n Additional center padding amount to use in the topbar\n\n'
                      ' NOTE: If too high for your window the topbar will hide/collapse\n\n'
                      ' Manually enter numbers above 24',
        min = 0,
        soft_max = 24,
        default = 1)

    update_fps: IntProperty(
        name = 'Shader Update FPS',
        description = '\n Update the shader drawn at this frame rate',
        min = 1,
        soft_min = 10,
        soft_max = 60,
        default = 30)

    shape_fade_time_in: IntProperty(
        name = 'Shape',
        description = '\n Amount of time (milliseconds) it takes for the shape to fade in',
        min = 0,
        soft_max = 200,
        default = 0)

    shape_fade_time_out: IntProperty(
        name = 'Shape Exit',
        description = '\n Amount of time (milliseconds) it takes for the shape to fade out',
        min = 0,
        soft_max = 200,
        default = 0)

    dot_fade_time_in: IntProperty(
        name = 'Dot',
        description = '\n Amount of time (milliseconds) it takes for the dot widgets to fade in',
        min = 0,
        soft_max = 200,
        default = 100)

    dot_fade_time_out: IntProperty(
        name = 'Dot Exit',
        description = '\n Amount of time (milliseconds) it takes for the dot widgets to fade out',
        min = 0,
        soft_max = 200,
        default = 100)

    grid_fade_time_in: IntProperty(
        name = 'Grid',
        description = '\n Amount of time (milliseconds) it takes for the grid to fade in',
        min = 1,
        soft_max = 200,
        default = 10)

    grid_fade_time_out: IntProperty(
        name = 'Grid Exit',
        description = '\n Amount of time (milliseconds) it takes for the grid to fade out',
        min = 0,
        soft_max = 200,
        default = 60)

    sound_volume: IntProperty(
        name = 'Sound Volume',
        description = '\n Volume of sound for sound cutting',
        subtype = 'PERCENTAGE',
        min = 0,
        max = 100,
        default = 10)

def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.display, 'tab', layout.row())

    label_row(preference.display, 'update_fps', layout.row(), 'Shader Update FPS')

    layout.separator()

    label_row(preference.display, 'wire_only', layout.row())
    label_row(preference.display, 'thick_wire', layout.row())
    label_row(preference.display, 'wire_width', layout.row())
    label_row(preference.display, 'stipple_width', layout.row())

    if preference.display.wire_size_factor:
        label_row(preference.display, 'wire_size_factor', layout.row(), 'Wire Size Multiplier')

    layout.separator()

    label_row(preference.display, 'snap_dot_size', layout.row(), 'Snap Dot Size')
    label_row(preference.display, 'snap_dot_factor', layout.row(), 'Snap Dot Detection Factor')
    label_row(preference.display, 'dots', layout.row(), 'Display Dot Gizmos')
    label_row(preference.display, 'dot_size', layout.row(), 'Dot Size')
    label_row(preference.display, 'dot_factor', layout.row(), 'Dot Detection Factor')

    layout.separator()
    row = layout.row()
    row.alignment = 'CENTER'
    row.label(text='Topbar')
    layout.separator()

    label_row(preference.display, 'simple_topbar', layout.row())
    label_row(preference.display, 'snap', layout.row())
    label_row(preference.display, 'destructive_menu', layout.row())
    label_row(preference.display, 'mode_label', layout.row())
    label_row(preference.display, 'shape_label', layout.row())
    label_row(preference.display, 'operation_label', layout.row())
    label_row(preference.display, 'surface_label', layout.row())

    layout.separator()

    label_row(preference.display, 'topbar_pad', layout.row(), label='Topbar Padding')

    if preference.display.topbar_pad:
        label_row(preference.display, 'pad_menus', layout.row(), label='Pad Menus')
        label_row(preference.display, 'padding', layout.row(), label='Amount')

    label_row(preference.display, 'middle_pad', layout.row(), label='Middle Padding')

    layout.separator()
    row = layout.row()
    row.alignment = 'CENTER'
    row.label(text='Fade Timing')
    layout.separator()

    # row = layout.row(align=True)
    # label_row(preference.display, 'shape_fade_time_in', row, label='Shape')
    # row.prop(preference.display, 'shape_fade_time_out', text='')

    row = layout.row(align=True)
    label_row(preference.display, 'dot_fade_time_in', row, label='Dot')
    row.prop(preference.display, 'dot_fade_time_out', text='')

    if preference.display.shape_fade_time_out in time_code.keys():
        row = layout.row(align=True)
        row.label(text='Volume')
        #row = layout.row(align=True)
        row.prop(preference.display, 'sound_volume', text='')
