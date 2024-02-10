import bpy

from bpy.types import Panel

from ... utility import tool, addon
from .. property.utility import names
from . utility import preset
from .. import toolbar


class BC_PT_operation(Panel):
    bl_label = 'Operations'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'


    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        preference = addon.preference()
        bc = context.scene.bc
        option = toolbar.options()

        layout = self.layout
        layout.ui_units_x = 15

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        column = layout.column()
        column.scale_x = 1.5
        column.scale_y = 1.5

        row = column.row(align=True)

        if self.is_popover:
            row.active = bc.running
            row.prop(option, 'operation', expand=True)
        else:
            row.prop(bc, 'start_operation', expand=True, icon_only=True)
            sub = row.row(align=True)
            sub.active = bc.running
            sub.prop(option, 'operation', text='', icon_only=True)

        if option.operation == 'ARRAY':
            self.label_row(layout.row(align=True), preference.shape, 'array_count', label='Count')

            if not bc.running:
                self.label_row(layout.row(align=True), preference.shape, 'array_axis', label='Axis')

            # if not bc.running:
            #     self.label_row(layout.row(align=True), preference.shape, 'array_around_cursor', label='3D Cursor')

        elif option.operation == 'BEVEL':
            self.label_row(layout.row(align=True), preference.shape, 'bevel_width', label='Width')
            self.label_row(layout.row(align=True), preference.shape, 'bevel_segments', label='Segments')
            self.label_row(layout.row(align=True), preference.shape, 'quad_bevel')
            if preference.shape.quad_bevel:
                self.label_row(layout.row(align=True), preference.shape, 'straight_edges')

        elif option.operation == 'SOLIDIFY':
            self.label_row(layout.row(align=True), preference.shape, 'solidify_thickness', label='Thickness')


    def label_row(self, row, path, prop, label=''):
        if prop in {'array_count', 'bevel_width', 'bevel_segments'}:
            column = self.layout.column(align=True)
            row = column.row(align=True)
        else:
            row.scale_x = 1.2

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        values = {
            'Count': preset.array,
            'Width': preset.width,
            'Segments': preset.segment}

        if prop in {'array_count', 'bevel_width', 'bevel_segments'}:
            row = column.row(align=True)
            split = row.split(factor=0.49, align=True)
            sub = split.row(align=True)
            sub = split.row(align=True)

            for value in values[label]:
                op = sub.operator(F'wm.context_set_{"int" if prop != "bevel_width" else "float"}', text=str(value))
                op.data_path = F'preferences.addons["{__name__.partition(".")[0]}"].preferences.shape.{prop}'
                op.value = value

            column.separator()
