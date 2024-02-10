from ..... import toolbar


def change(op, context, to='NONE'):
    bc = context.scene.bc
    value = to

    bc.axis = value
