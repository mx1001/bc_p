import bpy

from math import radians

# from . displace import shape as displace_shape
from . import displace
# from .... utility import modifier
from .. import modifier
from ...... utility import addon, screen


def shape(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc
    snap = preference.snap.enable and (preference.snap.incremental or preference.snap.grid)

    negative = op.last['modifier']['offset'] < 0
    limit = 0.000001 if not negative else -0.000001
    modal = True
    array = None

    if event.type in {'X', 'Y', 'Z'} and event.value == 'PRESS':
        current = bc.shape.bc.array_axis
        axis = event.type
        index = 'XYZ'.index(axis)
        bc.shape.bc.array_axis = axis if current != axis else 'XYZ'[index + 1 if index != 2 else 0]

    axis_index = 'XYZ'.index(bc.shape.bc.array_axis)

    for mod in bc.shape.modifiers:
        if mod.type == 'ARRAY':
            array = mod

    existing_displace_mod= None
    for mod in bc.shape.modifiers:
        if mod.type == 'DISPLACE':
            existing_displace_mod = mod

    if bc.shape.bc.array_circle and not existing_displace_mod:

        if array:
            for mod in bc.shape.modifiers:
                if mod.type == 'ARRAY':
                    bc.shape.modifiers.remove(mod)

        displace.shape(op, context, event)

        array = bc.shape.modifiers.new(name='Array', type='ARRAY')
        array.show_in_editmode = False

        modifier.sort(bc.shape, ignore=modifier.bevels(bc.shape, props={'use_only_verts': True}), sort_types=modifier.sort_types, static_sort=True)

    elif bc.shape.bc.array_circle:
        displace.shape(op, context, event)

    if not array:
        array = bc.shape.modifiers.new(name='Array', type='ARRAY')
        array.count = preference.shape.array_count
        array.show_in_editmode = False
        array.use_constant_offset = True
        array.use_relative_offset = True

        array.constant_offset_displace[axis_index] = op.last['modifier']['offset'] if abs(op.last['modifier']['offset']) > 0.1 else 0.1
        array.relative_offset_displace[axis_index] = 1.0 if not negative else -1.0

        for index, _ in enumerate(array.constant_offset_displace[:]):
            if index != axis_index:
                array.relative_offset_displace[index] = 0.0

        op.last['modifier']['offset'] = array.constant_offset_displace[axis_index]

        modifier.sort(bc.shape, ignore=modifier.bevels(bc.shape, props={'use_only_verts': True}), sort_types=modifier.sort_types, static_sort=True)

        modal = False

    if not modal:
        return

    array.use_object_offset = bc.shape.bc.array_circle
    array.use_constant_offset = not bc.shape.bc.array_circle
    array.use_relative_offset = not bc.shape.bc.array_circle

    if not bc.shape.bc.array_circle:
        for m in bc.shape.modifiers:
            if m.type == 'DISPLACE':
                bc.shape.modifiers.remove(m)

        array.count = preference.shape.array_count
        array.constant_offset_displace[axis_index] = op.last['modifier']['offset'] if abs(op.last['modifier']['offset']) > abs(limit) else limit
        array.relative_offset_displace[axis_index] = 1.0 if not negative else -1.0
        array.offset_object = None

        for index, offset in enumerate(array.constant_offset_displace[:]):
            if index != axis_index:
                array.relative_offset_displace[index] = 0.0
                array.constant_offset_displace[index] = 0.0

    else:
        if array.count == 2:
            array.count = 3

        bc.empty.driver_remove('rotation_euler', 2)
        driver = bc.empty.driver_add('rotation_euler', 2).driver
        driver.type == 'SCRIPTED'

        count = driver.variables.new()
        count.name = 'count'
        count.targets[0].id_type = 'OBJECT'
        count.targets[0].id = bc.shape
        count.targets[0].data_path = F'modifiers["{array.name}"].count'

        driver.expression = 'radians(360 / count)'

        array.offset_object = bc.empty

    # modifier.sort(bc.shape, ignore=modifier.bevels(bc.shape, props={'use_only_verts': True}), sort_types=modifier.sort_types, static_sort=True)

    for index, offset in enumerate(array.constant_offset_displace[:]):
        if index != axis_index:
            array.relative_offset_displace[index] = 0.0
            array.constant_offset_displace[index] = 0.0

    if not bc.shape.bc.array_circle:
        array.count = 2 if array.count < 2 else array.count
        op.last['modifier']['count'] = array.count

        offset = (op.mouse['location'].x - op.last['mouse'].x) / screen.dpi_factor(ui_scale=False, integer=True)
        # factor = 0.0001 if event.shift and not event.ctrl else 0.001
        max_dimension = max(bc.shape.dimensions[:-1])
        factor = max_dimension * 0.0015 if event.shift and not event.ctrl else max_dimension * 0.015
        offset = op.last['modifier']['offset'] + offset * factor
        relative = 1.0 if offset > 0 else -1.0

        if snap and event.ctrl:
            increment_amount = round(preference.snap.increment, 8)
            split = str(increment_amount).split('.')[1]
            increment_length = len(split) if int(split) != 0 else 0

            if event.shift:
                offset = round(round(offset * 10 / increment_amount) * increment_amount, increment_length)
                offset *= 0.1

            else:
                offset = round(round(offset / increment_amount) * increment_amount, increment_length)

        op.last['mouse'].x = op.mouse['location'].x

        op.last['modifier']['offset'] = offset

        array.relative_offset_displace[axis_index] = relative if not bc.flip else -relative
        array.constant_offset_displace[axis_index] = offset if not bc.flip else -offset
