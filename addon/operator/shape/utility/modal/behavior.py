from ..... import toolbar


def change(op, context, to='DESTRUCTIVE'):
    value = to

    op.behavior = value
    toolbar.change_prop(context, 'behavior', value)
