# from ... import shape as _shape
from .. import lattice, mesh


def shape(op, context, event, index=-1):
    bc = context.scene.bc

    within_x = op.mouse['location'].x < op.init_mouse.x + 1 and op.mouse['location'].x > op.init_mouse.x - 1
    within_y = op.mouse['location'].y < op.init_mouse.y + 1 and op.mouse['location'].y > op.init_mouse.y - 1

    if not within_x and not within_y:
        if op.shape_type != 'NGON':
            lattice.draw(op, context, event)
        else:
            mesh.draw(op, context, event, index=index)

    points = bc.lattice.data.points
    location_z = None
    for point in lattice.back:
        if not location_z:
            location_z = points[point].co_deform.z
        points[point].co_deform.z = location_z if location_z < -lattice.thickness_clamp(context) else -lattice.thickness_clamp(context)
