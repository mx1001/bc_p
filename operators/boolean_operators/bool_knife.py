import bpy

from ... utils.objects import get_current_selected_status


#Edgard Funcion
class KnifeCutterBoll(bpy.types.Operator):
    """Boolean one shape to another """
    bl_idname = "boxcutter.knife_bool"
    bl_label = "Box Knife Cutter Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
            use_knife_cut('KNIFE',self, context)
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVE':
            use_knife_cut('KNIFE')
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
            use_knife_cut('KNIFE',self, context)
        return {'FINISHED'}    

#def use_knife_cut(boolean_method = 'DIFFERENCE', self,context):
def use_knife_cut(boolean_method = 'DIFFERENCE'):
    object_active =get_current_selected_status() 
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect()
    bpy.ops.mesh.bevel(offset=0.1)    
   #bpy.ops.view3d.edit_mesh_extrude_move_shrink_fatten(TRANSFORM_OT_shrink_fatten={"value":1})
    bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_shrink_fatten={"value":bpy.context.scene.BoxCutter_valCut_loop, "use_even_offset":False, "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "release_confirm":False})    
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    #bpy.ops.mesh.primitive_cube_add(location=(region_height/10,region_width/10,0))