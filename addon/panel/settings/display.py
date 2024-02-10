import bpy

from bpy.types import Panel

from .... utility import addon, tool
from ... sound import time_code
from ... property.utility import names


class BC_PT_display_settings(Panel):
    bl_label = 'Display'
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

        # self.label_row(layout.row(), preference.snap, 'fade_distance', label='Fade Distance')
        self.label_row(layout.row(), preference.display, 'dots', 'Display Dots')
        self.label_row(layout.row(), preference.display, 'wire_only')

        if preference.display.wire_only:
            self.label_row(layout.row(), preference.display, 'thick_wire')
            self.label_row(layout.row(), preference.display, 'wire_size_factor', 'Wire Multiplier')

        self.label_row(layout.row(), preference.display, 'simple_topbar')
        self.label_row(layout.row(), preference.color, 'grid_use_mode')

        # layout.row().label(text='Fade')
        # self.label_row(layout.row(), preference.display, 'shape_fade_time_in', '  In')
        # self.label_row(layout.row(), preference.display, 'shape_fade_time_out', '  Out')

        # if preference.display.shape_fade_time_out in time_code.keys():
        #     self.label_row(layout.row(), preference.display, 'sound_volume', 'Volume')


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
