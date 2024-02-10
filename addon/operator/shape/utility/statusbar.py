import bpy
from bl_ui import space_statusbar

from ..... utility import method_handler, tool
# from .... import toolbar
from ..... utility import addon
from . import tracked_events, tracked_states

events = tracked_events
states = tracked_states
statusbar = space_statusbar.STATUSBAR_HT_header
normalbar = None


def add():
    global normalbar

    if not normalbar:
        normalbar = statusbar.draw

    statusbar.draw = draw_handler


def remove():
    statusbar.draw = normalbar


def draw_handler(hd, context):
    method_handler(draw,
        arguments = (hd, context),
        identifier = 'Status Bar',
        exit_method = remove)


#TODO: replace label with operator emboss = False that updates event_handler
def mouse(layout):
    unmodified = states.operation in {'DRAW', 'EXTRUDE'} and not states.modified
    sep = ''
    nav_type = 'Rotate' if not events.shift else 'Pan'
    cut = 'Lazorcut' if states.thin else 'Cut'
    #single_selected = len(context.selected_objects) == 1

    row = layout.row(align=True)
    if events.lmb and states.operation == 'NONE' and not states.rmb_lock:
        cut_type = cut if states.operation != 'MAKE' else 'Shape'
        row.label(text=F'{sep}Confirm {cut_type if states.operation != "JOIN" else "Join"}', icon='MOUSE_LMB')

    elif events.lmb and not states.rmb_lock:
        if unmodified and states.operation == 'EXTRUDE':
            cut_type = cut if states.operation != 'MAKE' else 'Shape'
            row.label(text=F'{sep}Confirm {cut_type if states.operation != "JOIN" else "Join"}', icon='MOUSE_LMB')
        else:
            row.label(text=F'{sep}Confirm {states.operation.title()}', icon='MOUSE_LMB')

    elif states.operation != 'NONE' and not states.thin:
        row.label(text=F'{sep}Confirm {states.operation.title()}', icon='MOUSE_LMB')

    elif not states.rmb_lock:
        cut_type = cut if states.operation != 'MAKE' else 'Shape'
        row.label(text=F'{sep}Confirm {cut_type if states.operation != "JOIN" else "Join"}', icon='MOUSE_LMB')

    if states.operation != 'NONE':
        icon = 'MOUSE_LMB_DRAG' if events.lmb else 'MOUSE_MOVE'
        row.label(text=F'{sep}Adjust {states.operation.title()}', icon=icon)

    layout.separator(factor=4.0)

    row = layout.row(align=True)
    row.label(text=F'{sep}{nav_type} View', icon='MOUSE_MMB')

    layout.separator(factor=4.0)

    row = layout.row(align=True)
    cancel_type = '' if states.operation == 'NONE' or not states.modified else F' {states.operation.title()}'
    row.label(text=F'{sep}Lock Shape' if events.lmb and states.operation != 'NONE' else F'{sep}Cancel{cancel_type}', icon='MOUSE_RMB')


def common(layout, context):
    preference = addon.preference()
    bc = context.scene.bc
    sep = ''

    if states.operation in {'MOVE', 'ROTATE', 'SCALE', 'ARRAY'}:
        layout.separator()

        # row = layout.row(align=True)

        if bc.axis != 'X':
            layout.label(text='', icon='EVENT_X')

        if bc.axis != 'Y':
            layout.label(text='', icon='EVENT_Y')

        if bc.axis != 'Z':
            layout.label(text='', icon='EVENT_Z')

        layout.label(text=F'{sep}Change Axis')

    if states.operation in {'ARRAY', 'SOLIDIFY', 'BEVEL'}:
        row = layout.row(align=True)
        row.label(text='', icon='EVENT_SHIFT')
        row.label(text=F'{sep}Reset Adjustment', icon='EVENT_R')

    layout.separator()

    if states.operation != 'NONE':
        layout.label(text=F'{sep}Lock Shape', icon='EVENT_TAB')

    layout.label(text=F'{sep}{"Disable " if preference.display.wire_only else ""}Wire', icon='EVENT_H')

    layout.separator()

    if states.operation != 'MOVE':
        layout.label(text=F'{sep}Move', icon='EVENT_G')

    if states.operation != 'ROTATE':
        layout.label(text=F'{sep}Rotate', icon='EVENT_R')

    if states.shape_type == 'CUSTOM' or (bc.shape and (bc.shape.bc.applied or bc.shape.bc.applied_cycle)):
        row = layout.row(align=True)
        row.label(text='', icon='EVENT_SHIFT')
        row.label(text=F'{sep}Rotate 90\u00b0 in Bounds', icon='EVENT_R')

    if states.operation != 'SCALE':
        layout.label(text=F'{sep}Scale', icon='EVENT_S')

    layout.separator()

    if states.operation != 'BEVEL':
        layout.label(text=F'{sep}Bevel', icon='EVENT_B')

    else:
        layout.label(text=F'{sep}Contour Bevel', icon='EVENT_Q')

    layout.separator()

    if states.operation != 'EXTRUDE':
        operation = 'Extrude' if states.operation != 'EXTRUDE' else 'Offset'
        layout.label(text=F'{sep}{operation}', icon='EVENT_E')

    if states.operation != 'OFFSET':
        row = layout.row(align=True)

        if states.operation == 'EXTRUDE':
            row.label(text='', icon='EVENT_E')

        row.label(text=F'{sep}Offset', icon='EVENT_O')

    layout.separator()

    if states.operation != 'SOLIDIFY':
        layout.label(text=F'{sep}Solidify', icon='EVENT_T')

    if states.operation != 'ARRAY':
        layout.label(text=F'{sep}Array', icon='EVENT_V')

    elif states.operation == 'ARRAY' and not bc.shape.bc.array_circle:
        layout.label(text=F'{sep}Radial Array', icon='EVENT_V')

    layout.separator()

    if states.mode == 'CUT':
        layout.label(text=F'{sep}Slice', icon='EVENT_X')

    elif states.mode == 'SLICE':
        layout.label(text=F'{sep}Intersect', icon='EVENT_X')
    
    elif states.mode == 'INTERSECT':
        layout.label(text=F'{sep}Inset', icon='EVENT_X')

    else:
        layout.label(text=F'{sep}Cut', icon='EVENT_X')

    if states.mode in {'SLICE', 'INSET'}:
        row = layout.row(align=True)
        row.label(text='', icon='EVENT_ALT')
        row.label(text=F'{sep}{"Disable " if preference.behavior.recut else ""}Recut', icon='EVENT_X')

    if context.selected_objects or (tool.active() and tool.active().mode == 'EDIT_MESH'):
        layout.label(text=F'{sep}{"Knife" if states.mode != "KNIFE" else "Cut"}', icon='EVENT_K')
        layout.label(text=F'{sep}{"Join" if states.mode != "JOIN" else "Cut"}', icon='EVENT_J')
        layout.label(text=F'{sep}{"Extract" if states.mode != "EXTRACT" else "Cut"}', icon='EVENT_Y')
        layout.label(text=F'{sep}{"Make" if states.mode != "MAKE" else "Cut"}', icon='EVENT_A')

    layout.separator()

    if states.operation == 'NONE':
        layout.label(text=F'{sep}Pie Menu', icon='EVENT_D')

        row = layout.row(align=True)
        row.label(text='', icon='EVENT_CTRL')
        row.label(text=F'{sep}Behavior Helper', icon='EVENT_D')

        row = layout.row(align=True)
        row.label(text='', icon='EVENT_ALT')
        row.label(text=F'{sep}Toggle Dots', icon='EVENT_D')


def draw(hd, context):
    layout = hd.layout


    if bpy.app.version < (2, 90, 0):
        layout.template_reports_banner()
        layout.template_running_jobs()

    if not events.mmb:
        mouse(layout)
        common(layout, context)

    else:
        layout.template_input_status()

    layout.separator_spacer()

    # stats
    scene = context.scene
    view_layer = context.view_layer

    if bpy.app.version < (2, 90, 0):
        layout.label(text=scene.statistics(view_layer), translate=False)
    else:
        row = layout.row()
        row.alignment = 'RIGHT'

        # Stats & Info
        row.label(text=context.screen.statusbar_info(), translate=False)

        # Messages
        row.template_reports_banner()

        # Progress Bar
        row.template_running_jobs()

