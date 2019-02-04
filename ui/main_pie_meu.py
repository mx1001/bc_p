import bpy 
import os

class BoxCutterPieMenu(bpy.types.Menu):
    bl_label = "Box Cutter Pie Menu"
    bl_idname = "boxcutter_pie_menu"
    
    def draw(self, context):
        layout = self.layout
        active_object = context.active_object

        if active_object is None:
            self.draw_without_active_object_pie(layout)
        elif active_object.mode == "OBJECT":
            self.draw_object_mode_pie(layout)
        elif active_object.mode == "EDIT":
            self.draw_edit_mode_pie(layout, active_object)

    def draw_without_active_object_pie(self,layout):
        pie = self.layout.menu_pie()  

        #left
        pie.separator()
        #right
        pie.separator()
        #bot
        pie.separator()
        #top
        pie.separator()
        #top L
        pie.separator()
        #top R
        pie.operator("boxcutter.draw_boolean_layout", text = "bool layout")
        #bot L
        pie.operator("boxcutter.draw_boolean_layout", text = "bool layout")
        #bot R
        pie.separator()

    def draw_edit_mode_pie(self, layout, object):
    	
        pie = self.layout.menu_pie()  

        #left
        pie.separator()
        #right
        pie.separator()
        #bot
        pie.separator()
        #top
        pie.separator()
        #top L
        pie.separator()
        #top R
        pie.operator("boxcutter.draw_boolean_layout", text = "bool layout")
        #bot L
        pie.operator("boxcutter.draw_boolean_layout", text = "bool layout")
        #bot R
        pie.separator()
        
    def draw_object_mode_pie(self, layout):
        pie = self.layout.menu_pie()  

        #left
        pie.separator()
        #right
        pie.separator()
        #bot
        pie.separator()
        #top
        pie.separator()
        #top L
        pie.separator()
        #top R
        pie.operator("boxcutter.draw_boolean_layout", text = "bool layout")
        #bot L
        pie.operator("boxcutter.draw_boolean_layout", text = "bool layout")
        #bot R
        pie.separator()