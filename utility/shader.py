import bpy

from math import pi, cos, sin
from mathutils import Matrix

import gpu
from gpu.types import GPUBatch, GPUIndexBuf, GPUVertBuf


def batch(shader, type, property={}, vbo_index=0, indices=[]):
    vbo = None
    vbo_length = 0
    ibo = None

    if property:
        vbo_length = len(list(property.values())[vbo_index])

    vbo = GPUVertBuf(shader.format_calc(), vbo_length)

    if property:
        for prop, data in property.items():
            vbo.attr_fill(prop, data)

    if indices:
        ibo = GPUIndexBuf(type=type, seq=indices)
        return GPUBatch(type=type, buf=vbo, elem=ibo)

    return GPUBatch(type=type, buf=vbo)


def coordinates_from_mesh(obj, evaluated=True):
    mesh = obj.data
    matrix = obj.matrix_world

    if evaluated:
        mesh = (obj.evaluated_get(bpy.context.evaluated_depsgraph_get())).to_mesh()
        obj.to_mesh_clear()

    mesh.update()
    mesh.calc_loop_triangles()

    vert = [matrix @ vert.co for vert in mesh.vertices[:]]
    loop_index = tuple([loop.vertices[:] for loop in mesh.loop_triangles[:]])
    edge_index = tuple(mesh.edge_keys[:])

    return vert, loop_index, edge_index, mesh


def circle_coordinates(x, y, size=10, resolution=32):
    step = lambda i: i * pi * 2 * (1 / resolution)

    vert = [(x + cos(step(i)) * size, y + sin(step(i)) * size) for i in range(resolution)]
    vert.insert(0, (x, y))

    loop_index = [(0, i + 1, i + 2 if i + 2 < resolution else 1)
                   for i in range(resolution - 1)]

    edge_vert = vert[1:]
    edge_vert.append(edge_vert[-1])

    edge_index = [(i if i < resolution else 0, i + 1 if i < resolution else resolution) for i in range(resolution + 1)]

    return vert, loop_index, edge_vert, edge_index
