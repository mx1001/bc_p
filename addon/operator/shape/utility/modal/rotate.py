from math import radians, atan2, degrees
from mathutils import Matrix
from ...... utility import view3d, addon
# from ... import shape as _shape
from .. import mesh


def by_90(op, context, event, inside=False, init=False):

    bc = context.scene.bc

    if op.shape_type != 'NGON':
        if not init:
            bc.shape.data.transform(Matrix.Rotation(radians(-90 * bc.rotated_inside), 4, 'Z'))

            if bc.rotated_inside > 3:
                bc.rotated_inside = 0

            bc.rotated_inside += 1

        bc.shape.data.transform(Matrix.Rotation(radians(90 * bc.rotated_inside), 4, 'Z'))


# def invoke(op, context, event):
#     bc = context.scene.bc
#     op.last['mouse'] = op.mouse['location']
#     op.last['location'] = bc.shape.matrix_world @ bc.shape.location
#     op.last['local_pivot'] = op.ray['location'] if addon.preference().behavior.set_origin == 'MOUSE' else mesh.set_pivot(op, context)
#     op.last['global_pivot'] = op.ray['location'] if addon.preference().behavior.set_origin == 'MOUSE' else bc.shape.matrix_world @ op.last['local_pivot']
#     op.last['lattice_data'] = bc.lattice.data.copy()
#     op.last['shape_data'] = bc.shape.data.copy()
#     op.last['lattice'] = bc.lattice.copy()
#     op.last['shape'] = bc.shape.copy()


def shape(op, context, event):
    bc = context.scene.bc

    round_to = 1 if event.shift else addon.preference().snap.rotate_angle
    angle = angleround(round(angle3pt(op.mouse['location'], view3d.location3d_to_location2d(op.last['global_pivot']), op.last['mouse'])), round_to)

    if event.type in {'X', 'Y', 'Z'}:
        if event.value == 'RELEASE':
            addon.preference().shape.rotate_axis = event.type

    rotate_matrix = Matrix.Rotation(radians(-angle), 4, addon.preference().shape.rotate_axis)
    op.last['revert_matrix'] = rotate_matrix

    if op.shape_type == 'NGON':

        bc.shape.location = op.last['local_pivot']
        bc.shape.matrix_world = op.last['shape'].matrix_world @ rotate_matrix
        bc.shape.location = op.last['global_pivot']

    else:
        points = bc.lattice.data.points

        locked_points = op.last['lattice_data'].points

        if addon.preference().behavior.set_origin == 'MOUSE' or bc.shape.bc.array_circle:

            bc.lattice.matrix_world = op.last['lattice'].matrix_world @ rotate_matrix
            bc.shape.matrix_world = op.last['shape'].matrix_world @ rotate_matrix

        else:
            for point in (0, 1, 2, 3, 4, 5, 6, 7):
                points[point].co_deform = locked_points[point].co_deform - op.last['local_pivot']

            # bc.shape.location = bc.lattice.location

            for v in range((len(op.last['shape_data'].vertices))):
                bc.shape.data.vertices[v].co = op.last['shape_data'].vertices[v].co + op.last['local_pivot']

            bc.lattice.matrix_world = op.last['lattice'].matrix_world @ rotate_matrix
            bc.shape.matrix_world = op.last['shape'].matrix_world @ rotate_matrix

            bc.shape.location = op.last['global_pivot']
            bc.lattice.location = op.last['global_pivot']


def angle3pt(a, b, c):
    """Counterclockwise angle in degrees by turning from a to c around b"""
    angle = degrees(atan2(c[1] - b[1], c[0] - b[0]) - atan2(a[1] - b[1], a[0] - b[0]))
    return angle + 360 if angle < 0 else angle


def angleround(x, base=5):
    return base * round(x / base)
