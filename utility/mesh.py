from statistics import median
from mathutils import Matrix, Vector


def longest_edge_median(face, verts):
    center = Vector()
    max_length = 0.0
    for current in face.vertices:
        for check in face.vertices:
            if check == current:
                continue

            length = (verts[current].co - verts[check].co).length

            if length < max_length:
                continue

            current_mid = median((verts[current].co, verts[check].co))

            max_length = length
            center = current_mid

    return center


def transform_scale(mesh, x=0.0, y=0.0, z=0.0, uniform=0.0, magnitude=1):
    if x: mesh.transform(Matrix.Scale(x, 4, Vector((magnitude, 0, 0)) ))
    if y: mesh.transform(Matrix.Scale(y, 4, Vector((0, magnitude, 0)) ))
    if z: mesh.transform(Matrix.Scale(z, 4, Vector((0, 0, magnitude)) ))

    if uniform:
        mesh.transform(Matrix.Scale(uniform, 4, Vector((magnitude, 0, 0)) ))
        mesh.transform(Matrix.Scale(uniform, 4, Vector((0, magnitude, 0)) ))
        mesh.transform(Matrix.Scale(uniform, 4, Vector((0, 0, magnitude)) ))
