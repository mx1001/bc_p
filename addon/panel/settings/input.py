import bpy

from bpy.types import Panel

from .... utility import addon, tool
from ... property.utility import names


class BC_PT_input_settings(Panel):
    bl_label = 'Input'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_parent_id = 'BC_PT_settings'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name and context.region.type == 'UI'


    def draw(self, context):
        preference = addon.preference()
        layout = self.layout

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        self.label_row(layout.row(), context.preferences.inputs, 'drag_threshold', label='Drag threshold')

        self.label_row(layout.row(), preference.keymap, 'release_lock', label='Release Lock')
        self.label_row(layout.row(), preference.keymap, 'release_lock_lazorcut', label='Lazorcut Lock')
        self.label_row(layout.row(), preference.keymap, 'quick_execute')
        self.label_row(layout.row(), preference.keymap, 'make_active')

        # self.label_row(layout.row(), preference.keymap, 'enable_surface_toggle')
        self.label_row(layout.row(), preference.keymap, 'enable_toolsettings', label='Enable Topbar')
        self.label_row(layout.row(), preference.keymap, 'allow_selection', label='Allow Selection')
        self.label_row(layout.row(), preference.keymap, 'rmb_cancel_ngon', label='RMB Cancel Ngon')

        if tool.active().mode == 'EDIT_MESH':
            self.label_row(layout.row(), preference.keymap, 'edit_disable_modifiers', label='Disable Ctrl & Shift LMB')

        self.label_row(layout.row(), preference.keymap, 'alt_preserve', label='Preserve Alt')
        self.label_row(layout.row(), preference.keymap, 'rmb_preserve', label='Preserve RMB')
        self.label_row(layout.row(), preference.keymap, 'alt_draw', label='Alt Center')
        self.label_row(layout.row(), preference.keymap, 'shift_draw', label='Shift Uniform')
        self.label_row(layout.row(), preference.keymap, 'scroll_adjust_circle')
        self.label_row(layout.row(), preference.keymap, 'view_pie', label='View Pie')


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
