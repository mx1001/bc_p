import bpy

from bpy.types import Operator

from .. import toolbar
from ... utility import tool, addon


class BC_OT_tool_activate(Operator):
    bl_idname = 'bc.tool_activate'
    bl_label = 'Activate BoxCutter'
    bl_description = 'Activate BoxCutter'


    def execute(self, context):
        preference = addon.preference()

        if preference.keymap.enable_toolsettings:
            context.space_data.show_region_tool_header = True
            context.space_data.show_region_header = True

        if preference.cursor:
            context.window_manager.gizmo_group_type_ensure('bc.gizmogroup')
            context.window_manager.gizmo_group_type_ensure('bc.gridgizmo')

        if tool.active().idname != addon.name:
            is_active = tool.activate()

            if not is_active:
                self.report({'INFO'}, 'Failed to activate BoxCutter: mode is usupported')
                
                return {'CANCELLED'}

            toolbar.change_prop(context, 'mode', 'CUT')

            self.report({'INFO'}, 'Activated BoxCutter')

            context.workspace.tools.update()

            return {'FINISHED'}

        elif addon.hops() and not preference.keymap.enable_surface_toggle:
            tool.activate_by_id(context, 'VIEW_3D', 'Hops')

            self.report({'INFO'}, 'Activated HardOps')

            return {'FINISHED'}

        elif preference.keymap.enable_surface_toggle:
            if preference.transform_gizmo:
                context.window_manager.gizmo_group_type_ensure('bc.transformgizmogroup')

            if preference.surface == 'OBJECT':
                preference.surface = 'CURSOR'
                preference.cursor = True
                context.window_manager.gizmo_group_type_ensure('bc.gizmogroup')
                context.window_manager.gizmo_group_type_ensure('bc.gridgizmo')

            else:
                preference.surface = 'OBJECT'
                preference.cursor = False
                context.window_manager.gizmo_group_type_unlink_delayed('bc.gizmogroup')
                context.window_manager.gizmo_group_type_unlink_delayed('bc.gridgizmo')

            if preference.surface == 'OBJECT':
                self.report({'INFO'}, 'Drawing from Object')

            else:
                self.report({'INFO'}, 'Drawing from Cursor')

            context.workspace.tools.update()

            return {'FINISHED'}

        else:
            return {'PASS_THROUGH'}
