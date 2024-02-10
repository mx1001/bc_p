import bpy
from mathutils import Matrix, Vector

from . import axis, display, refresh, bevel

from ..... import toolbar

# from ... import shape
from ...... utility import addon, view3d
from .. import mesh, lattice


def change(op, context, event, to='NONE', modified=True, init=False, clear_mods=[], dot=False):
    preference = addon.preference()
    bc = context.scene.bc
    op.modified = modified

    if modified and op.lmb:
        op.modified_lock = True
    else:
        op.modified_lock = False

    if to == 'BEVEL_Q':
        bc.q_bevel = not bc.q_bevel
        bc.shape.data.bc.q_beveled = bc.q_bevel
        to = 'BEVEL'

    if not init:
        op.last['operation'] = op.operation

    for mod in bc.shape.modifiers:
        if mod.type in clear_mods:
            setattr(bc.shape.bc, mod.type.lower(), False)
            bc.shape.modifiers.remove(mod)

    if op.operation == 'DRAW' and op.shape_type == 'NGON':
        if not op.add_point and not preference.behavior.line_box:
            mesh.remove_point(op, context, event)

    elif op.operation in {'EXTRUDE', 'OFFSET', 'SCALE', 'ROTATE', 'MOVE'}:
        bc.plane.matrix_world = bc.shape.matrix_world
        op.start['matrix'] = bc.plane.matrix_world.copy()
        op.start['extrude'] = bc.lattice.data.points[lattice.back[0]].co_deform.z

    elif op.operation == 'ARRAY':
        axis_index = [bc.shape.bc.array_axis == axis for axis in 'XYZ'].index(True)

        for mod in bc.shape.modifiers:
            if mod.type == 'ARRAY':
                op.last['modifier']['offset'] = mod.constant_offset_displace[axis_index]
                op.last['modifier']['count'] = mod.count
                break

        # if modified:
            # if to == 'ARRAY' and bc.shape.bc.array_circle:
                # to = 'NONE'

        if to == 'ARRAY' and not bc.shape.bc.array_circle:
            bc.shape.bc.array_circle = True

            mesh.set_pivot(op, context)

        elif to == 'ARRAY' and op.operation == 'ARRAY' and bc.shape.bc.array_circle:
            bc.shape.bc.array_circle = False
            for mod in bc.shape.modifiers:
                if mod.type == 'ARRAY':
                    bc.shape.modifiers.remove(mod)
                elif mod.type == 'DISPLACE':
                    bc.shape.modifiers.remove(mod)

        # elif to != 'ARRAY':
            # axis.change(op, context, to='NONE')

        # elif to == 'NONE' and op.operation == 'ARRAY' and bc.shape.bc.array_circle:
            # to = 'NONE'

    elif op.operation == 'SOLIDIFY':
        obj = bc.shape if op.mode != 'INSET' else (op.datablock['slices'][-1] if op.datablock['slices'] else None)
        if obj:
            for mod in obj.modifiers:
                if mod.type == 'SOLIDIFY':
                    if op.mode != 'INSET':
                        op.last['modifier']['thickness'] = mod.thickness
                    else:
                        op.last['thickness'] = mod.thickness
                    break

            if modified:
                if to == 'SOLIDIFY': to = 'NONE'

        del obj

    elif op.operation == 'BEVEL':
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL' and not init:
                op.last['modifier']['width'] = mod.width
                op.last['modifier']['segments'] = mod.segments
                op.last['modifier']['limit_method'] = mod.limit_method
                if bpy.app.version < (2, 90, 0):
                    op.last['modifier']['use_only_vertices'] = mod.use_only_vertices
                else:
                    op.last['modifier']['affect'] = mod.affect
                op.last['modifier']['use_clamp_overlap'] = mod.use_clamp_overlap
                break

        op.last['mouse'] = op.mouse['location']

        if modified:
            if to == 'BEVEL':
                to = 'NONE'

    rebevel = False
    if (op.shape_type == 'NGON' and to == 'EXTRUDE'):
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                bc.shape.modifiers.remove(mod)

                rebevel = True

    if op.modified and op.alt_lock:
        op.alt_lock = False

    if to == 'ROTATE':
        op.last['mouse'] = op.mouse['location']
        op.last['location'] = bc.shape.matrix_world @ bc.shape.location
        op.last['local_pivot'] = op.ray['location'] if addon.preference().behavior.set_origin == 'MOUSE' else mesh.set_pivot(op, context)
        op.last['global_pivot'] = op.ray['location'] if addon.preference().behavior.set_origin == 'MOUSE' else bc.shape.matrix_world @ op.last['local_pivot']
        op.last['lattice_data'] = bc.lattice.data.copy()
        op.last['shape_data'] = bc.shape.data.copy()
        op.last['lattice'] = bc.lattice.copy()
        op.last['shape'] = bc.shape.copy()

    if op.operation == 'ROTATE':
        op.rotated = True

    if to == 'SCALE':
        op.last['mouse'] = op.mouse['location']
        op.last['location'] = bc.shape.matrix_world @ bc.shape.location
        op.last['local_pivot'] = op.ray['location'] if addon.preference().behavior.set_origin == 'MOUSE' else mesh.set_pivot(op, context)
        op.last['global_pivot'] = op.ray['location'] if addon.preference().behavior.set_origin == 'MOUSE' else bc.shape.matrix_world @ op.last['local_pivot']
        op.last['lattice_data'] = bc.lattice.data.copy()
        op.last['shape_data'] = bc.shape.data.copy()
        op.last['lattice'] = bc.lattice.copy()
        op.last['shape'] = bc.shape.copy()
        op.last['scale'] = (view3d.location3d_to_location2d(op.last['global_pivot']) - op.last['mouse']).length
        op.last['axis'] = 'XYZ'

    if op.operation == 'SCALE':
        op.scaled = True

    if to == 'MOVE':
        op.last['location'] = bc.shape.matrix_world @ bc.shape.location
        op.last['view3d_location'] = op.view3d['location']
        op.last['lattice'] = bc.lattice.copy()
        op.last['lattice'].bc.removeable = True
        op.last['shape'] = bc.shape.copy()
        op.last['shape'].bc.removeable = True
        op.last['axis'] = 'XY'

    if op.operation == 'MOVE':
        op.translated = True

    value = to

    op.operation = value
    toolbar.change_prop(context, 'operation', value)


    if value in {'EXTRUDE', 'OFFSET'}:
        mouse = op.mouse['location']

        bc.plane.matrix_world = bc.shape.matrix_world
        matrix = bc.plane.matrix_world
        inverse = matrix.inverted()

        front = (1, 2, 5, 6)
        back = (0, 3, 4, 7)
        side = front if value == 'OFFSET' else back
        coord = matrix @ (0.25 * sum((op.bounds[point] for point in side), Vector()))

        location = inverse @ view3d.location2d_to_location3d(mouse.x, mouse.y, coord)

        op.start['offset'] = location.z

    elif value == 'ROTATE':
        op.angle = 0
        op.last['track'] = op.mouse['location'] - view3d.location3d_to_location2d(bc.lattice.matrix_world.translation)
        op.last['mouse'] = op.mouse['location']
        bc.axis = 'Z' if bc.axis == 'NONE' else bc.axis

    elif value == 'ARRAY':
        bc.shape.bc.array = True

        # if bc.axis == 'NONE':
            # axis.change(op, context, to=bc.shape.bc.array_axis)

        axis_index = [bc.shape.bc.array_axis == axis for axis in 'XYZ'].index(True)

        for mod in bc.shape.modifiers:
            if mod.type == 'ARRAY':
                op.last['modifier']['offset'] = mod.constant_offset_displace[axis_index]
                op.last['modifier']['count'] = mod.count

                break

    elif value == 'SOLIDIFY':
        bc.shape.bc.solidify = True
        obj = bc.shape if op.mode != 'INSET' else op.datablock['slices'][-1]
        for mod in obj.modifiers:
            if mod.type == 'SOLIDIFY':
                if op.mode != 'INSET':
                    op.last['modifier']['thickness'] = mod.thickness
                else:
                    op.last['thickness'] = mod.thickness
                break

        del obj

        op.last['mouse'] = op.mouse['location']

    elif value == 'BEVEL':
        bc.shape.bc.bevel = True
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                preference.shape.bevel_segments = mod.segments
                bc.shape.modifiers.remove(mod)

        op.last['mouse'] = op.mouse['location']

    elif value == 'DISPLACE':
        displace = None

        for mod in bc.shape.modifiers:
            if mod.type == 'DISPLACE':
                displace = mod

                break

        if displace:
            op.start['displace'] = displace.strength / 2

    # if op.modified:
        # dots.collect(op)

    if not init:
        if value == 'NONE':
            op.report({'INFO'}, 'Shape Locked')

        else:
            op.report({'INFO'}, '{}{}{}'.format(
                'Added ' if value == 'ARRAY' else '',
                value.title()[:-1 if value in {'MOVE', 'ROTATE', 'SCALE', 'EXTRUDE', 'DISPLACE'} else len(value)],
                'ing' if value != 'ARRAY' else ''))

        refresh.shape(op, context, event, dot=dot)

    elif value != 'DRAW':
        refresh.shape(op, context, event)

    if rebevel:
        bevel.shape(op, context, event)

    if to != 'MOVE':
        op.move_lock = False
