import traceback
import string

import bpy
import bmesh

from random import random
from math import pi, radians, cos, sin
from mathutils import Vector, Matrix

# from ... shape import draw
from ...... utility import method_handler, tool, addon, screen, math, view3d, ray, modifier

import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader


def grid(x, y, z, matrix, size, span):
    offset = size * span * 0.5
    span_count = lambda count: size * (span - count)
    coord = lambda pos, count: (pos - offset) + span_count(count)
    unit = lambda xspan, yspan: plane(coord(x, xspan), coord(y, yspan), z, matrix, size)
    return ((unit(xspan, yspan) for xspan in range(span)) for yspan in range(span))


def plane(x, y, z, matrix, size):
    coord = lambda pos: matrix @ Vector(pos)

    verts = (
        coord((x, y, z)),
        coord((x + size, y, z)),
        coord((x, y + size, z)),
        coord((x + size, y + size, z)))

    index = (
        (0, 1, 3),
        (0, 3, 2))

    edge_index = (
        (0, 2), (0, 1),
        (1, 3), (2, 3))

    center = Vector((x, y, z))

    return verts, index, edge_index, center


def circle(x, y, size=6.0, segments=16):
    size = size * 0.5
    factor = 1 / segments

    verts = [(x, y)]
    verts += [(x + cos(i * pi * 2 * factor) * size, y + sin(i * pi * 2 * factor) * size) for i in range(segments)]
    index = [(0, i + 1, i + 2 if i + 2 < segments else 1) for i in range(segments - 1)]

    edges = verts[1:]
    edges.append(edges[0])
    edge_index = [(i, i + 1) if i < segments else (0, segments) for i in range(segments)]

    return verts, edges, index, edge_index


class setup:
    units: dict = {}
    points: dict = {}
    exit: bool = False


    @staticmethod
    def snap_mesh(context, objects):
        if not objects:
            return

        bc = context.scene.bc

        bm = bmesh.new(use_operators=False)
        new_data = []

        max_dimension = lambda obj: max(obj.dimensions[:])
        copies = [obj.copy() for obj in objects if max_dimension(obj)]

        for copy in copies:
            context.scene.collection.objects.link(copy)

        for copy in copies:
            max_dimension = max(copy.dimensions[:])
            for mod in copy.modifiers:
                if mod.type != 'BEVEL':
                    continue

                segment_limit = mod.segments > 1 and mod.width < max_dimension * 0.1
                chamfer_limit = mod.segments == 1 and mod.width < max_dimension * 0.05
                if segment_limit or chamfer_limit:
                    copy.modifiers.remove(mod)

        context.view_layer.update()

        for copy in copies:
            evaluated = copy.evaluated_get(context.evaluated_depsgraph_get())

            new = bpy.data.meshes.new_from_object(evaluated)
            new.transform(copy.matrix_world)

            bm.from_mesh(new)
            new_data.append(new)

        bc.snap.mesh = bpy.data.meshes.new(name='snap_mesh')
        bm.to_mesh(bc.snap.mesh)
        bm.free()

        for mesh in new_data:
            bpy.data.meshes.remove(mesh)

        del new_data

        for copy in copies:
            bpy.data.objects.remove(copy)


    def __init__(self, context, event):
        method_handler(self._init,
            arguments = (context, event),
            identifier = 'Snap Init',
            exit_method = self.remove,
            exit_arguments=(context, ),
            return_result = False)


    def _init(self, context, event):
        preference = addon.preference()
        bc = context.scene.bc

        self.time_in = preference.display.grid_fade_time_in * 0.001
        self.time_out = preference.display.grid_fade_time_out * 0.001

        self.grid_size = preference.snap.increment
        self.grid_units = preference.snap.grid_units
        self.grid_active = False
        self.face_index = -1
        self.last_index = -1
        self.nearest_unit = Vector()
        self.last_unit = Vector()
        self.handler = None

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        hit, location, normal, _, _, _ = ray.cast(*self.mouse, selected=True)

        active = context.active_object
        selected = context.selected_objects

        if not hit and selected:
            return

        if active:
            self.matrix = active.matrix_world.copy()

            if hit:
                self.snap_mesh(context, selected)

        axis = {
            'X': 'Y',
            'Y': 'X',
            'Z': 'Z'}
        angle = radians(-90 if preference.axis in {'X', 'Y'} else 90)

        if preference.surface == 'OBJECT' and bc.snap.mesh:
            self.type = 'OBJECT'

            if hit:
                hit, location, normal, face_index = ray.cast(*self.mouse, mesh_data=bc.snap.mesh)

                self.location = location
                self.normal = normal
                self.face_index = face_index

                self.matrix = view3d.track_matrix(self.normal, Vector(), Matrix())
            else:
                self.location = Vector()
                self.normal = Vector()
                self.face_index = 0

                self.matrix = Matrix()

            # track = (self.normal, Vector(), Matrix())
            # self.matrix = view3d.track_matrix(*track)

        elif preference.surface == 'VIEW' or (preference.surface == 'OBJECT' and not hit and active and selected):
            self.type = 'VIEW'

            matrix = context.region_data.view_rotation.to_matrix().to_4x4()
            self.normal = Vector((0, 0, -1))
            self.location = context.region_data.view_location
            self.matrix = matrix

        elif preference.surface == 'CURSOR':
            self.type = 'CURSOR'

            cursor = context.scene.cursor
            matrix = cursor.rotation_euler.to_matrix().to_4x4()
            # matrix.translation = cursor.location

            rotation = Matrix.Rotation(angle, 4, axis[preference.axis])
            matrix @= rotation

            # self.normal = matrix @ Vector((0, 0, -1))
            # self.location = matrix.translation
            self.normal = Vector((0, 0, -1))
            self.location = cursor.location
            self.matrix = matrix

        elif preference.surface == 'WORLD' or (preference.surface == 'OBJECT' and not selected):
            self.type = 'WORLD'

            matrix = Matrix.Rotation(angle, 4, axis[preference.axis])

            self.normal = matrix @ Vector((0, 0, -1))
            self.location = matrix.translation
            self.matrix = matrix

        # track = (self.normal, Vector(), Matrix())
        # self.matrix = view3d.track_matrix(*track)

        if preference.snap.grid or self.type in {'VIEW', 'CURSOR', 'WORLD'}:
            self.grid_active = True
            intersect = (*self.mouse, self.location, self.matrix)
            self.intersect = view3d.intersect_plane(*intersect)

            increment = (*self.intersect[:-1], preference.snap.increment)
            increment_round = (*math.increment_round_2d(*increment), self.intersect[2])
            self.nearest_unit = Vector(increment_round)

            self.update_grid(context)

        self.update_points(context)

        self.last_unit = self.nearest_unit
        self.last_index = self.face_index

        handler = (self.shader, (context, ), 'WINDOW', 'POST_PIXEL')
        self.handler = bpy.types.SpaceView3D.draw_handler_add(*handler)


    def check_mouse_over(self, location, return_distance=False):
        preference = addon.preference()

        dot_size = preference.display.snap_dot_size * screen.dpi_factor()
        dot_factor = preference.display.snap_dot_factor
        limit = dot_size * dot_factor

        distance = (self.mouse - location).length

        if not return_distance:
            return distance < limit
        else:
            return distance


    def shader(self, context):
        method_handler(self._shader,
            arguments=(context, ),
            identifier = 'Shader',
            exit_method = self.remove,
            exit_arguments=(context, ),
            return_result = False)


    def _shader(self, context):
        if self.grid_active:
            self.update_grid(context)

        self.update_points(context)

        self.last_unit = self.nearest_unit
        self.last_index = self.face_index

        # if self.exit or self.type == 'VIEW':
        #     self.remove(context)

        #     if context.area:
        #         context.area.tag_redraw()


    def update(self, context, event):
        method_handler(self._update,
            arguments = (context, event),
            identifier = 'Snap Update',
            exit_method = self.remove,
            exit_arguments=(context, ),
            return_result = False)


    def _update(self, context, event):
        preference = addon.preference()
        bc = context.scene.bc

        if not self.handler:
            return

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        if bc.snap.mesh and ((preference.snap.grid_off_face or preference.snap.grid_units == 0) or not preference.snap.grid):
            hit, location, normal, face_index = ray.cast(*self.mouse, mesh_data=bc.snap.mesh)

            if face_index != self.face_index and hit:
                self.location = location
                self.normal = normal
                self.face_index = face_index

                track = (self.normal, Vector(), Matrix())
                self.matrix = view3d.track_matrix(*track)

        # track = (self.normal, Vector(), Matrix())
        # self.matrix = view3d.track_matrix(*track)

        if self.grid_active:
            intersect = (*self.mouse, self.location, self.matrix)
            self.intersect = view3d.intersect_plane(*intersect)

            increment_round = (*self.intersect[:-1], preference.snap.increment)
            self.nearest_unit = Vector((*math.increment_round_2d(*increment_round), self.intersect[2]))

        if context.area:
            context.area.tag_redraw()


    def update_grid(self, context):
        preference = addon.preference()
        bc = context.scene.bc

        # if self.type == 'VIEW':
        #     return

        if self.grid_size != preference.snap.increment:
            self.grid_size = preference.snap.increment
            for key in list(self.units.keys()):
                self.units[key].remove()

                del self.units[key]

            for key in list(self.points.keys()):
                self.points[key].remove()

                del self.points[key]

            intersect = (*self.mouse, self.location, self.matrix)
            self.intersect = view3d.intersect_plane(*intersect)

            increment = (*self.intersect[:-1], preference.snap.increment)
            increment_round = (*math.increment_round_2d(*increment), self.intersect[2])
            self.nearest_unit = Vector(increment_round)

        if self.face_index != self.last_index:
            for key in list(self.units.keys()):
                self.units[key].remove()

        for key in list(self.units.keys()):
            if not self.units[key].handler:
                del self.units[key]

        if self.nearest_unit != self.last_unit or not self.units:
            grid_units = self.grid_units if preference.snap.grid else 4
            for span in grid(*self.nearest_unit, self.matrix, self.grid_size, grid_units):
                for unit in span:
                    location = unit[3]
                    increment_round = (*location[:-1], self.grid_size)
                    center = Vector((*math.increment_round_2d(*increment_round), location.z))
                    key = str(center[:-1])

                    if key not in self.units:
                        verts = unit[0]
                        index = unit[1]
                        edge_index = unit[2]

                        args = (context, verts, index, edge_index, center, self.time_in)
                        self.units[key] = grid_unit(*args)

        for key in list(self.units.keys()):
            unit = self.units[key]
            distance = (unit.center - self.nearest_unit).length

            if distance > self.grid_size * self.grid_units:
                unit.remove()
                if not self.units[key].handler:
                    del self.units[key]

        for key in self.units:
            unit = self.units[key]
            unit.type = self.type

            distance = (unit.center - self.nearest_unit).length
            normalized = distance / ((self.grid_size * self.grid_units) * 0.5)

            if normalized > 1.0:
                normalized = 1.0

            unit.alpha = 1.0 - normalized if bc.snap.display and preference.snap.grid else 0.0


    def update_points(self, context):
        preference = addon.preference()
        bc = context.scene.bc

        if self.type == 'VIEW':
            return

        if bc.snap.mesh:
            face = bc.snap.mesh.polygons[self.face_index]
            if self.face_index != self.last_index:
                self.remove_external('points')

                if preference.snap.verts:
                    for index in face.vertices:
                        vert = bc.snap.mesh.vertices[index]

                        if str(vert.co) not in self.points:
                            self.points[str(vert.co)] = point(view3d.location3d_to_location2d(vert.co), vert.co)
                        else:
                            self.points[str(vert.co)].remove()
                            self.points[str(vert.co) + F'{random()}-r'] = self.points[str(vert.co)]
                            self.points[str(vert.co)] = point(view3d.location3d_to_location2d(vert.co), vert.co)

                if preference.snap.edges:
                    for indices in face.edge_keys:
                        vert1 = bc.snap.mesh.vertices[indices[0]]
                        vert2 = bc.snap.mesh.vertices[indices[1]]

                        center = (vert1.co + vert2.co) * 0.5

                        if str(center) not in self.points:
                            self.points[str(center)] = point(view3d.location3d_to_location2d(center), center)
                        else:
                            self.points[str(center)].remove()
                            self.points[str(center) + F'{random()}-r'] = self.points[str(center)]
                            self.points[str(center)] = point(view3d.location3d_to_location2d(center), center)

                if preference.snap.faces:
                    if str(face.center) not in self.points:
                        self.points[str(face.center)] = point(view3d.location3d_to_location2d(face.center), face.center)
                    else:
                        self.points[str(face.center)].remove()
                        self.points[str(face.center) + F'{random()}-r'] = self.points[str(face.center)]
                        self.points[str(face.center)] = point(view3d.location3d_to_location2d(face.center), face.center)

        if self.grid_active:
            if self.nearest_unit != self.last_unit:
                if str(self.last_unit) in self.points:
                    self.points[str(self.last_unit)].remove()
                    self.points[str(self.last_unit) + F'{random()-1}'] = self.points[str(self.last_unit)]
                    del self.points[str(self.last_unit)]

                if str(self.nearest_unit) not in self.points and not context.scene.bc.shape:
                    self.points[str(self.nearest_unit)] = point(view3d.location3d_to_location2d(self.matrix @ self.nearest_unit), self.matrix @ self.nearest_unit)

        for key in list(self.points.keys()):
            current = self.points[key]
            if not current.handler:
                del self.points[key]

                continue

            intersect = view3d.location2d_to_intersect3d(*self.mouse, self.location, self.normal)
            location = view3d.location2d_to_intersect3d(*current.location, self.location, self.normal)
            distance = (intersect - location).length

            fade_distance = preference.snap.fade_distance * 2
            normalized = 1.0 - distance / fade_distance

            if normalized < 0:
                normalized = 0

            current.alpha = normalized if bc.snap.display else 0.0

        mouse_over = []
        positions = []
        for key in self.points:
            current = self.points[key]

            if self.check_mouse_over(current.location):
                mouse_over.append(current)
                positions.append(self.check_mouse_over(current.location, return_distance=True))
            else:
                current.highlight = False

        if positions:
            smallest = min([pos for pos in positions])
            for index, pt in enumerate(mouse_over):
                if index == positions.index(smallest):
                    pt.highlight = True
                    bc.snap.hit = False if self.type == 'VIEW' else True #an execption for view cuz math dowstream doesn't do it
                    bc.snap.location = pt.location3d
                    bc.snap.normal = self.normal
                else:
                    pt.highlight = False
        else:
            bc.snap.hit = False
            bc.snap.location = Vector()


    def remove(self, context):
        method_handler(self._remove,
            arguments=(context, ),
            identifier = 'Snap Remove',
            return_result = False)


    def _remove(self, context):
        self.exit = True
        bc = context.scene.bc

        if bc.snap.mesh:
            bpy.data.meshes.remove(bc.snap.mesh)

        self.remove_external('units')
        for key in list(self.units.keys()):
            if not self.units[key].handler:
                del self.units[key]

        self.remove_external('points')
        for key in list(self.points.keys()):
            if not self.points[key].handler:
                del self.points[key]

        if self.handler and not self.points and not self.units:
            self.handler = bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')


    def remove_external(self, type):
        types = getattr(self, type)
        for key in types:
            types[key].remove()


class point:
    alpha: float = 0.0
    highlight: bool = False


    def __init__(self, location, location3d=None):
        preference = addon.preference()

        self.location = location
        self.location3d = location3d
        self.verts, self.edges, self.index, self.edge_index  = circle(*self.location,
            size = preference.display.snap_dot_size * screen.dpi_factor())

        self.highlight = False
        self.width = 1 * screen.dpi_factor(rounded=True, integer=True)
        self.alpha = 1.0
        self.color = Vector(preference.color.snap_point[:])
        self.color[-1] = self.color[-1] * self.alpha

        handler = (self.shader, tuple(), 'WINDOW', 'POST_PIXEL')
        self.handler = bpy.types.SpaceView3D.draw_handler_add(*handler)


    def shader(self):
        method_handler(self._shader,
        identifier = 'Shader',
        exit_method = self.remove,
        return_result = False)


    def _shader(self):
        preference = addon.preference()

        if self.highlight:
            self.color = Vector(preference.color.snap_point_highlight[:])
        else:
            self.color = Vector(preference.color.snap_point[:])
        self.color[-1] = self.color[-1] * self.alpha

        self.geometry(self.color)
        self.wire(self.color, self.width)


    def geometry(self, color):
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': self.verts}, indices=self.index)

        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)
        glDepthFunc(GL_ALWAYS)

        batch.draw(shader)

        glDisable(GL_BLEND)


    def wire(self, color, width):
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': self.edges}, indices=self.edge_index)

        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)

        glDepthFunc(GL_ALWAYS)

        glLineWidth(width)

        batch.draw(shader)

        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)


    def remove(self):
        if self.handler:
            self.handler = bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')


class grid_unit:
    alpha: float = 0.0


    def __init__(self, context, verts, index, edge_index, center, time_in):
        self.verts = verts
        self.index = index
        self.edge_index = edge_index
        self.center = center
        self.alpha = 0.0

        self.tool = tool.active().operator_properties('bc.shape_draw')

        handler = (self.shader, tuple(), 'WINDOW', 'POST_VIEW')
        self.handler = bpy.types.SpaceView3D.draw_handler_add(*handler)


    def shader(self):
        method_handler(self._shader,
            identifier = 'Grid Unit Geometry',
            exit_method = self.remove,
            return_result = False)


    def _shader(self):
        preference = addon.preference()

        # self.color = Vector(getattr(preference.color, draw.prop.mode.lower()))
        color = Vector(getattr(preference.color, self.tool.mode.lower())) if preference.color.grid_use_mode else Vector(preference.color.grid[:])
        if self.type == 'WORLD' and not bpy.context.selected_objects[:]:
            color = Vector(getattr(preference.color, 'make'))

        color[3] = color[3] * self.alpha

        wire_color = Vector(preference.color.grid_wire[:])
        wire_color[3] = (wire_color[3] * 0.5) * self.alpha
        width = preference.display.wire_width * screen.dpi_factor(rounded=True, integer=True)

        self.geometry(color)
        self.wire(wire_color, width)


    def geometry(self, color):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': self.verts}, indices=self.index)

        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)

        batch.draw(shader)

        glDisable(GL_BLEND)


    def wire(self, color, width):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': self.verts}, indices=self.edge_index)

        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)

        glLineWidth(width)

        batch.draw(shader)

        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)


    def remove(self):
        if self.handler:
            self.handler = bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
