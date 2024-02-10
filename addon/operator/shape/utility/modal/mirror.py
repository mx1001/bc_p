# from .... utility import modifier
from .. import modifier


def shape(op, context, event, to=None, flip=False):
    bc = context.scene.bc

    index = {
        'X': 0,
        'Y': 1,
        'Z': 2}

    mirror = None

    for mod in bc.shape.modifiers:
        if mod.type == 'MIRROR':
            mirror = mod

            break

    if not mirror:
        mirror = bc.shape.modifiers.new(name='Mirror', type='MIRROR')
        mirror.use_axis[0] = False

        if context.active_object:
            mirror.mirror_object = context.active_object

    # if to and mirror.use_axis[index[to]] and not bc.mirror_axis_flip[index[to]]:
        # flip = True

    init_enabled = tuple(a for a in mirror.use_axis)

    if not flip:
        for i in range(len(mirror.use_axis)):
            mirror.use_axis[i] = False
            mirror.use_bisect_axis[i] = False

    for i in range(len(mirror.use_bisect_flip_axis)):
        mirror.use_bisect_flip_axis[i] = False

    if not flip:
        if to:
            bc.mirror_axis[index[to]] = int(not bool(bc.mirror_axis[index[to]]))

            if not bc.mirror_axis[index[to]]:
                bc.mirror_axis_flip[index[to]] = False

        for i, a in enumerate(bc.mirror_axis):
            mirror.use_axis[i] = bool(a)
            mirror.use_bisect_axis[i] = bool(a)

        for i, f in enumerate(bc.mirror_axis_flip):
            mirror.use_bisect_flip_axis[i] = bool(f)

    elif True in init_enabled:
        bc.mirror_axis_flip[index[to]] = int(not bool(bc.mirror_axis_flip[index[to]]))

        for i, f in enumerate(bc.mirror_axis_flip):
            mirror.use_bisect_flip_axis[i] = bool(f)

    enabled = tuple(a for a in mirror.use_axis)

    if to and True not in enabled:
        bc.shape.modifiers.remove(mirror)
        if not flip:
            op.report({'INFO'}, 'Removed Mirror')

    elif True not in enabled:
        bc.mirror_axis[0] = True
        mirror.use_axis[0] = True
        mirror.use_bisect_axis[0] = True

        mirror.use_bisect_flip_axis[0] = bool(bc.mirror_axis_flip[0])
        op.report({'INFO'}, 'Mirrored on: X')

    elif to and not flip:
        current = ''
        for i, a in enumerate(index.keys()):
            if mirror.use_axis[i]:
                current += F'{a} | '

        op.report({'INFO'}, F'Mirrored on: {current[:-3]}')

    elif flip and True in init_enabled:
        msg = 'Bisect {}lipped on: {}'.format('Unf' if not mirror.use_bisect_flip_axis[index[to]] else 'F', to)
        op.report({'INFO'}, msg)

    context.view_layer.update()
    dimensions = list(bc.shape.dimensions)
    if not sum(dimensions):
        index = index[to] if to else 0
        if not mirror.use_bisect_flip_axis[index]:
            mirror.use_bisect_flip_axis[index] = True
            bc.mirror_axis_flip[index] = int(mirror.use_bisect_flip_axis[index])
        else:
            mirror.use_bisect_flip_axis[index] = False
            # mirror.use_axis[index] = False
            # bc.mirror_axis_flip[index] = False

        # mirror.use_bisect_flip_axis[index] = not mirror.use_bisect_flip_axis[index]
        # bc.mirror_axis_flip[index] = int(mirror.use_bisect_flip_axis[index])

    del mirror
