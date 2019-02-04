import bpy

from ... utils.objects import set_active, get_current_selected_status, mesh_of_activeobj_select
from ... utils.modifiers import apply_modifiers

class BoxCutterBoolUnion(bpy.types.Operator):
    """Boolean one shape to another """
    bl_idname = "boxcutter.bool_union"
    bl_label = "Box Cutter Union Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
            use_bmesh_boolean('UNION')
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVE':
            use_carve_boolean('UNION')
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
            use_carve_mod_boolean('UNION')
        return {'FINISHED'}    


class BoxCutterBoolDifference(bpy.types.Operator):
    """Boolean one shape to another """
    bl_idname = "boxcutter.bool_difference"
    bl_label = "Box Cutter Difference Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
            use_bmesh_boolean('DIFFERENCE')
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVE':
            use_carve_boolean('DIFFERENCE')
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
            use_carve_mod_boolean('DIFFERENCE')
        return {'FINISHED'}   


class BoxCutterBoolIntersect(bpy.types.Operator):
    """Boolean one shape to another """
    bl_idname = "boxcutter.bool_intersect"
    bl_label = "Box Cutter Intersect Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
            use_bmesh_boolean('INTERSECT')
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVE':
            use_carve_boolean('INTERSECT')
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
            use_carve_mod_boolean('INTERSECT')
        return {'FINISHED'}   


def use_bmesh_boolean(boolean_method = 'DIFFERENCE'):
    active_object, other_objects, other_object = get_current_selected_status()
    mesh_of_activeobj_select('DESELECT')
    for obj in other_objects:
        set_active(obj, select = False, only_select = False)
        mesh_of_activeobj_select('SELECT')
        #if split:

    set_active(active_object, select = False, only_select = False)
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    if  boolean_method == 'DIFFERENCE':
        bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')
    elif boolean_method == 'UNION':
        bpy.ops.mesh.intersect_boolean(operation='UNION')
    elif boolean_method == 'INTERSECT':
        bpy.ops.mesh.intersect_boolean(operation='INTERSECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')


def use_carve_boolean(boolean_method = 'DIFFERENCE'):
    active_object, other_objects, other_object = get_current_selected_status()
    for obj in other_objects:
        obj.draw_type = 'BOUNDS'
        boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
        if  boolean_method == 'DIFFERENCE':
            boolean.operation = 'DIFFERENCE'
        elif boolean_method == 'UNION':
            boolean.operation = 'UNION'
        elif boolean_method == 'INTERSECT':
           boolean.operation = 'INTERSECT'
        boolean.object = obj
    apply_list = [active_object] 
    apply_modifiers(active_object, 'BOOLEAN')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in other_objects:
        obj.select = True
        bpy.ops.object.delete(use_global=False)


def use_carve_mod_boolean(boolean_method = 'DIFFERENCE'):
    active_object, other_objects, other_object = get_current_selected_status()
    for obj in other_objects:
        obj.draw_type = 'WIRE'
        
        #Add Boolshape Sstatus
        try: 
            obj.hops.status = "BOOLSHAPE"
        except:
            pass

        boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
        if  boolean_method == 'DIFFERENCE':
            boolean.operation = 'DIFFERENCE'
        elif boolean_method == 'UNION':
            boolean.operation = 'UNION'
        elif boolean_method == 'INTERSECT':
           boolean.operation = 'INTERSECT'
        boolean.object = obj
    set_active(active_object, select = True, only_select = True)
    
 