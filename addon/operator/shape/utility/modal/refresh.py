import bpy
from mathutils import Vector

from . import array, axis, behavior, bevel, displace, display, draw, extrude, mode, move, offset, operation, origin, ray, refresh, solidify, rotate, scale

# from ... import shape
from ...... utility import addon, view3d
# from ... import shape as _shape
from .. import modifier, mesh


def shape(op, context, event, dot=False):
    preference = addon.preference()
    wm = context.window_manager
    bc = context.scene.bc

    if not op.bounds:
        return

    mouse = op.mouse['location']

    if bc.running:
        matrix = bc.plane.matrix_world
        inverse = matrix.inverted()

        normal = matrix.to_3x3() @ Vector((0, 0, 1))

        try:
            intersect = inverse @ view3d.location2d_to_intersect3d(mouse.x, mouse.y, op.ray['location'], normal)
        except:
            intersect = op.mouse['intersect']

        op.mouse['intersect'] = intersect
        op.view3d['origin'] = 0.125 * sum((op.bounds[point] for point in (0, 1, 2, 3, 4, 5, 6, 7)), Vector())

        front = (1, 2, 5, 6)
        back = (0, 3, 4, 7)
        side = back if op.operation == 'EXTRUDE' else front
        coord = matrix @ (0.25 * sum((op.bounds[point] for point in side), Vector()))

        thin = bc.lattice.dimensions[2] < 0.0001

        location = inverse @ view3d.location2d_to_location3d(mouse.x, mouse.y, coord)
        start_offset = op.start['offset'] if op.operation == 'EXTRUDE' else op.start['offset'] + op.start['extrude']
        op.view3d['location'] = Vector((op.mouse['intersect'].x, op.mouse['intersect'].y, location.z - start_offset + op.start['extrude']))

        if dot:
            if op.operation == 'DRAW' and op.shape_type == 'NGON':
                index = -1
                for dot in op.widget.dots:
                    if dot.type == 'DRAW' and dot.highlight:
                        index = dot.index

                        break

                # if index != -1:
                    # break

                if index != -1:
                    draw.shape(op, context, event, index=index)

            else:
                globals()[op.operation.lower()].shape(op, context, event)

        elif op.operation != 'NONE':
            globals()[op.operation.lower()].shape(op, context, event)

        if context.active_object:
            if modifier.shape_bool(context.active_object):
                display.shape.boolean(op)

        if op.operation not in {'NONE', 'BEVEL', 'ARRAY'} and not bc.shape.bc.copy:
            for mod in bc.shape.modifiers:
                if mod.type == 'BEVEL':
                    mod.width = op.last['modifier']['width'] if op.last['modifier']['width'] > 0.0004 else 0.0004

                    if mod.width > bevel.clamp(op):
                        mod.width = bevel.clamp(op) - 0.0025

                elif mod.type == 'SOLIDIFY':
                    mod.show_viewport = bc.lattice.dimensions[2] > 0.001 or op.shape_type == 'NGON'

        if (op.operation != 'DRAW' or (preference.keymap.release_lock and preference.keymap.release_lock_lazorcut and preference.keymap.quick_execute) or op.original_mode == 'EDIT_MESH') and op.live:
            if op.mode in {'CUT', 'SLICE', 'INTERSECT', 'INSET', 'JOIN', 'EXTRACT'}:
                if hasattr(wm, 'Hard_Ops_material_options'):
                    bc.shape.hops.status = 'BOOLSHAPE'

                if bc.shape.display_type != 'WIRE':
                    bc.shape.display_type = 'WIRE'
                    bc.shape.hide_set(False)

                if not modifier.shape_bool(context.active_object):
                    modifier.create(op)

                if op.original_mode == 'EDIT_MESH':

                    for target in op.datablock['targets']:
                        for mod in target.modifiers:
                            if mod != modifier.shape_bool(target):
                                mod.show_viewport = False

                                if op.mode == 'INSET' and mod.type == 'BOOLEAN' and mod.object in op.datablock['slices'] and not thin:
                                    mod.show_viewport = True

                    modifier.update(op, context)

            elif op.mode == 'MAKE':
                if hasattr(wm, 'Hard_Ops_material_options'):
                    bc.shape.hops.status = 'UNDEFINED'

                if bc.shape.display_type != 'TEXTURED':
                    bc.shape.display_type = 'TEXTURED'
                    bc.shape.hide_set(True)

                if op.datablock['targets']:
                    if modifier.shape_bool(context.active_object):
                        modifier.clean(op)

            elif op.mode == 'KNIFE':
                if hasattr(wm, 'Hard_Ops_material_options'):
                    bc.shape.hops.status = 'UNDEFINED'

                if bc.shape.display_type != 'WIRE':
                    bc.shape.display_type = 'WIRE'
                    bc.shape.hide_set(False)

                if modifier.shape_bool(context.active_object):
                    modifier.clean(op)

                mesh.knife(op, context, event)

        if op.shape_type == 'NGON' and not preference.behavior.line_box:
            screw = None
            for mod in bc.shape.modifiers:
                if mod.type == 'SCREW' and mod.angle == 0:
                    screw = mod

                    break

            if not screw and not context.scene.bc.cyclic and not op.extruded:
                mod = bc.shape.modifiers.new(name='Screw', type='SCREW')
                mod.screw_offset = -0.001
                mod.angle = 0
                mod.steps = 2
                mod.render_steps = 2

                for mod in bc.shape.modifiers:
                    if mod.type == 'WELD':
                        mod.show_viewport = False

            elif screw and (context.scene.bc.cyclic or op.extruded):
                bc.shape.modifiers.remove(screw)

            solidify = None
            for mod in bc.shape.modifiers:
                if mod.type == 'SOLIDIFY' and mod.offset == 0:
                    solidify = mod

                    break

            if not solidify and not context.scene.bc.cyclic:
                mod = bc.shape.modifiers.new(name='Solidify', type='SOLIDIFY')
                mod.offset = 0
                mod.use_even_offset = True
                mod.use_quality_normals = True
                mod.thickness = op.last['modifier']['thickness']

            elif solidify and context.scene.bc.cyclic:
                bc.shape.modifiers.remove(solidify)

        weld = None
        for mod in bc.shape.modifiers:
            if mod.type == 'WELD':
                weld = mod
                break

        if not weld:
            return

        dimensions = bc.shape.dimensions[:-1]
        below_thresh = weld.merge_threshold < sum(dimensions)

        if below_thresh:
            weld.merge_threshold = sum(dimensions) * 0.001

        elif sum(dimensions) * 0.01 > weld.merge_threshold and weld.merge_threshold != 0.0001:
            weld.merge_threshold = 0.0001
