import bpy

def only_select(objects):
    if not hasattr(objects, "__iter__"): objects = [objects]
    deselect_all()
    for object in objects:
        object.select = True

def deselect_all():
    for object in bpy.data.objects:
        object.select = False

def set_active(object, select = False, only_select = False):
    bpy.context.scene.objects.active = object
    if only_select: deselect_all()
    if select or only_select: bpy.context.scene.objects.active.select = True

def get_current_selected_status():
    active_object = bpy.context.active_object
    other_objects = get_inactive_selected_objects()
    other_object = None
    if len(other_objects) == 1:
            other_object = other_objects[0]

    return active_object, other_objects, other_object

def get_inactive_selected_objects():
    selected_objects = list(bpy.context.selected_objects)
    if bpy.context.active_object in selected_objects:
        selected_objects.remove(bpy.context.active_object)
    return selected_objects

def mesh_of_activeobj_select(select = 'SELECT'):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.reveal()
    if select == 'SELECT':
        bpy.ops.mesh.select_all(action='SELECT')
    elif select == 'DESELECT':
        bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

def show_obj_wires(context, enable):
    if enable:
        bpy.context.object.show_wire = True
        bpy.context.object.show_all_edges = True
    else:
        bpy.context.object.show_wire = False
        bpy.context.object.show_all_edges = False