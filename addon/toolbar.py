import os

import bpy

from bl_ui import space_view3d
from bpy.utils import register_class, unregister_class
from bpy.utils.toolsystem import ToolDef
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools

from . import icon, operator
from .. utility import method_handler, addon, screen, tool
from .. import bl_info

normaltoolbar = None
tool_header = space_view3d.VIEW3D_HT_tool_header
operator_id = 'bc.shape_draw'
label = 'BoxCutter'
description = bl_info['description'][10:]


def options():
    return tool.options(addon.name, operator_id)


def change_prop(context, prop, value):
    for tooldef in context.workspace.tools:
        if tooldef.idname == tool.active().idname:
            setattr(options(), prop, value)

    context.workspace.tools.update()


def change_mode_behavior(op, context):
    bc = context.scene.bc

    if not bc.running:
        if op.shape_type == 'BOX':
            change_prop(context, 'origin', 'CORNER' if op.shape_type in 'BOX' else 'CENTER')
        elif op.shape_type == 'CIRCLE':
            change_prop(context, 'origin', 'CENTER')
        elif op.shape_type == 'CUSTOM':
            bc.collection = bc.stored_collection
            bc.shape = bc.stored_shape


def change_mode(op, context):
    bc = context.scene.bc

    if not bc.running:
        # if op.mode == 'KNIFE':
        #     change_prop(context, 'shape_type', 'BOX')
        #     change_mode_behavior(op, context)

        if op.mode == 'EXTRACT':
            change_prop(context, 'shape_type', 'BOX')
            change_mode_behavior(op, context)

    elif op.mode == 'MAKE' and bc.shape and bc.shape.display_type != 'TEXTURED':
        bc.shape.display_type = 'TEXTURED'

    elif op.mode != 'MAKE' and op.shape_type != 'CUSTOM' and bc.shape and bc.shape.display_type != 'WIRE':
        bc.shape.display_type = 'WIRE'


def update_operator(op, context):
    for tooldef in context.workspace.tools:
        if tooldef.idname == tool.active().idname and tooldef.mode == tool.active().mode:
            prop = tooldef.operator_properties(operator_id)

            op.tool = tooldef
            op.mode = prop.mode
            op.shape_type = prop.shape_type
            op.operation = prop.operation
            op.behavior = prop.behavior
            # bc.axis = prop.axis
            op.origin = prop.origin
            op.align_to_view = prop.align_to_view
            op.live = prop.live
            op.active_only = prop.active_only

            return True

    return False


def ui_scale(value, factor=1):
    return value * factor


@ToolDef.from_fn
def boxcutter():
    def draw_settings(context, layout, tooldef):
        bc = context.scene.bc
        preference = addon.preference()
        option = options()

        if context.region.type not in {'UI', 'WINDOW'}:
            icons = {
                'CUT': icon.id('red'),
                'SLICE': icon.id('yellow'),
                'INTERSECT': icon.id('orange'),
                'INSET': icon.id('purple'),
                'JOIN': icon.id('green'),
                'KNIFE': icon.id('blue'),
                'EXTRACT': icon.id('black'),
                'MAKE': icon.id('grey')}

            row = layout.row(align=True)

            if not preference.display.simple_topbar:
                row.prop(option, 'mode', text='', expand=True, icon_only=True)

            row.popover(panel='BC_PT_helper', text='', icon_value=icons[option.mode])
            # row.popover(panel='BC_PT_mode', text='', icon_value=icons[option.mode])

            if preference.display.mode_label:
                box = row.box()
                box.ui_units_x = 2.9
                box.scale_y = ui_scale(0.5, factor=1 if bpy.app.version[1] < 82 else 2)
                box.label(text=F' {option.mode.title()}')

            row.prop(option, 'knife', text='', icon_value=icon.id('blue'))

            if preference.display.topbar_pad:
                for _ in range(preference.display.padding):
                    layout.separator()

            icons = {
                'BOX': 'MESH_PLANE',
                'CIRCLE': 'MESH_CIRCLE',
                'NGON': 'MOD_SIMPLIFY',
                'CUSTOM': 'FILE_NEW'}

            row = layout.row(align=True)

            if not preference.display.simple_topbar:
                row.prop(option, 'shape_type', expand=True, text='')

            row.popover(panel='BC_PT_shape', text='', icon=icons[option.shape_type])

            if preference.display.shape_label:
                box = row.box()
                box.ui_units_x = 3.0
                box.scale_y = ui_scale(0.5, factor=1 if bpy.app.version[1] < 82 else 2)
                box.label(text=F' {option.shape_type.title()}')

            if option.shape_type in {'BOX', 'CIRCLE'}:
                row.prop(preference.behavior, 'line_box', text='', icon='DRIVER_DISTANCE')

            elif option.shape_type == 'NGON':
                sub = row.row(align=True)
                sub.enabled = not bc.running #TODO: Fix in modal toggle (update func?)
                sub.prop(context.scene.bc, 'cyclic', text='', icon=F'RESTRICT_INSTANCED_O{"FF" if context.scene.bc.cyclic else "N"}')

            icons = {
                'MOUSE': 'RESTRICT_SELECT_OFF',
                'CENTER': 'SNAP_FACE_CENTER',
                'BBOX': 'PIVOT_BOUNDBOX',
                'ACTIVE': 'PIVOT_ACTIVE'}

            row.popover(panel='BC_PT_set_origin', text='', icon=icons[preference.behavior.set_origin])

            if preference.display.topbar_pad:
                for _ in range(preference.display.padding):
                    layout.separator()

            row = layout.row(align=True)

            if not preference.display.simple_topbar:
                row.prop(bc, 'start_operation', expand=True, icon_only=True)

            icons = {
                'NONE': 'LOCKED',
                'DRAW': 'GREASEPENCIL',
                'EXTRUDE': 'ORIENTATION_NORMAL',
                'OFFSET': 'MOD_OFFSET',
                'MOVE': 'RESTRICT_SELECT_ON',
                'ROTATE': 'DRIVER_ROTATIONAL_DIFFERENCE',
                'SCALE': 'FULLSCREEN_EXIT',
                'ARRAY': 'MOD_ARRAY',
                'SOLIDIFY': 'MOD_SOLIDIFY',
                'BEVEL': 'MOD_BEVEL',
                'DISPLACE': 'MOD_DISPLACE',
                'MIRROR': 'MOD_MIRROR'}

            row.popover(panel='BC_PT_operation', text='', icon=icons[option.operation])

            if preference.display.operation_label:
                box = row.box()
                box.ui_units_x = 3.5
                box.scale_y = ui_scale(0.5, factor=1 if bpy.app.version[1] < 82 else 2)
                lock_label = 'Locked' if bc.running else 'Default'
                box.label(text=F' {option.operation.title()}' if option.operation != 'NONE' else F' {lock_label}')

            row.prop(preference.keymap, 'release_lock', text='', icon=F'RESTRICT_SELECT_O{"FF" if preference.keymap.release_lock else "N"}')

            icons = {
                'OBJECT': 'OBJECT_DATA',
                'VIEW': 'LOCKVIEW_ON',
                'CURSOR': 'PIVOT_CURSOR',
                'WORLD': 'WORLD'}

            if preference.display.topbar_pad:
                for _ in range(preference.display.padding):
                    layout.separator()

            row = layout.row(align=True)
            row.popover(panel='BC_PT_surface', text='', icon=icons[preference.surface])
            if preference.display.surface_label:
                box = row.box()
                box.ui_units_x = 3.25
                box.scale_y = ui_scale(0.5, factor=1 if bpy.app.version[1] < 82 else 2)
                box.label(text=F' {preference.surface.title()}')

            row.prop(option, 'align_to_view', text='', icon='LOCKVIEW_ON')

            for _ in range(preference.display.middle_pad):
                layout.separator()

            if preference.display.snap:
                # layout.separator()

                row = layout.row(align=True)
                row.prop(preference.snap, 'enable', text='', icon=F'SNAP_O{"N" if preference.snap.enable else "FF"}')
                sub = row.row(align=True)
                sub.active = preference.snap.enable
                sub.prop(preference.snap, 'grid', text='', icon='SNAP_GRID')

                row.popover('BC_PT_snap', text='', icon='SNAP_INCREMENT')

            if preference.display.topbar_pad and preference.display.pad_menus:
                padding = preference.display.padding

                if not preference.display.destructive_menu:
                    padding = 0

                for _ in range(padding):
                    layout.separator()

            if preference.display.destructive_menu:
                row = layout.row(align=True)
                sub = row.row(align=True)
                sub.active = tool.active().mode == 'OBJECT'
                sub.prop(option, 'behavior', text='')
                sub = row.row(align=True)
                sub.operator('bc.smart_apply', text='', icon='IMPORT')


            if preference.display.topbar_pad and preference.display.pad_menus:
                for _ in range(preference.display.padding):
                    layout.separator()

            row = layout.row(align=True)
            row.popover(panel='BC_PT_settings', text='', icon='PREFERENCES')
            row.prop(option, 'live', text='', icon='PLAY' if not option.live else 'PAUSE')

            layout.separator()

            layout.operator('bc.help_link', text='', icon='QUESTION', emboss=False)

    return dict(
        idname=addon.name,
        label=label,
        description=description,
        icon=os.path.join(os.path.dirname(__file__), '.', 'icon', 'toolbar'),
        widget = None,
        keymap = '3D View Tool: BoxCutter',
        draw_settings = draw_settings)


def clear_trailing_separators(tools):
    if not tools[-1]:
        tools.pop()
        clear_trailing_separators(tools)


def add():
    global normaltoolbar

    if not normaltoolbar:
        normaltoolbar = tool_header.draw

    tool_header.draw = draw_handler


def remove():
    tool_header.draw = normaltoolbar


def draw_handler(hd, context):
    method_handler(draw,
        arguments = (hd, context),
        identifier = 'Toolbar',
        exit_method = remove)


def draw(hd, context):
    layout = hd.layout

    layout.row(align=True).template_header()

    hd.draw_tool_settings(context)

    layout.separator_spacer()

    if tool.active().idname not in {tool.name, 'Hops'}:
        space_view3d.VIEW3D_HT_header.draw_xform_template(layout, context)

        layout.separator_spacer()

    hd.draw_mode_settings(context)


def register():
    modes = ('OBJECT', 'EDIT_MESH')

    for context_mode in modes:
        tools = view3d_tools._tools[context_mode]

        if not addon.hops() or context_mode == 'EDIT_MESH':

            tools.append(None)

        tools.append(boxcutter)


def unregister():
    modes = ('OBJECT', 'EDIT_MESH')

    for context_mode in modes:
        tools = view3d_tools._tools[context_mode]

        tools.remove(boxcutter)

        clear_trailing_separators(tools)
