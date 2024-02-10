import bpy

from bpy.types import Panel

from . import behavior, display, hardops, input, shape, sort_last

from .... utility import tool, addon
from ... property.utility import names
from ... import toolbar


class BC_PT_settings(Panel):
    bl_label = 'Settings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'

    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        preference = addon.preference()
        option = toolbar.options()
        wm = context.window_manager

        layout = self.layout

        if self.is_popover:
            layout.ui_units_x = 12

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        row = layout.row(align=True)
        row.scale_x = 1.25
        row.scale_y = 1.25
        # row.prop(option, 'align_to_view', text='', icon='VIEW_ORTHO' if option.align_to_view else 'VIEW_PERSPECTIVE')
        # row.prop(preference.keymap, 'allow_selection', text='', icon='RESTRICT_SELECT_ON' if not preference.keymap.allow_selection else 'RESTRICT_SELECT_OFF')
        # sub = row.row(align=True)
        row.active = tool.active().mode == 'OBJECT'
        row.prop(option, 'behavior', text='')
        sub = row.row(align=True)
        sub.enabled = row.active
        sub.operator('bc.smart_apply', text='', icon='IMPORT')

        if self.is_popover:
            self.header_row(layout.row(align=True), 'behavior', label='Behavior')
            if preference.expand.behavior:
                behavior.BC_PT_behavior_settings.draw(self, context)

            self.header_row(layout.row(align=True), 'shape', label='Shape')
            if preference.expand.shape:
                shape.BC_PT_shape_settings.draw(self, context)

            self.header_row(layout.row(align=True), 'input', label='Input')
            if preference.expand.input:
                input.BC_PT_input_settings.draw(self, context)

            self.header_row(layout.row(align=True), 'display', label='Display')
            if preference.expand.display:
                display.BC_PT_display_settings.draw(self, context)

            hops = hasattr(wm, 'Hard_Ops_material_options')
            if hops:
                self.header_row(layout.row(align=True), 'hops', label='HardOps')
                if preference.expand.hops:
                    hardops.BC_PT_hardops_settings.draw(self, context)

        if self.is_popover:
            row = layout.row()
            row.alignment = 'RIGHT'
            row.operator('bc.help_link', text='', icon='QUESTION', emboss=False)


    def header_row(self, row, prop, label='', emboss=False):
        preference = addon.preference()

        icon = 'DISCLOSURE_TRI_RIGHT' if not getattr(preference.expand, prop) else 'DISCLOSURE_TRI_DOWN'
        row.alignment = 'LEFT'
        row.prop(preference.expand, prop, text='', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.25
        sub.prop(preference.expand, prop, text='', icon=icon, emboss=emboss)
        row.prop(preference.expand, prop, text=F'{label}', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.75
        sub.prop(preference.expand, prop, text=' ', icon='BLANK1', emboss=emboss)


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
