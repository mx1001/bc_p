import bpy

from .. import modifier
# from .... utility import modifier



# TODO: move shape display here
class shape:


    def boolean(op, display=False):
        bc = bpy.context.scene.bc
        show = op.live if not display else display

        original_active = bpy.context.view_layer.objects.active

        if bc.shape.dimensions[2] > 0.001:
            for obj in op.datablock['targets']:
                if op.mode == 'INSET':
                    for mod in reversed(obj.modifiers):
                        if mod.type == 'BOOLEAN' and mod.object and mod.object.bc.inset:
                            shown = mod.show_viewport
                            mod.show_viewport = show

                            if show and not shown:
                                bc.shape.hide_set(False)
                                bpy.context.view_layer.objects.active = bc.shape
                                bc.shape.select_set(True)

                                bc.shape.hide_set(True)
                                bc.shape.select_set(False)

                                bpy.context.view_layer.objects.active = original_active

                            break

                if modifier.shape_bool(obj):
                    modifier.shape_bool(obj).show_viewport = show if op.mode != 'INSET' else False

            for obj in op.datablock['slices']:
                if modifier.shape_bool(obj):
                    modifier.shape_bool(obj).show_viewport = show

        else:
            for obj in op.datablock['targets']:
                if op.mode == 'INSET':
                    for mod in reversed(obj.modifiers):
                        if mod.type == 'BOOLEAN' and mod.object and mod.object.bc.inset:
                            mod.show_viewport = False
                            break

                if modifier.shape_bool(obj):
                    modifier.shape_bool(obj).show_viewport = False

            for obj in op.datablock['slices']:
                if modifier.shape_bool(obj):
                    modifier.shape_bool(obj).show_viewport = False
