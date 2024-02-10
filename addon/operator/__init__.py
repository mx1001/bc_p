import bpy

from bpy.utils import register_class, unregister_class

from . import gizmo, property, shape, modifier, popover, tool_activate, web


classes = (
    modifier.BC_OT_smart_apply,
    popover.BC_OT_release_lock,
    tool_activate.BC_OT_tool_activate,
    web.BC_OT_help_link)


def register():
    for cls in classes:
        register_class(cls)

    gizmo.register()
    property.register()
    shape.register()


def unregister():
    for cls in classes:
        unregister_class(cls)

    gizmo.unregister()
    property.unregister()
    shape.unregister()
