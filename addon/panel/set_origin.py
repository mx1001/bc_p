import bpy

from bpy.types import Panel

from ... utility import addon, tool


class BC_PT_set_origin(Panel):
    bl_label = 'Set Origin'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        preference = addon.preference()

        layout = self.layout
        layout.ui_units_x = 5.5

        row = layout.row(align=True)
        row.scale_x = 1.5
        row.scale_y = 1.5
        row.prop(preference.behavior, 'set_origin', text='', expand=True, icon_only=True)
