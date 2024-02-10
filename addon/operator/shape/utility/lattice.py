import bpy

from mathutils import Vector, Matrix

from ..... utility import addon

back = (4, 5, 6, 7)
front = (0, 1, 2, 3)
left = (0, 2, 4, 6)
right = (1, 3, 5, 7)
top = (2, 3, 6, 7)
bottom = (0, 1, 4, 5)


def thickness_clamp(context):
    bc = context.scene.bc
    factor = 0.005
    thickness = min(bc.shape.dimensions[:-1]) * factor
    offset = addon.preference().shape.offset

    return thickness if thickness < offset else offset - 0.001


def create(op, context, event, zero=True):
    bc = context.scene.bc

    dat = bpy.data.lattices.new(name='Lattice')
    dat.bc.removeable = True
    bc.lattice = bpy.data.objects.new(name='Lattice', object_data=dat)
    # bc.lattice = bc.lattice

    bc.collection.objects.link(bc.lattice)

    dat.interpolation_type_u = 'KEY_LINEAR'
    dat.interpolation_type_v = 'KEY_LINEAR'
    dat.interpolation_type_w = 'KEY_LINEAR'

    del dat

    if op.shape_type != 'NGON':
        mod = bc.shape.modifiers.new(name='Lattice', type='LATTICE')
        mod.object = bc.lattice

    bc.lattice.hide_set(True)
    bc.shape.hide_set(True)

    bc.lattice.data.transform(bc.lattice.matrix_world.copy().Translation(Vector((0.0, 0.0, -0.5))))

    if op.origin == 'CORNER':
        bc.lattice.data.transform(bc.lattice.matrix_world.copy().Translation(Vector((0.5, 0.5, 0.0))))

    if zero:
        for point in (0, 1, 2, 3, 4, 5, 6, 7):
            bc.lattice.data.points[point].co_deform.x = 0
            bc.lattice.data.points[point].co_deform.y = 0

        for point in front:
            bc.lattice.data.points[point].co_deform.z = 0

        for point in back:
            bc.lattice.data.points[point].co_deform.z = -0.001


def center(matrix, side=''):
    bc = bpy.context.scene.bc
    sides = {
        'front': front,
        'back': back,
        'left': left,
        'right': right,
        'top': top,
        'bottom': bottom}

    if not side:
        return matrix @ (0.125 * sum((Vector(bc.lattice.data.points[point].co_deform[:]) for point in (0, 1, 2, 3, 4, 5, 6, 7)), Vector()))
    else:
        return matrix @ (0.25 * sum((Vector(bc.lattice.data.points[point].co_deform[:]) for point in sides[side]), Vector()))


def draw(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc
    snap = preference.snap.enable and (preference.snap.incremental or preference.snap.grid)
    snap_lock = snap and preference.snap.increment_lock
    points = bc.lattice.data.points

    location_x = op.view3d['location'].x
    location_y = op.view3d['location'].y

    if bc.shape.bc.array and bc.shape.bc.array_circle:
        displace = None

        for mod in bc.shape.modifiers:
            if mod.type == 'DISPLACE':
                displace = mod

                break

        if displace:
            location_x = op.view3d['location'].x - displace.strength / 2

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.snap.increment, 8)
        split = str(increment_amount).split('.')[1]

        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_x = round(round(location_x * 10 / increment_amount) * increment_amount, increment_length)
            location_x *= 0.1
            limit = increment_amount * 0.1

            if op.view3d['location'].x < 0:
                limit = -limit

            if location_x == 0:
                location_x += limit

            location_y = round(round(location_y * 10 / increment_amount) * increment_amount, increment_length)
            location_y *= 0.1

            if location_y == 0:
                location_y += limit

        else:
            location_x = round(round(location_x / increment_amount) * increment_amount, increment_length)
            limit = preference.snap.increment

            if op.view3d['location'].x < 0:
                limit = -limit

            if location_x == 0:
                location_x += limit

            location_y = round(round(location_y / increment_amount) * increment_amount, increment_length)

            if location_y == 0:
                location_y += limit

    draw_dot_index = ((2, 1), (6, 5))
    index1 = 0 if op.view3d['location'].x < op.view3d['origin'].x else 1
    draw_dot_index = draw_dot_index[index1]
    sides = ('left', 'right')
    side = globals()[sides[index1]]
    clear = globals()[sides[not index1]]

    use_alt = event.alt and preference.keymap.alt_draw # and not event.ctrl
    use_shift = event.shift and preference.keymap.shift_draw # and not event.ctrl

    if use_alt and not use_shift:

        for point in side:
            points[point].co_deform.x = location_x
        for point in clear:
            points[point].co_deform.x = -location_x

    elif use_shift and not use_alt:

        for point in side:
            points[point].co_deform.x = location_x
        for point in clear:
            points[point].co_deform.x = 0

    elif use_shift and use_alt:

        for point in side:
            points[point].co_deform.x = location_x
        for point in clear:
            points[point].co_deform.x = -location_x

    elif not use_alt or not use_shift:

        for point in side:
            points[point].co_deform.x = location_x

        if op.origin == 'CORNER':
            for point in clear:
                points[point].co_deform.x = 0

        elif op.origin == 'CENTER':
            for point in clear:
                points[point].co_deform.x = -location_x

    index2 = 0 if op.view3d['location'].y > op.view3d['origin'].y else 1
    draw_dot_index = draw_dot_index[index2]
    sides = ('bottom', 'top')
    side = globals()[sides[index2]]
    clear = globals()[sides[not index2]]

    if use_alt and not use_shift:

        for point in side:
            points[point].co_deform.y = location_y
        for point in clear:
            points[point].co_deform.y = -location_y

    elif use_shift and not use_alt:

        for point in side:
            points[point].co_deform.y = location_x if index1 != index2 else -location_x
        for point in clear:
            points[point].co_deform.y = 0

    elif use_shift and use_alt:

        for point in side:
            points[point].co_deform.y = location_x if index1 != index2 else -location_x
        for point in clear:
            points[point].co_deform.y = -location_x if index1 != index2 else location_x

    elif not use_alt or not use_shift:
        if op.origin == 'CENTER':
            for point in side:
                points[point].co_deform.y = location_x if index1 != index2 else -location_x

        else:
            for point in side:
                points[point].co_deform.y = location_y

        if op.origin == 'CENTER':
            for point in clear:
                points[point].co_deform.y = -location_x if index1 != index2 else location_x

        else:
            for point in clear:
                points[point].co_deform.y = 0

    op.draw_dot_index = draw_dot_index


def offset(op, context, event):
    preference = addon.preference()
    offset = preference.shape.offset

    if not op.modified:
        if op.mode == 'MAKE':
            offset = 0
        elif op.mode == 'JOIN':
            offset = -offset
    else:
        offset = 0

    bc = context.scene.bc
    snap = preference.snap.enable and (preference.snap.incremental or preference.snap.grid)
    snap_lock = snap and preference.snap.increment_lock
    shape = bc.shape
    lat = bc.lattice
    points = lat.data.points

    location_z = op.view3d['location'].z

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.snap.increment, 8)
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
            location_z *= 0.1

        else:
            location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

    if location_z > op.start['extrude']:
        location = location_z + offset
        matrix = op.start['matrix'] @ Matrix.Translation(Vector((0, 0, location)))
        shape.matrix_world.translation = matrix.translation
        lat.matrix_world.translation = matrix.translation

        for point in back:
            points[point].co_deform.z = -location_z + op.start['extrude']

    else:
        location = op.start['extrude'] + offset
        matrix = op.start['matrix'] @ Matrix.Translation(Vector((0, 0, location)))
        shape.matrix_world.translation = matrix.translation
        lat.matrix_world.translation = matrix.translation

        for point in back:
            points[point].co_deform.z = -thickness_clamp(context)


def extrude(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc
    snap = preference.snap.enable and (preference.snap.incremental or preference.snap.grid)
    snap_lock = snap and preference.snap.increment_lock
    points = bc.lattice.data.points

    location_z = op.view3d['location'].z

    if not op.extruded:
        op.extruded = True

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.snap.increment, 8)
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
            location_z *= 0.1

        else:
            location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

    for point in back:
        points[point].co_deform.z = location_z if location_z < -thickness_clamp(context) else -thickness_clamp(context)
