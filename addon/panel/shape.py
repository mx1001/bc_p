import bpy

from bpy.types import Panel

from ... utility import tool, addon
from .. property.utility import names
from . utility import preset
from .. import toolbar


class BC_PT_shape(Panel):
    bl_label = 'Shape'
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

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        column = layout.column()

        row = column.row()
        row.scale_x = 2.0
        row.scale_y = 1.5

        sub = row.row()
        sub.enabled = not bc.running
        sub.prop(option, 'shape_type', expand=True, text='')

        sub = row.row()
        sub.enabled = option.shape_type != 'NGON'
        sub.prop(option, 'origin', expand=True, text='')

        if option.shape_type == 'CIRCLE':
            self.label_row(layout.row(), preference.shape, 'circle_vertices', label='Vertices')

        # elif option.shape_type == 'NGON':
        #     self.label_row(layout.row(), preference.snap, 'ngon_angle', label='Snap Angle')

        elif option.shape_type == 'CUSTOM':
            self.label_row(layout.row(), bc, 'collection', label='Collection')

            if not bc.collection:
                self.label_row(layout.row(), bc, 'shape', label='Shape')

            else:
                row = layout.row()
                split = row.split(factor=0.5)
                split.label(text='Shape')
                split.prop_search(bc, 'shape', bc.collection, 'objects', text='')

        elif option.shape_type == 'BOX':
            self.label_row(layout.row(), preference.behavior, 'line_box')

            if preference.behavior.line_box:
                self.label_row(layout.row(align=True), preference.shape, 'wedge')

        elif option.shape_type == 'NGON':
            self.label_row(layout.row(), context.scene.bc, 'cyclic', label='Cyclic')


    def label_row(self, row, path, prop, label=''):
        if prop in {'circle_vertices'}:
            column = self.layout.column(align=True)
            row = column.row(align=True)

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        values = {
            'Vertices': preset.vertice,
            'Snap Angle': preset.angle}

        if prop in {'circle_vertices'}:
            row = column.row(align=True)
            split = row.split(factor=0.48, align=True)
            sub = split.row(align=True)
            sub = split.row(align=True)

            pointer = '.shape.'
            for value in values[label]:
                op = sub.operator('wm.context_set_int', text=str(value))
                op.data_path = F'preferences.addons[\"{__name__.partition(".")[0]}\"].preferences{pointer}{prop}'
                op.value = value
