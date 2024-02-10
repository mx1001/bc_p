import bpy

from bpy.utils import register_class, unregister_class

from . import draw, snap
from . draw import interface


classes = (
    draw.BC_OT_shape_draw,
    interface.BC_OT_draw_interface,
    snap.BC_OT_shape_snap)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
