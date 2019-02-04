import bpy
import textwrap
from mathutils import Vector

def get_dpi_factor():
    return get_dpi() / 72

def get_dpi():
    systemPreferences = bpy.context.user_preferences.system
    retinaFactor = getattr(systemPreferences, "pixel_size", 1)
    return int(systemPreferences.dpi * retinaFactor)

def get_3d_view_tools_panel_overlay_width(area):
    use_region_overlap = bpy.context.user_preferences.system.use_region_overlap

    n = 0
    if use_region_overlap:
        for region in area.regions:
            if region.type == "UI":
                if region.x < bpy.context.region.width/3 :
                    n = region.width

    if use_region_overlap:
        for region in area.regions:
            if region.type == "TOOLS":
                return region.width + n

    return 0

def write_text(layout, text, width = 30, icon = "NONE"):
    col = layout.column(align = True)
    col.scale_y = 0.85
    prefix = " "
    for paragraph in text.split("\n"):
        for line in textwrap.wrap(paragraph, width):
            col.label(prefix + line, icon = icon)
            if icon != "NONE": prefix = "     "
            icon = "NONE"

def get_region_dimensions():
    height = bpy.context.region.height
    width = bpy.context.region.width

    return height, width