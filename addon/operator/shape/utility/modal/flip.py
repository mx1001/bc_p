import bmesh

from mathutils import Matrix, Vector


def shape(op, context, event, report=True):
    bc = context.scene.bc
    bc.shape.data.transform(Matrix.Scale(-1, 4, Vector((0, 0, 1))))

    bm = bmesh.new()
    bm.from_mesh(bc.shape.data)

    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(bc.shape.data)
    bm.free()

    if report:
        op.report({'INFO'}, 'Flipped Shape on Z')
