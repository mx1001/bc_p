import bpy

from bpy.types import Operator
from bpy.props import BoolProperty

from .... utility import addon, object
from ... import toolbar
from mathutils import Matrix


class BC_OT_box(Operator):
    bl_idname = 'bc.box'
    bl_label = 'Box'
    bl_description = ('Draws using box shape utilizing corner draw by default.\n\n'
                      'Hotkeys :\n\n'
                      'Alt - center draw\n'
                      'Shift - square proportion constrain\n'
                      'Shift + Alt - center box draw\n'
                      'Period during draw toggles center draw if needed')
    bl_options = {'INTERNAL'}


    def execute(self, context):
        toolbar.options().shape_type = 'BOX'

        context.workspace.tools.update()

        return {'FINISHED'}


class BC_OT_circle(Operator):
    bl_idname = 'bc.circle'
    bl_label = 'Circle'
    bl_description = ('Draws using round plane figure whose boundary consists of points equidistant from the center.\n'
                      'Typically defaults to center draw.\n\n'
                      'Hotkeys :\n\n'
                      'Alt - free constrain\n'
                      'Alt + Shift - center contrain\n'
                      'Period during draw toggles corner / center draw if needed')
    bl_options = {'INTERNAL'}


    def execute(self, context):
        toolbar.options().shape_type = 'CIRCLE'

        context.workspace.tools.update()

        return {'FINISHED'}


class BC_OT_ngon(Operator):
    bl_idname = 'bc.ngon'
    bl_label = 'Ngon'
    bl_description = ('Draws using custom points determined by the user.\n'
                      'Hold Ctrl during draw to angle snap.\n'
                      'Line is also available by pressing C during draw')
    bl_options = {'INTERNAL'}


    def execute(self, context):
        toolbar.options().shape_type = 'NGON'

        context.workspace.tools.update()

        return {'FINISHED'}


class BC_OT_custom(Operator):
    bl_idname = 'bc.custom'
    bl_label = 'Custom'
    bl_description = ('Draws utilizing custom shape.\n'
                      'Without a specified mesh the boxcutter logo will be drawn\n'
                      'Specify custom mesh using dropdown in tool options or select mesh and press C\n'
                      'Capable of utilizing itself as cutter for self.cut')
    bl_options = {'INTERNAL'}

    set: BoolProperty(default=False)


    def execute(self, context):
        bc = context.scene.bc
        option = toolbar.options()

        obj = context.active_object
        assigned = False

        if not self.set:
            option.shape_type = 'CUSTOM'

        if self.set and obj and obj.type in {'MESH', 'FONT'} and option.shape_type == 'CUSTOM':
            assigned = True
            bc.shape = obj
            self.report({'INFO'}, F'Custom Shape: {bc.shape.name}')

        context.workspace.tools.update()

        if self.set and not assigned:
            return {'PASS_THROUGH'} # pass through for circle select

        return {'FINISHED'}
