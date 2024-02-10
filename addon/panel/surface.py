import bpy

from bpy.types import Panel

from ... utility import tool, addon
from .. import toolbar


class BC_PT_surface(Panel):
    bl_label = 'Surface'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'


    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        preference = addon.preference()
        # bc = context.scene.bc
        # option = toolbar.options()

        layout = self.layout

        if self.is_popover:
            layout.ui_units_x = 12

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        row = layout.row(align=True)
        row.scale_x = 1.5
        row.scale_y = 1.5
        if not self.is_popover:
            flow = row.column()
            row = flow.row()
        row.prop(preference, 'surface', expand=True, icon_only=not self.is_popover)

        if preference.surface not in {'OBJECT', 'VIEW'}:
            # row = layout.row(align=True)
            # row.scale_y = 1.25
            # row.prop(option, 'align_to_view', icon='VIEW_ORTHO' if option.align_to_view else 'VIEW_PERSPECTIVE')

            # else:
            row = layout.row(align=True)
            row.scale_y = 1.25
            row.prop(preference, 'axis', expand=True)

        #added by me
        if preference.surface in {'VIEW'}:
            row = layout.row(align=True)
            row.scale_y = 1.25
            row.prop(preference.behavior, 'auto_ortho', text = "Auto Ortho")
            row = layout.row(align=True)
            inputs = context.preferences.inputs
            if inputs.use_auto_perspective:
                row.prop(inputs, "use_auto_perspective")
                row.label(text = "Off (best)")

        row = layout.row(align=True)
        row.scale_x = 1.25
        row.scale_y = 1.25
        row.label(text='Gizmo')

        # if preference.grid_gizmo:
        #     row.operator('bc.grid_remove_gizmo', text='', icon='CANCEL')
        # else:
        #     row.operator('bc.grid_add_gizmo', text='', icon='VIEW_PERSPECTIVE')

        # if preference.cursor:
        #     row.operator('bc.cursor3d_remove_gizmo', text='', icon='CANCEL')
        # else:
        #     row.operator('bc.cursor3d_add_gizmo', text='', icon='PIVOT_CURSOR')

        if preference.transform_gizmo:
            row.operator('bc.transform_remove_gizmo', text='', icon='CANCEL')
        else:
            row.operator('bc.transform_add_gizmo', text='', icon='ORIENTATION_GLOBAL')
