import bpy

class BoxCutterAddCube(bpy.types.Operator):
        """Draw an cube with the mouse"""
        bl_idname = "boxcutter.add_cube"
        bl_label = "Box Cutter Add Cube"
        bl_options = {'REGISTER', 'UNDO'}
        
        def execute(self, context):
            bpy.ops.mesh.primitive_cube_add(radius=0.2, view_align=False)
            bpy.ops.transform.resize('INVOKE_DEFAULT')
            return {'FINISHED'}