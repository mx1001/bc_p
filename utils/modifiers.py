import bpy
import bmesh

def apply_modifiers(object, modtype):

    #objects = bpy.data.objects
    for obj in object, :
        if obj.type == "MESH":
            modifiers = obj.modifiers
            for mod in modifiers:
                if mod.type == modtype:
                    #bpy.context.scene.object.active = obj
                    bpy.ops.object.modifier_apply(apply_as="DATA",modifier=mod.name)

def create_solidify_modifier(object, thickness, offset= -1, use_even_offset = True , use_rim_only= False , use_quality_normals= True , show_on_cage= True  ):
    #object = bpy.context.active_object
    solidify = object.modifiers.new("Solidify", "SOLIDIFY")
    solidify.thickness = thickness
    solidify.use_even_offset = use_even_offset
    solidify.use_quality_normals = use_quality_normals
    solidify.use_rim_only = use_rim_only
    solidify.show_on_cage = show_on_cage
    solidify.offset = offset

