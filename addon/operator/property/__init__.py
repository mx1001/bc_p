import bpy

from bpy.utils import register_class, unregister_class

from . import shape_type

classes = (
    shape_type.BC_OT_box,
    shape_type.BC_OT_circle,
    shape_type.BC_OT_ngon,
    shape_type.BC_OT_custom)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
