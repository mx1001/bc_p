from mathutils import Matrix
from ...... utility import view3d, addon
# from ... import shape as _shape
from .. import mesh


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
#     op.last['scale'] = (view3d.location3d_to_location2d(op.last['global_pivot']) - op.last['mouse']).length
#     op.last['axis'] = 'XYZ'


def shape(op, context, event):
    bc = context.scene.bc

    scale = ((view3d.location3d_to_location2d(op.last['global_pivot']) - op.mouse['location']).length) / op.last['scale']

    if event.type in {'X', 'Y', 'Z'}:
        if event.value == 'RELEASE':
            if event.type == op.last['axis']:
                op.last['axis'] = 'XYZ'
            else:
                op.last['axis'] = event.type

    scale_x = scale_y = scale_z = 1

    if op.last['axis'] == 'XYZ':
        scale_x = scale_y = scale_z = scale
    elif op.last['axis'] == 'X':
        scale_x = scale
    elif op.last['axis'] == 'Y':
        scale_y = scale
    elif op.last['axis'] == 'Z':
        scale_z = scale

    scale_matrix = Matrix.Scale(scale_x, 4, (1, 0, 0)) @ Matrix.Scale(scale_y, 4, (0, 1, 0)) @ Matrix.Scale(scale_z, 4, (0, 0, 1))
    op.last['revert_matrix'] = scale_matrix.inverted()

    if op.shape_type == 'NGON':

        bc.shape.location = op.last['local_pivot']
        bc.shape.matrix_world = op.last['shape'].matrix_world @ scale_matrix
        bc.shape.location = op.last['global_pivot']

    else:
        points = bc.lattice.data.points

        locked_points = op.last['lattice_data'].points

        if addon.preference().behavior.set_origin == 'MOUSE':

            bc.lattice.matrix_world = op.last['lattice'].matrix_world @ scale_matrix
            bc.shape.matrix_world = op.last['shape'].matrix_world @ scale_matrix

        else:
            for point in (0, 1, 2, 3, 4, 5, 6, 7):
                points[point].co_deform = locked_points[point].co_deform - op.last['local_pivot']

            bc.shape.location = bc.lattice.location

            for v in range((len(op.last['shape_data'].vertices))):
                bc.shape.data.vertices[v].co = op.last['shape_data'].vertices[v].co + op.last['local_pivot']

            bc.lattice.matrix_world = op.last['lattice'].matrix_world @ scale_matrix
            bc.shape.matrix_world = op.last['shape'].matrix_world @ scale_matrix

            bc.shape.location = op.last['global_pivot']
            bc.lattice.location = op.last['global_pivot']
