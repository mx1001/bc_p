import bpy

from bpy.types import Panel

from ... utility import tool, addon
from .. property.utility import names


class BC_PT_release_lock(Panel):
    bl_label = 'Release Lock'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'


    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        preference = addon.preference()
        layout = self.layout

        self.label_row(layout.row(), preference.keymap, 'release_lock', label='Release Lock')
        self.label_row(layout.row(), preference.keymap, 'release_lock_lazorcut', label='Release Lock Lazorcut')
        self.label_row(layout.row(), preference.keymap, 'quick_execute', label='Quick Execute')


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
