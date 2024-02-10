import bpy

from bpy.utils import register_class, unregister_class

from . import transform

classes = (
    transform.BC_OT_transform_translate,
    transform.BC_OT_transform_rotate,
    transform.BC_OT_transform_resize,
    transform.BC_WGT_transform_gizmo_group,
    transform.BC_OT_transform_add_gizmo,
    transform.BC_OT_transform_remove_gizmo,
    transform.BC_GT_transform_gizmo)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
