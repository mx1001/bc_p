import bpy

from bpy.types import Panel

from ... utility import addon, tool


class BC_PT_grid(Panel):
    bl_label = 'Grid'
    bl_space_type = 'TOPBAR'
    bl_region_type = 'WINDOW'
    bl_category = 'BoxCutter'


    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        layout = self.layout
        preference = addon.preference()

        layout.scale_x = 1.5
        layout.scale_y = 1.5

        row = layout.row(align=True)
        # row.prop(preference.snap, 'grid_relative_size', text='', icon='CON_SIZELIKE')
        row.prop(preference.snap, 'grid_units', text='')
        row.prop(preference.snap, 'grid_off_face', text='', icon='GRID')
