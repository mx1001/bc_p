
import time
import bpy
from bpy.types import Panel

from .... utility import tool, addon
from ... import toolbar
from ... operator.shape.utility import tracked_events, tracked_states


# TODO: ctrl, alt, shift modifier key bahavior states
class BC_PT_help_general(Panel):
    bl_label = F'Help{" " * 30}{toolbar.description}'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.workspace'
    bl_options = {'HIDE_HEADER'}
    bl_parent_id = 'BC_PT_help'


    def draw(self, context):
        preference = addon.preference()
        bc = context.scene.bc
        option = toolbar.options()

        unmodified = option.operation in {'DRAW', 'EXTRUDE'} and not tracked_states.modified
        indentation = '           '
        sep = '-   '
        nav_type = 'Rotate' if not tracked_events.shift else 'Pan'
        cut = 'Lazorcut' if tracked_states.thin else 'Cut'
        single_selected = len(context.selected_objects) == 1

        layout = self.layout

        row = layout.row()
        if not self.is_popover:
            row.label(text=F'{indentation}{toolbar.description}')

        sub = row.row()
        sub.alignment = 'RIGHT'
        op = sub.operator('bc.help_link', text='', icon='QUESTION', emboss=False)

        if self.is_popover or context.region.type == 'UI':
            op.use_url = True

        if not bc.running:
            edit_mode = tool.active().mode == 'EDIT_MESH'
            use_make = not context.selected_objects[:] and not edit_mode

            if use_make:
                layout.label(text='Select Objects to Cut', icon='INFO') # icon='ERROR')

            elif preference.surface == 'OBJECT' and not option.active_only:
                layout.label(text=F'Draw Off{" the" if single_selected else ""} Object{"" if single_selected else "s"} to Project', icon='INFO')

            elif preference.surface == 'VIEW':
                layout.label(text='Cutting in Projection Only', icon='INFO')

            elif not option.active_only:
                layout.label(text='Adjust Surface Options', icon='INFO')

            else:
                layout.label(text='Cutting Only Active', icon='INFO')

            layout.separator()

            make = option.mode == 'MAKE'
            layout.label(text=F'{sep}{option.mode.title() if not use_make else "Make"} {"Object" if single_selected or option.active_only else "Selected" if not make and not use_make else ""}', icon='MOUSE_LMB_DRAG')

            layout.separator()

            if addon.preference().snap.enable:
                layout.label(text='Display Snapping Points', icon='EVENT_CTRL')
                layout.separator()

            layout.label(text=F'{sep}Pie Menu', icon='EVENT_D')

            row = layout.row(align=True)
            row.label(text='', icon='EVENT_CTRL')
            row.label(text=F'{sep}Behavior Helper', icon='EVENT_D')

            row = layout.row(align=True)
            row.label(text='', icon='EVENT_SHIFT')
            row.label(text=F'{sep}Surface Options', icon='EVENT_V')

            if option.shape_type == 'CUSTOM':
                layout.separator()
                layout.label(text=F'{sep}Active Object to Custom', icon='EVENT_C')

            return

        if tracked_events.mmb:
            layout.label(text=F'{sep}Confirm {nav_type}', icon='MOUSE_MMB')

            if not tracked_events.shift:
                layout.separator()

                layout.label(text=F'{sep}Axis Snape', icon='EVENT_ALT')

            return

        if option.operation != 'NONE':
            icon = 'MOUSE_LMB_DRAG' if tracked_events.lmb else 'MOUSE_MOVE'
            layout.label(text=F'{sep}Adjust {option.operation.title()}', icon=icon)

        if tracked_events.lmb and option.operation == 'NONE' and not tracked_states.rmb_lock:
            cut_type = cut if option.operation != 'MAKE' else 'Shape'
            layout.label(text=F'{sep}Confirm {cut_type if option.operation != "JOIN" else "Join"}', icon='MOUSE_LMB')

        elif tracked_events.lmb and not tracked_states.rmb_lock:
            if unmodified and option.operation == 'EXTRUDE':
                cut_type = cut if option.operation != 'MAKE' else 'Shape'
                layout.label(text=F'{sep}Confirm {cut_type if option.operation != "JOIN" else "Join"}', icon='MOUSE_LMB')
            else:
                layout.label(text=F'{sep}Confirm {option.operation.title()}', icon='MOUSE_LMB')

        elif option.operation != 'NONE' and not tracked_states.thin:
            layout.label(text=F'{sep}Confirm {option.operation.title()}', icon='MOUSE_LMB')

        elif not tracked_states.rmb_lock:
            cut_type = cut if option.operation != 'MAKE' else 'Shape'
            layout.label(text=F'{sep}Confirm {cut_type if option.operation != "JOIN" else "Join"}', icon='MOUSE_LMB')

        layout.label(text=F'{sep}{nav_type} View', icon='MOUSE_MMB')

        cancel_type = '' if option.operation == 'NONE' or not tracked_states.modified else F' {option.operation.title()}'
        layout.label(text=F'{sep}Lock Shape' if tracked_events.lmb and option.operation != 'NONE' else F'{sep}Cancel{cancel_type}', icon='MOUSE_RMB')

        layout.separator()

        if option.operation in {'MOVE', 'ROTATE', 'SCALE', 'ARRAY'}:
            layout.separator()

            row = layout.row(align=True)

            if bc.axis != 'X':
                row.label(text='', icon='EVENT_X')

            if bc.axis != 'Y':
                row.label(text='', icon='EVENT_Y')

            if bc.axis != 'Z':
                row.label(text='', icon='EVENT_Z')

            row.label(text=F'{sep}Change Axis')

        if option.operation in {'ARRAY', 'SOLIDIFY', 'BEVEL'}:
            row = layout.row(align=True)
            row.label(text='', icon='EVENT_SHIFT')
            row.label(text=F'{sep}Reset Adjustment', icon='EVENT_R')

        layout.separator()

        if option.operation != 'NONE':
            layout.label(text=F'{sep}Lock Shape', icon='EVENT_TAB')

        layout.label(text=F'{sep}{"Disable " if preference.display.wire_only else ""}Wire', icon='EVENT_H')

        layout.separator()

        if option.operation != 'MOVE':
            layout.label(text=F'{sep}Move', icon='EVENT_G')

        if option.operation != 'ROTATE':
            layout.label(text=F'{sep}Rotate', icon='EVENT_R')

        if option.shape_type == 'CUSTOM' or bc.shape.bc.applied or bc.shape.bc.applied_cycle:
            row = layout.row(align=True)
            row.label(text='', icon='EVENT_SHIFT')
            row.label(text=F'{sep}Rotate 90\u00b0 in Bounds', icon='EVENT_R')

        if option.operation != 'SCALE':
            layout.label(text=F'{sep}Scale', icon='EVENT_S')

        layout.separator()

        if option.operation != 'BEVEL':
            layout.label(text=F'{sep}Bevel', icon='EVENT_B')

        else:
            layout.label(text=F'{sep}Contour Bevel', icon='EVENT_Q')

        layout.separator()

        if option.operation != 'EXTRUDE':
            operation = 'Extrude' if option.operation != 'EXTRUDE' else 'Offset'
            layout.label(text=F'{sep}{operation}', icon='EVENT_E')

        if option.operation != 'OFFSET':
            row = layout.row(align=True)

            if option.operation == 'EXTRUDE':
                row.label(text='', icon='EVENT_E')

            row.label(text=F'{sep}Offset', icon='EVENT_O')

        layout.separator()

        if option.operation != 'SOLIDIFY':
            layout.label(text=F'{sep}Solidify', icon='EVENT_T')

        if option.operation != 'ARRAY':
            layout.label(text=F'{sep}Array', icon='EVENT_V')

        elif option.operation == 'ARRAY' and not bc.shape.bc.array_circle:
            layout.label(text=F'{sep}Radial Array', icon='EVENT_V')

        layout.separator()

        if option.mode == 'CUT':
            layout.label(text=F'{sep}Slice', icon='EVENT_X')

        elif option.mode == 'SLICE':
            layout.label(text=F'{sep}Intersect', icon='EVENT_X')

        elif option.mode == 'INTERSECT':
            layout.label(text=F'{sep}Inset', icon='EVENT_X')

        else:
            layout.label(text=F'{sep}Cut', icon='EVENT_X')

        if option.mode in {'SLICE', 'INSET'}:
            row = layout.row(align=True)
            row.label(text='', icon='EVENT_ALT')
            row.label(text=F'{sep}{"Disable " if preference.behavior.recut else ""}Recut', icon='EVENT_X')

        if context.selected_objects or tool.active().mode == 'EDIT_MESH':
            layout.label(text=F'{sep}{"Knife" if option.mode != "KNIFE" else "Cut"}', icon='EVENT_K')
            layout.label(text=F'{sep}{"Join" if option.mode != "JOIN" else "Cut"}', icon='EVENT_J')
            layout.label(text=F'{sep}{"Extract" if option.mode != "EXTRACT" else "Cut"}', icon='EVENT_Y')
            layout.label(text=F'{sep}{"Make" if option.mode != "MAKE" else "Cut"}', icon='EVENT_A')

        layout.separator()

        if option.operation == 'NONE':
            layout.label(text=F'{sep}Pie Menu', icon='EVENT_D')

            row = layout.row(align=True)
            row.label(text='', icon='EVENT_CTRL')
            row.label(text=F'{sep}Behavior Helper', icon='EVENT_D')

            row = layout.row(align=True)
            row.label(text='', icon='EVENT_ALT')
            row.label(text=F'{sep}Toggle Dots', icon='EVENT_D')

            # elif option.shape_type == 'CUSTOM':
                # layout.separator()
                # layout.label(text='Active Object as Custom Cutter', icon='EVENT_C')


        if option.operation != 'NONE' and option.operation == 'SOLIDIFY':
            layout.label(text=F'1 2 3   Solidify Type')
        else:
            layout.label(text=F'1 2 3   Mirror Axis')

        layout.label(text='.          Change origin')


class BC_PT_help_general_npanel_tool(Panel):
    bl_label = 'Interaction'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_parent_id = 'BC_PT_help_npanel_tool'
    bl_options = {'HIDE_HEADER'}


    def draw(self, context):
        BC_PT_help_general.draw(self, context)


class BC_PT_help_general_npanel(Panel):
    bl_label = 'Interaction'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_parent_id = 'BC_PT_help_npanel'
    bl_options = {'HIDE_HEADER'}


    def draw(self, context):
        BC_PT_help_general.draw(self, context)
