import bpy

from math import radians
from mathutils import Vector, Matrix

from . import refresh

from ..... import toolbar
from ...... utility import addon, object, ray, view3d, math


def custom(op, context, event, axis=None):
    preference = addon.preference()
    bc = context.scene.bc

    size = context.space_data.clip_end * 10

    verts = [Vector(( size,  size, 0.0)), Vector((-size,  size, 0.0)),
             Vector((-size, -size, 0.0)), Vector(( size, -size, 0.0))]

    edges = [(0, 1), (1, 2),
             (2, 3), (3, 0)]

    faces = [(0, 1, 2, 3)]

    data = bpy.data.meshes.new(name='Box')
    data.bc.removeable = True

    if not bc.snap.hit:
        data.from_pydata(verts, edges, faces)

    box = bpy.data.objects.new(name='Box', object_data=data if not bc.snap.hit else bc.snap.mesh)
    bpy.context.scene.collection.objects.link(box)

    if not axis:
        axis = preference.axis

    current = {
        'X': 'Y',
        'Y': 'X',
        'Z': 'Z'}

    rotation = Matrix.Rotation(radians(-90 if axis in {'X', 'Y'} else 90), 4, current[axis])

    cursor = context.scene.cursor.rotation_euler.to_matrix().to_4x4()
    cursor.translation = context.scene.cursor.location

    matrix = cursor @ rotation if preference.surface == 'CURSOR' else rotation

    if not bc.snap.hit:
        box.data.transform(matrix)

    if bc.snap.hit:
        # hit, op.ray['location'], op.ray['normal'], _ = ray.cast(*op.mouse['location'], mesh_data=bc.snap.mesh)
        op.ray['location'] = Vector(bc.snap.location[:])
        op.ray['normal'] = Vector(bc.snap.normal[:])

    else:
        hit, op.ray['location'], op.ray['normal'], _ = ray.cast(*op.mouse['location'], obj=box)

    if not bc.snap.hit:
        if not hit:
            index = [axis == a for a in 'XYZ'].index(True)

            if index > 1:
                index = 0
            else:
                index += 1

            axis = 'XYZ'[index]

            bpy.data.objects.remove(box)

            del box

            op.plane_checks += 1

            if op.plane_checks < 4:
                custom(op, context, event, axis=axis)
            return

    bc.lattice.matrix_world = matrix
    bc.lattice.matrix_world.translation = Vector(op.ray['location'][:] if not bc.snap.hit else bc.snap.location)
    bc.shape.matrix_world = bc.lattice.matrix_world
    bc.plane.matrix_world = bc.lattice.matrix_world

    op.start['matrix'] = bc.plane.matrix_world.copy()

    bc.location = op.ray['location'] if not bc.snap.hit else bc.snap.location

    bpy.data.objects.remove(box)

    del box

    refresh.shape(op, context, event)


def screen(op, context, event):
    bc = context.scene.bc
    size = context.space_data.clip_end
    view_rotation = context.region_data.view_rotation
    view_location = context.region_data.view_location
    view_matrix = view_rotation.to_matrix().to_4x4()

    if not bc.snap.hit:
        verts = [Vector((-size, -size, 0.0)), Vector(( size, -size, 0.0)),
                Vector((-size,  size, 0.0)), Vector(( size,  size, 0.0))]

        edges = [(0, 2), (0, 1),
                (1, 3), (2, 3)]

        faces = [(0, 1, 3, 2)]

        data = bpy.data.meshes.new(name='Box')
        data.bc.removeable = True

        data.from_pydata(verts, edges, faces)
        plane = bpy.data.objects.new(name='Box', object_data=data)
        bpy.context.scene.collection.objects.link(plane)

        del data

        plane.data.bc.removeable = True if not bc.snap.hit else False

        plane.data.transform(Matrix.Translation(Vector((0, 0, max(op.datablock['dimensions'])))))
        plane.data.transform(view_matrix)

        center = math.coordinates_center(op.datablock['bounds'])
        plane.data.transform(Matrix.Translation(center))

        _, op.ray['location'], op.ray['normal'], _ = ray.cast(*op.mouse['location'], mesh_data=plane.data)

        bpy.data.objects.remove(plane)
        del plane

        bc.lattice.matrix_world = view_matrix
        bc.lattice.matrix_world.translation = Vector(op.ray['location'][:])
        bc.shape.matrix_world = bc.lattice.matrix_world
        bc.plane.matrix_world = bc.lattice.matrix_world

    else:
        intersect = view3d.intersect_plane(*op.mouse['location'], view_location, view_matrix)
        bc.lattice.matrix_world = view_matrix
        bc.lattice.matrix_world.translation = intersect
        bc.shape.matrix_world = bc.lattice.matrix_world
        bc.plane.matrix_world = bc.lattice.matrix_world

    op.start['matrix'] = bc.plane.matrix_world.copy()

    bc.location = op.ray['location'] if not bc.snap.hit else view_location
    refresh.shape(op, context, event)


# TODO: consider parent matrix
def surface(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc

    obj = context.active_object

    matrix = obj.matrix_world if obj else Matrix()
    # TODO: needs to pick obj ray trace target for matrix
    if op.active_only: # XXX: add different prop controller for this?
        if len(op.datablock['targets']) == 2:
            for o in op.datablock['targets']:
                if o != context.active_object:
                    obj = o
                    matrix = obj.matrix_world

    if bc.snap.hit:
        matrix = Matrix()
    ray_normal = op.ray['normal'] if not bc.snap.hit else Vector(bc.snap.normal[:])
    # normal = obj.matrix_world.inverted().to_3x3() @ ray_normal
    normal = matrix.inverted().to_3x3() @ ray_normal
    track_quat = normal.to_track_quat('Z', 'Y')
    track_mat = track_quat.to_matrix().to_4x4()
    track_mat.translation = bc.plane.data.polygons[0].center

    # XXX: doesnt work for rotated objects properly
    ray_location = op.ray['location'] if not bc.snap.hit else bc.snap.location
    bc.lattice.matrix_world = matrix @ track_mat
    bc.lattice.matrix_world.translation = Vector(ray_location[:])
    bc.shape.matrix_world = bc.lattice.matrix_world
    bc.plane.matrix_world = bc.lattice.matrix_world

    del obj

    op.start['matrix'] = bc.plane.matrix_world.copy()

    bc.location = ray_location
    refresh.shape(op, context, event)
