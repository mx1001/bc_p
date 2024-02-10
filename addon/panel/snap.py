import bpy

from bpy.types import Panel

from ... utility import addon, tool
from .. property.utility import names
from . utility import preset
from .. import toolbar


class BC_PT_snap(Panel):
    bl_label = 'Snap'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'


    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        layout = self.layout
        preference = addon.preference()
        option = toolbar.options()
        # tool = tool.active().operator_properties('bc.shape_draw')

        snap = layout.row(align=True)
        snap.scale_x = 1.5
        snap.scale_y = 1.5

        # row = snap.row(align=True)
        # row.prop(preference.behavior, "pivot_point", text="", icon_only=True)

        row = snap.row(align=True)
        row.active = preference.snap.enable

        row = snap.row(align=True)
        if not self.is_popover:
            row.prop(preference.snap, 'enable', text='', icon=F'SNAP_O{"N" if preference.snap.enable else "FF"}')
        row.prop(preference.snap, 'incremental', text='', icon='SNAP_INCREMENT')

        sub = row.row(align=True)
        snap_grid = (preference.snap.enable and preference.snap.grid)

        if preference.snap.incremental or snap_grid:
            sub.prop(preference.snap, 'increment', text='')
            sub.prop(preference.snap, 'increment_lock', text='', icon=F'{"" if preference.snap.increment_lock else "UN"}LOCKED')

            if snap_grid:
                sub = row.row(align=True)
                sub.scale_x = 1.2
                sub.popover('BC_PT_grid', text='', icon='SNAP_GRID')

            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_x = 1.5
            row.scale_y = 1.5

            sub = row.row(align=True)
            sub.active = preference.snap.enable

            if not self.is_popover:
                sub.prop(preference.snap, 'grid', text='', icon='SNAP_GRID')

            sub.prop(preference.snap, 'verts', text='', icon='VERTEXSEL')
            sub.prop(preference.snap, 'edges', text='', icon='EDGESEL')
            sub.prop(preference.snap, 'faces', text='', icon='FACESEL')

            if option.shape_type == 'NGON' or option.shape_type == 'BOX' and preference.behavior.line_box:
                sub = row.row(align=True)
                sub.separator()
                sub.active = not preference.snap.incremental or not preference.snap.increment_lock
                sub.prop(preference.snap, 'angle_lock', text='', icon='DRIVER_ROTATIONAL_DIFFERENCE')

        else:
            subsub = sub.row(align=True)
            subsub.active = preference.snap.enable

            separators = 10 if option.shape_type != 'NGON' else 6
            for _ in range(2 if not self.is_popover else separators):
                subsub.separator()

            if not self.is_popover:
                subsub.prop(preference.snap, 'grid', text='', icon='SNAP_GRID')

            subsub.prop(preference.snap, 'verts', text='', icon='VERTEXSEL')
            subsub.prop(preference.snap, 'edges', text='', icon='EDGESEL')
            subsub.prop(preference.snap, 'faces', text='', icon='FACESEL')

            if option.shape_type == 'NGON' or option.shape_type == 'BOX' and preference.behavior.line_box:
                sub.separator()
                sub.prop(preference.snap, 'angle_lock', text='', icon='DRIVER_ROTATIONAL_DIFFERENCE')

        if option.shape_type == 'NGON':
            self.label_row(layout.row(), preference.snap, 'ngon_angle', label='Ngon Angle')

        elif option.shape_type == 'BOX' and preference.behavior.line_box:
            self.label_row(layout.row(), preference.snap, 'line_box_angle')

        self.label_row(layout.row(), preference.snap, 'rotate_angle', 'Rotate Angle')


    def label_row(self, row, path, prop, label=''):
        if prop in {'line_box_angle', 'ngon_angle', 'rotate_angle'}:
            column = self.layout.column(align=True)
            row = column.row(align=True)

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        values = {
            'line_box_angle': preset.line_angle,
            'ngon_angle': preset.angle,
            'rotate_angle': preset.angle}

        if prop in {'line_box_angle', 'ngon_angle', 'rotate_angle'}:
            row = column.row(align=True)
            split = row.split(factor=0.48, align=True)
            sub = split.row(align=True)
            sub = split.row(align=True)

            # pointer = '.shape.' if prop == 'ngon_snap_angle' else '.shape.'
            pointer = '.snap.'
            for value in values[prop]:
                op = sub.operator('wm.context_set_int', text=str(value))
                op.data_path = F'preferences.addons[\"{__name__.partition(".")[0]}\"].preferences{pointer}{prop}'
                op.value = value
