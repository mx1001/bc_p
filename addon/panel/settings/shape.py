import bpy

from bpy.types import Panel

from .... utility import addon, tool
from ... property.utility import names
from ... import toolbar


class BC_PT_shape_settings(Panel):
    bl_label = 'Shape'
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
        option = toolbar.options()
        layout = self.layout

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        layout.separator()

        # self.label_row(layout.row(), preference.shape, 'offset')
        # self.label_row(layout.row(), preference.shape, 'lazorcut_limit', label='Lazorcut Thresh')

        if preference.behavior.lazorcut_trim:
            self.label_row(layout.row(), preference.shape, 'lazorcut_depth', label='Lazorcut Depth')

        layout.separator()

        self.label_row(layout.row(), preference.shape, 'circle_vertices')

        layout.separator()

        self.label_row(layout.row(), preference.shape, 'rotate_axis')

        layout.separator()

        self.label_row(layout.row(), preference.shape, 'inset_thickness')

        layout.separator()

        self.label_row(layout.row(), preference.shape, 'array_count')
        self.label_row(layout.row(), preference.shape, 'array_axis')
        # self.label_row(layout.row(), preference.shape, 'array_around_cursor')

        layout.separator()

        self.label_row(layout.row(), preference.shape, 'solidify_thickness')

        layout.separator()

        self.label_row(layout.row(), preference.shape, 'bevel_width')
        self.label_row(layout.row(), preference.shape, 'bevel_segments')
        self.label_row(layout.row(), preference.shape, 'quad_bevel')
        self.label_row(layout.row(), preference.shape, 'straight_edges')
        self.label_row(layout.row(), preference.shape, 'cycle_all')

        if option.shape_type == 'NGON':
            self.label_row(layout.row(), context.scene.bc, 'cyclic', label='Cyclic')


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
