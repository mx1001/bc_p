import bpy

from bpy.types import Operator

from .. import toolbar
from ... utility import tool, addon


class BC_OT_release_lock(Operator):
    bl_idname = 'bc.release_lock'
    bl_label = 'Release Lock'
    bl_description = 'Access to release lock related options'
    bl_options = {'INTERNAL'}


    def invoke(self, context, event):
        preference = addon.preference()

        if event.shift or event.ctrl:
            preference.keymap['release_lock'] = not preference.keymap.release_lock
            bpy.ops.wm.call_panel(name='BC_PT_release_lock', keep_open=True)

        return {'FINISHED'}
