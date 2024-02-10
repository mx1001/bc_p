import bpy

from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from ... utility import addon
from . import behavior, grid, mode, operation, release_lock, set_origin, shape, surface, snap, settings, help

classes = [
    help.BC_PT_help,
    help.BC_PT_help_npanel_tool,
    help.BC_PT_help_npanel,
    help.general.BC_PT_help_general,
    help.general.BC_PT_help_general_npanel_tool,
    help.general.BC_PT_help_general_npanel,
    help.start_operation.BC_PT_help_start_operation,
    help.start_operation.BC_PT_help_start_operation_npanel_tool,
    help.start_operation.BC_PT_help_start_operation_npanel,
    behavior.BC_PT_helper,
    mode.BC_PT_mode,
    shape.BC_PT_shape,
    release_lock.BC_PT_release_lock,
    set_origin.BC_PT_set_origin,
    operation.BC_PT_operation,
    surface.BC_PT_surface,
    snap.BC_PT_snap,
    grid.BC_PT_grid,
    settings.BC_PT_settings,
    settings.behavior.BC_PT_behavior_settings,
    settings.sort_last.BC_PT_sort_last,
    settings.shape.BC_PT_shape_settings,
    settings.input.BC_PT_input_settings,
    settings.display.BC_PT_display_settings,
    settings.hardops.BC_PT_hardops_settings]


def register():
    for cls in classes:
        if hasattr(cls, 'bl_category') and cls.bl_category and cls.bl_category != 'Tool':
            cls.bl_category = addon.preference().display.tab
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
