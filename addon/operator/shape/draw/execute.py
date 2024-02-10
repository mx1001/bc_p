import bpy

from mathutils import Vector

from ..... utility import addon, object, modifier
# from ... utility.shape.change import last
from .. utility.change import last
# from ... utility import shape
from .. import utility
from .. utility import statusbar
# from .. utility import statusbar

# from .... property import prop


def operator(op, context):
    preference = addon.preference()
    bc = context.scene.bc

    bc.running = False
    statusbar.remove()

    bc.shape.bc.target = context.active_object

    if op.original_mode == 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='OBJECT')

    # if op.shape_type != 'NGON' and sum(int(dimension < preference.shape.lazorcut_limit) for dimension in bc.shape.dimensions[:-1]) > 1:
    if sum(int(dimension < preference.shape.lazorcut_limit) for dimension in bc.shape.dimensions[:-1]) > 1:
        op.origin = last['origin']

        if op.last['geo']['verts']:
            dat = bpy.data.meshes.new(name='Cutter')

            verts = op.last['geo']['verts']
            edges = op.last['geo']['edges']
            faces = op.last['geo']['faces']

            dat.from_pydata(verts, edges, faces)
            dat.validate()

            if preference.behavior.auto_smooth:
                if not dat.use_auto_smooth:
                    dat.use_auto_smooth = True

                    for face in dat.polygons:
                        face.use_smooth = True

            bc.shape.data = dat

            del dat

            for mod in bc.shape.modifiers:
                bc.shape.modifiers.remove(mod)

    for mod in bc.shape.modifiers:
        if mod.type == 'SOLIDIFY':
            mod.show_viewport = False

        if mod.type == 'MIRROR':
            mod.show_viewport = False

    context.view_layer.update()

    # TODO: Use lattice coords instead of dimensions, immediate/accurate lazorcut check
    if bc.shape.dimensions[2] < preference.shape.lazorcut_limit and not op.repeat:
        utility.lazorcut(op, context)

    if not op.repeat and op.mode == 'KNIFE' and preference.surface == 'VIEW' and bc.shape.dimensions[2] < preference.shape.lazorcut_limit:
        op.lazorcut = True

    for mod in bc.shape.modifiers:
        if mod.type == 'MIRROR':
            mod.show_viewport = True

    last['origin'] = op.origin
    last['points'] = [Vector(point.co_deform) for point in bc.lattice.data.points]

    for mod in bc.shape.modifiers:
        if mod.type == 'ARRAY' and not mod.use_object_offset:
            offsets = [abs(o) for o in mod.constant_offset_displace]
            if sum(offsets) < 0.0005:
                bc.shape.modifiers.remove(mod)

            else:
                index = offsets.index(max(offsets))
                last['modifier']['offset'] = mod.constant_offset_displace[index]
                last['modifier']['count'] = mod.count

        elif mod.type == 'BEVEL':
            if mod.width < 0.0005:
                bc.shape.modifiers.remove(mod)

            else:
                last['modifier']['width'] = mod.width if mod.width > last['modifier']['width'] else last['modifier']['width']
                last['modifier']['segments'] = mod.segments

        elif mod.type == 'SOLIDIFY':
            if abs(mod.thickness) < 0.0005:
                bc.shape.modifiers.remove(mod)

            else:
                last['modifier']['thickness'] = mod.thickness

    if not op.repeat:
        duplicate = object.duplicate(bc.shape, link=bc.collection)
        original_active = context.active_object
        context.view_layer.objects.active = duplicate
        duplicate.data.bc.removeable = True

        modifier.apply(duplicate)
        last['geo']['verts'] = [vertex.co.copy() for vertex in duplicate.data.vertices]
        last['geo']['edges'] = duplicate.data.edge_keys[:]
        last['geo']['faces'] = [face.vertices[:] for face in duplicate.data.polygons]

        context.view_layer.objects.active = original_active

        bpy.data.objects.remove(duplicate)

        del duplicate

    if op.original_mode == 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')

    op.update()

    # op.shader.exit = True
    # op.widgets.exit = True

    utility.data.clean(op, context)

    # if preference.display.dots:
    #    op.widgets.remove()
    # bpy.types.SpaceView3D.draw_handler_remove(op.dot_handler, 'WINDOW')
    # op.widgets.exit = True
    op.report({'INFO'}, 'Executed')

    return {'FINISHED'}
