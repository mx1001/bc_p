from .. import mesh, lattice


def shape(op, context, event, extrude_only=False):
    if op.shape_type == 'NGON':
        mesh.extrude(op, context, event, extrude_only=extrude_only)

    lattice.extrude(op, context, event)
