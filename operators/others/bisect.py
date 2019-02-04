import bpy


class BoxCutterBisect(bpy.types.Operator):
        """Draw a box from 2d shape """
        bl_idname = "boxcutter.bisect"
        bl_label = "Box Cutter Bisect"
        bl_options = {'REGISTER', 'UNDO'}


        def execute(self, context):
            try :
                if context.active_object.mode == 'OBJECT':
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.bisect('INVOKE_DEFAULT')

                elif context.active_object.mode == 'EDIT':
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.bisect('INVOKE_DEFAULT')
            except:
            	pass

            return {'FINISHED'}
        