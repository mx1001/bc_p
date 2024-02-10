import bpy

from bpy.types import Panel

from .... utility import addon


class BC_PT_help_start_operation(Panel):
    bl_label = 'Start Operation'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.workspace'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'BC_PT_help'


    def draw(self, context):
        layout = self.layout

        bc = context.scene.bc

        layout.label(text='Begin with a modifier on the cutter;')

        row = layout.row()
        row.alignment = 'RIGHT'
        row.prop(bc, 'start_operation', text='', expand=True, icon_only=True)


class BC_PT_help_start_operation_npanel_tool(Panel):
    bl_label = 'Start Operation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_parent_id = 'BC_PT_help_npanel_tool'
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        BC_PT_help_start_operation.draw(self, context)


class BC_PT_help_start_operation_npanel(Panel):
    bl_label = 'Start Operation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_parent_id = 'BC_PT_help_npanel'
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        BC_PT_help_start_operation.draw(self, context)
