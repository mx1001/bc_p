import os
import bpy
import rna_keymap_ui
from bpy.props import *
from . utils.blender_ui import write_text, get_dpi_factor
#from . utils.addons import addon_exists

def get_preferences():
    name = get_addon_name()
    return bpy.context.user_preferences.addons[name].preferences

def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))

# Specific preference settings

def enable_experimental_tools():
    return get_preferences().enable_experimental_tools

def enable_border_display():
    return get_preferences().enable_border_display

def BC_border_color():
    return get_preferences().BC_border_color

def BC_indicator_color():
    return get_preferences().BC_indicator_color

settings_tabs_items = [
    ("UI", "UI", ""),
    ("INFO", "Info", ""),
    ("KEYMAP", "Keymap", ""),
    ("LINKS", "Links / Help", "")]

class BoxCutterPreferences(bpy.types.AddonPreferences):
    bl_idname = get_addon_name()

    tab = EnumProperty(name = "Tab", items = settings_tabs_items)

    #Main Prefs Needed
    enable_experimental_tools = BoolProperty(name = "Enable Experimental Tools", default=False)
    
    enable_border_display = BoolProperty(name = "Enable Border Display", default=True)

    BC_border_color = FloatVectorProperty(
            name="", 
            default=(0.29, 0.52, 1.0, 0.53),
            size = 4, 
            min=0, max=1,
            subtype='COLOR'
            )

    BC_indicator_color = FloatVectorProperty(
            name="", 
            default=(0.29, 0.52, 1.0, 0.53),
            size = 4, 
            min=0, max=1,
            subtype='COLOR'
            )

    def draw(self, context):
        layout = self.layout

        col = layout.column(align = True)
        row = col.row()
        row.prop(self, "tab", expand = True)

        box = col.box()

        if self.tab == "UI":
            self.draw_ui_tab(box)
        elif self.tab == "INFO":
            self.draw_info_tab(box)
        elif self.tab == "KEYMAP":
            self.draw_keymap_tab(box)
        elif self.tab == "LINKS":
            self.draw_links_tab(box)

    def draw_ui_tab(self, layout):
        #layout.prop(self, "toolbar_category_name")
        row = layout.row()
        
        box = layout.box()
        row = box.row(align=True) 
        row.prop(self, "enable_experimental_tools", text = "Enable Experiemental Tools")

        row = box.row(align=True) 
        row.prop(self, "enable_border_display", text = "Enable Border Display")   
        
        row = box.row(align=True)
        row.prop(self, "BC_border_color", text = "Border Display")

        row = box.row(align=True)
        row.prop(self, "BC_indicator_color", text = "Inciator Color")

        #if addon_exists("BoxCutter"):
            #row = layout.row()
            #row.prop(self, "BC_border_color", text = "Border Color")    
            #row.prop(self, "BC_indicator_color", text = "Inciator Color")    

    def draw_info_tab(self, layout):
        write_text(layout, info_text, width = bpy.context.region.width / get_dpi_factor() / 8)

    def draw_keymap_tab(self, layout):
        layout.label("Alt + W unleashes the box cutting fury!")

    def draw_links_tab(self, layout):
        col = layout.column()
        for name, url in weblinks:
            col.operator("wm.url_open", text = name).url = url

info_text = """ Thank you for your support.


Box Cutter V1 Experimental
""".replace("\n", " ")

weblinks = [
    ("AR",                      "https://www.artstation.com/artist/adrianrutkowski"),
    ("MX",                      "https://www.artstation.com/artist/jerryperkins1447"),
    ("Intro Guide",             "https://masterxeon1001.com/2016/04/26/box-cutter-guide-v1/"),
]
