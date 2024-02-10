from ..... import toolbar
from . import refresh


def change(op, context, event, to='CORNER'):
    value = to

    op.origin = value
    toolbar.change_prop(context, 'origin', value)

    refresh.shape(op, context, event)
