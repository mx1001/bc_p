import bpy 
import os

class BoxCutterMenu(bpy.types.Menu):
    bl_label = "view3d.boxcutter_menu"
    bl_idname = "boxcutter_menu"
    
    def draw(self, context):

        layout = self.layout
        active_object = context.active_object

        if active_object is None:
            self.draw_without_active_object(layout)
        elif active_object.mode == "OBJECT":
            self.draw_object_mode(layout)
        elif active_object.mode == "EDIT":
            self.draw_edit_mode(layout, active_object)

      
    def draw_without_active_object(self, layout):
        layout.seperator()

    def draw_object_mode(self, layout):
        layout.operator("boxcutter.simple_sub_d", text = "apply SubD")

    def draw_edit_mode(self, layout, object):

        layout.operator("boxcutter.compex_crease", text = "(C)creese")
        layout.operator("boxcutter.simple_sub_d", text = "apply SubD")
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("boxcutter.adjust_solidify", text = "tthick")
        layout.operator("boxcutter.rebase", text = "rebase")