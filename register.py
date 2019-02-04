import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )


def register_panel():

    bpy.types.Scene.BoxCutter_enable_help = bpy.props.BoolProperty(
        name="Help info",
        description="enable help info",
        default = True)

    bpy.types.Scene.BoxCutter_display_shape = bpy.props.BoolProperty(
        name="Shape",
        description="open shape panel",
        default = False)
 
    bpy.types.Scene.BoxCutter_shape_moving = bpy.props.BoolProperty(
        name="Move BoxCutter",
        description="enable shape moving",
        default = False)

    bpy.types.Scene.BoxCutter_enable_grid = bpy.props.BoolProperty(
        name="Enable Grid ",
        description="enable grid ",
        default = False)

    bpy.types.Scene.BoxCutter_enable_hops = bpy.props.BoolProperty(
        name="Enable Hops",
        description="enable hops for box cutter",
        default = False)

    bpy.types.Scene.BoxCutter_circle_vert_count = IntProperty(
        name="circle verts",
        description = "Circle Verts Count",
        default = 28, min = 3, max = 128)
        
    bpy.types.Scene.BoxCutter_curve_vert_count = IntProperty(
        name="curve verts",
        description = "Curve Verts Count",
        default = 6, min = 1, max = 24)

    bpy.types.Scene.BoxCutter_enable_ngon = bpy.props.BoolProperty(
        name="Enable Ngon",
        description="enable ngons drawing option for box cutter",
        default = True)

    bpy.types.Scene.BoxCutter_split_mesh = BoolProperty(name = "Split Mesh",
        description = "Separate the mesh after CSplit",
        default = True)
    
    bpy.types.Scene.BoxCutter_show_wires = BoolProperty(name = "Show Wies",
        description = "show cutter wires",
        default = True)

    bpy.types.Scene.BoxCutter_snapping_angle = IntProperty(
        name="angle snapping",
        description = " value for angle snapping ",
        default = 5, min = 1, max = 90)

    bpy.types.Scene.BoxCutter_cut_loop = BoolProperty(name = "Cut Loop",
        description = "Ability Cut Loop",
        default = False)

    bpy.types.Scene.BoxCutter_valCut_loop = FloatProperty(
        name="val cut loop",
        description = " Value Cut Loop ",
        default = 0, min = -90, max = 90)
    
    bpy.types.Scene.BoxCutter_grid_spaceing = IntProperty(
        name="grid spaceing",
        description = " value for  grid spaceing ",
        default = 20, min = 0, max = 200)
    
    bool_items = [
    ("BMESH", "Bmesh", ""),
    ("CARVE", "Carve", ""),
    ("CARVEMOD", "Carve-mod", "") ]

    bpy.types.Scene.BoxCutter_bool_method = EnumProperty(name = "", default = "CARVE",
            options = {"SKIP_SAVE"}, items = bool_items)


    help_items = [
    ("BOX", "Box", ""),
    ("MAIN", "Main", ""),
    ("CIRCLE", "Circle", ""),
    ("NGON", "Ngon", "") ]

    bpy.types.Scene.BoxCutter_help_item = EnumProperty(name = "", default = "MAIN",
            options = {"SKIP_SAVE"}, items = help_items)

def unregister_panel():
    del bpy.types.Scene.BoxCutter_enable_help
    del bpy.types.Scene.BoxCutter_enable_hops
    del bpy.types.Scene.BoxCutter_circle_vert_count
    del bpy.types.Scene.BoxCutter_enable_ngon
    del bpy.types.Scene.BoxCutter_split_mesh
    del bpy.types.Scene.BoxCutter_shape_moving
    del bpy.types.Scene.BoxCutter_show_wires
    del bpy.types.Scene.BoxCutter_bool_method
    del bpy.types.Scene.BoxCutter_display_shape
    del bpy.types.Scene.BoxCutter_enable_grid
    del bpy.types.Scene.BoxCutter_grid_spaceing
    del bpy.types.Scene.BoxCutter_curve_vert_count
    del bpy.types.Scene.BoxCutter_snapping_angle
    del bpy.types.Scene.BoxCutter_valCut_Loop
    del bpy.types.Scene.BoxCutter_cut_loop
    del bpy.types.Scene.BoxCutter_help_item
