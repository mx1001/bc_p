import bpy


from bpy.types import Operator
from bpy.props import EnumProperty

from ... utility import modifier


class BC_OT_smart_apply(Operator):
    bl_idname = 'bc.smart_apply'
    bl_label = 'Smart Apply'
    bl_description = '\n Applies Boolean Modifiers'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        targets = []
        modifiers = {}

        cutters = []

        bool_mods = lambda mods: [mod for mod in mods if mod.type == 'BOOLEAN' and mod.object]

        mode = context.active_object.mode

        if mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        def collect_target(obj, mod):
            if obj not in targets:
                targets.append(obj)

            if obj.name not in modifiers:
                modifiers[obj.name] = [mod]

            elif obj.name in modifiers and mod not in modifiers[obj.name]:
                modifiers[obj.name].append(mod)


        def collect(obj, mod):
            collect_target(obj, mod)

            if mod.object not in cutters:
                cutters.append(mod.object)


        for obj in context.visible_objects:
            for mod in bool_mods(obj.modifiers):
                if mod.object.select_get():
                    collect(obj, mod)

        if not cutters:
            for obj in context.selected_objects:
                for mod in bool_mods(obj.modifiers):
                    collect(obj, mod)

        if True in [obj.select_get() for obj in targets]:
            for obj in context.visible_objects:
                for mod in bool_mods(obj.modifiers):
                    if mod.object in cutters and not obj.select_get():
                        cutters.remove(mod.object)

                if obj in targets and not obj.select_get():
                    targets.remove(obj)

        for obj in targets:
            obj.select_set(True)
            context.view_layer.objects.active = obj
            modifier.apply(obj, modifiers=modifiers[obj.name])

        for obj in cutters:
            bpy.data.meshes.remove(obj.data)

        if mode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        del targets
        del modifiers
        del cutters

        return {'FINISHED'}
