import bpy
from ... utils.objects import set_active, get_current_selected_status, mesh_of_activeobj_select
from ... utils.modifiers import create_solidify_modifier, apply_modifiers

class BoxCutterBoolSplit(bpy.types.Operator):
    """Split one shape from another """
    bl_idname = "boxcutter.bool_split"
    bl_label = "Box Cutter Split"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
            use_split_boolean_bmesh(False)
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVE':
            use_split_boolean_carve(False)
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
            use_split_boolean_carve(False)

        return {'FINISHED'}    

def use_split_boolean_bmesh(separtare = False):
    active_object, other_objects, other_object = get_current_selected_status()
    mesh_of_activeobj_select('DESELECT')
    for obj in other_objects:
        set_active(obj, select = False, only_select = False)
        mesh_of_activeobj_select('SELECT')
        create_solidify_modifier(obj, 0.00001)
        apply_modifiers(obj, 'SOLIDIFY')

    set_active(active_object, select = False, only_select = False)
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')
    if separtare:
        bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode = 'OBJECT')

def use_split_boolean_carve(separtare = False):
    active_object, other_objects, other_object = get_current_selected_status()
    if bpy.context.scene.BoxCutter_enable_hops == True:
        if separtare:
            bpy.ops.hops.complex_split_boolean()
        else:
            bpy.ops.hops.complex_split_boolean(split_mesh=False)

        bpy.ops.object.select_all(action='DESELECT')
        for obj in other_objects:
            bpy.ops.hops.soft_sharpen()
            obj.select = True
            bpy.ops.object.delete(use_global=False)
    else:
        mesh_of_activeobj_select('DESELECT')
        for obj in other_objects:
            boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
            boolean.operation = 'DIFFERENCE'
            boolean.object = obj

            set_active(obj, select = False, only_select = False)
            mesh_of_activeobj_select('SELECT')
            create_solidify_modifier(obj, 0.00001)
            apply_modifiers(obj, 'SOLIDIFY')
      
        set_active(active_object, select = False, only_select = False)
        apply_list = [active_object] 
        apply_modifiers(active_object, 'BOOLEAN')
        bpy.ops.object.select_all(action='DESELECT')
        for obj in other_objects:
            bpy.ops.hops.soft_sharpen()

            obj.select = True
            bpy.ops.object.delete(use_global=False)

        if separtare:
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode = 'OBJECT')

def use_split_boolean_carve_mod(separtare = False):
    active_object, other_objects, other_object = get_current_selected_status()
    mesh_of_activeobj_select('DESELECT')
    for obj in other_objects:
        obj.draw_type = 'BOUNDS'
        boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
        boolean.operation = 'DIFFERENCE'
        boolean.object = obj

        set_active(obj, select = False, only_select = False)
        mesh_of_activeobj_select('SELECT')
        create_solidify_modifier(obj, 0.00001)
        apply_modifiers(obj, 'SOLIDIFY')

    bpy.ops.object.select_all(action='DESELECT')
    set_active(active_object, select = False, only_select = False)
  
    
