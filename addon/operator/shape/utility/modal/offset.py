# from ..... import toolbar
# from ... import shape as _shape
from .. import mesh, lattice


def shape(op, context, event):
    ngon = op.shape_type == 'NGON'

    if op.shape_type == 'NGON':
        if not op.extruded:
            mesh.extrude(op, context, event)

    if not ngon:
        lattice.offset(op, context, event)
    else:
        mesh.offset(op, context, event)
