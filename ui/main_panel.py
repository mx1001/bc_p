import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )


def boxcutter_enable_hops():
    return bpy.context.scene.BoxCutter_enable_hops


class BoxCutterPanel(bpy.types.Panel):
    bl_label = "Box Cutter"
    bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    #enable_hops = BoolProperty(name = "Enable Hops", default=True)


    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.separator()
        col.operator("boxcutter.draw_boolean_layout", text="Start BoxCutter")

        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        layout.separator()
        split = col.split(percentage=0.20, align=True)
        if bpy.context.scene.BoxCutter_display_shape :
            split.prop(scene, "BoxCutter_display_shape", text="", icon='DOWNARROW_HLT')
        else:
            split.prop(scene, "BoxCutter_display_shape", text="", icon='RIGHTARROW')
        split.prop(scene, "BoxCutter_bool_method")

        if bpy.context.scene.BoxCutter_display_shape :
            box = col.column(align=True).box().column()
            box.prop(scene, "BoxCutter_enable_ngon")

        col.separator()
        col.prop(scene, "BoxCutter_enable_hops", text = "HardOps Connection")
        col.prop(scene, "BoxCutter_split_mesh")
        col.prop(scene, "BoxCutter_show_wires", text = "Show Wires")
        col.separator()
        col.prop(scene, "BoxCutter_circle_vert_count", text = "Circle Segments")
        col.prop(scene, "BoxCutter_curve_vert_count", text = "Curve Segments")
        col.separator()
        col.prop(scene, "BoxCutter_grid_spaceing", text = "Snap Grid")
        col.prop(scene, "BoxCutter_snapping_angle", text = "Snap Angle")
        col.separator()
        col.prop(scene, "BoxCutter_enable_help", text = "Help Info")
        #This is not ready yet. Unstable currently. WIP Feature
        #col.prop(scene, "BoxCutter_cut_loop", text = "Cut Loop")
        #col.prop(scene, "BoxCutter_valCut_loop", text = "Value Cut Loop")
        
        

