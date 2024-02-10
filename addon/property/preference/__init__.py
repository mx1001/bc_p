import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences
from bpy.props import *

from . import behavior, color, display, expand, keymap, shape, snap

from .... utility import addon
from ... property.utility import names


class bc(AddonPreferences):
    bl_idname = addon.name

    debug: BoolProperty(
        name = 'Debug',
        description = 'Allow errors to print that would otherwise be hidden through management',
        default = False)

    settings: EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [
            ('BEHAVIOR', 'Behavior', ''),
            ('COLOR', 'Color', ''),
            ('DISPLAY', 'Display', ''),
            ('SHAPE', 'Shape', ''),
            ('KEYMAP', 'Keymap', '')],
        default = 'BEHAVIOR')

    # TODO: add update handler to gizmo toggles that calls gizmo ot
    grid_gizmo: BoolProperty(
        name = names['grid_gizmo'],
        description = 'Show grid gizmo',
        default = False)

    cursor: BoolProperty(
        name = names['cursor'],
        description = 'Show cursor gizmo',
        default = False)

    transform_gizmo: BoolProperty(
        name = names['transform_gizmo'],
        description = 'Show transform gizmo',
        default = False)

    axis: EnumProperty(
        name = 'Axis',
        description = 'Axis to be used',
        items = [
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', '')],
        default = 'Z')

    surface: EnumProperty(
        name = 'Surface',
        description = 'Draw Surface',
        items = [
            ('OBJECT', 'Object', '\n Align Shape to Surface\n\n'
                                ' Object orients the drawing to the surface on draw\n'
                                ' BC will calculate the orientation based on surface geo.\n'
                                ' Typically the default', 'OBJECT_DATA', 0),
            ('VIEW', 'View', '\n Align shape to View\n\n'
                             ' View orients the drawing off the surface to the view on draw\n'
                             ' BC will calculate the orientation based on the viewport.\n'
                             ' Sets knife to work via knife project. Supporting (edge-only) 2d custom shapes.\n'
                             ' Typically used for cut projection', 'LOCKVIEW_ON', 1),
            ('CURSOR', 'Cursor', '\n Align Shape to 3d Cursor\n\n'
                                ' Cursor orients the drawing to the 3d cursor on draw\n'
                                ' Grid Gizmo being enabled shows grid.\n'
                                ' Cursor best aligns on Z axis.\n\n'
                                ' Gizmo may be disabled leaving only grid', 'PIVOT_CURSOR', 2),
            ('WORLD', 'World', '\n Align Shape to World Axis\n\n'
                                '\n Draws shape in 0,0,0 of the world\n'
                                '\n World is the final fallback utilizing the world for orientation\n'
                                '\n Typically used with make box for creation', 'WORLD', 3)],
        default = 'OBJECT')

    behavior: PointerProperty(type=behavior.bc)
    color: PointerProperty(type=color.bc)
    display: PointerProperty(type=display.bc)
    keymap: PointerProperty(type=keymap.bc)
    expand: PointerProperty(type=expand.bc)
    shape: PointerProperty(type=shape.bc)
    snap: PointerProperty(type=snap.bc)


    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        box = column.box()
        globals()[self.settings.lower()].draw(self, context, box)

        column.separator()

        row = column.row(align=True)
        row.prop(self, 'debug')


classes = (
    behavior.bc,
    color.bc,
    display.bc,
    keymap.bc,
    expand.bc,
    shape.bc,
    snap.bc,
    bc)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
