import bpy

from bpy.types import Panel

from .... utility import addon, tool
from ... property.utility import names
from ... import toolbar


class BC_PT_hardops_settings(Panel):
    bl_label = 'HardOps'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_parent_id = 'BC_PT_settings'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        hops = hasattr(context.window_manager, 'Hard_Ops_material_options')
        active = tool.active()
        return active and active.idname == tool.name and hops and context.region.type == 'UI'


    def draw(self, context):
        preference = addon.preference()
        hops = addon.hops()
        option = toolbar.options()
        wm = context.window_manager

        hops_material = wm.Hard_Ops_material_options if hasattr(wm, 'Hard_Ops_material_options') else False

        if hops:
            layout = self.layout

            column = layout.column()
            if option.mode == 'KNIFE':
                self.label_row(column.row(), preference.behavior, 'hops_mark')

            column.separator()
            column.label(text='Cutting Material')

            row = column.row()
            row.prop_search(hops_material, 'active_material', bpy.data, 'materials', text='')


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
