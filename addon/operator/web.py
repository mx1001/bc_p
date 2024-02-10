import bpy

from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from ... __init__ import bl_info


class BC_OT_help_link(Operator):
    bl_idname = 'bc.help_link'
    bl_label = 'Visit Documentation Website'
    bl_description = '\n Ctrl - HopsCutter Discord Community\n\nShift - Box Docs'

    url: StringProperty(
        name = 'Help URL',
        description = 'BoxCutter help URL to visit',
        default = bl_info['wiki_url'])

    use_url: BoolProperty(default=False)


    def invoke(self, context, event):
        use_url = False
        if event.ctrl and not self.use_url:
            self.url = 'https://discord.gg/ySRW6u9'
            use_url = True
        if event.shift and not self.use_url:
            self.url = bl_info['wiki_url']
            use_url = True
        elif self.use_url:
            use_url = True

        if not use_url:
            bpy.ops.wm.call_panel(name='BC_PT_help', keep_open=True)
            return {"FINISHED"}

        bpy.ops.wm.url_open(url=self.url)

        return {"FINISHED"}
