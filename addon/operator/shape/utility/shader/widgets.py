import time

import bpy

from bpy.types import SpaceView3D

# import bmesh
import gpu

from bgl import *
# from gpu_extras.batch import batch_for_shader

from math import pi, cos, sin
from mathutils import Vector

from ...... utility import new_type, method_handler, addon, math, screen, shader, view3d

widgets: list = []


def dot_size():
    return addon.preference().display.dot_size * screen.dpi_factor()


def wire_width():
    return screen.dpi_factor(rounded=True, integer=True)


def highlight_distance():
    size = dot_size()
    factor = addon.preference().display.dot_factor

    return size * factor


#TODO: refocus as main gizmo shader, including dots as a 'gizmo group'
class setup:
    handler = None

    exit: bool = False
    cancel: bool = False

    @staticmethod
    def dot(batch, shader, color):
        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)

        batch.draw(shader)

        glDisable(GL_BLEND)

    @staticmethod
    def outline(batch, shader, color, width=1):
        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)

        glLineWidth(width)
        batch.draw(shader)

        glDisable(GL_BLEND)
        glDisable(GL_LINE_SMOOTH)

        # glLineWidth(1)


    def __init__(self, op, exit=False):
        global widgets

        # if not self.handler:
        self.active = ''
        self.dots = []
        self.operation = 'NONE'
        self.mouse = Vector((0, 0))

        # if not exit:
        for widget in widgets:
            widget.cancel = True

        widgets = [self]

        self.dots.append(new_type(name='draw_dot', operation='DRAW'))
        self.dots.append(new_type(name='extrude_dot', operation='EXTRUDE'))
        self.dots.append(new_type(name='offset_dot', operation='OFFSET'))
        self.dots.append(new_type(name='bevel_dot', operation='BEVEL'))
        self.dots.append(new_type(name='displace_dot', operation='DISPLACE'))

        size = addon.preference().display.dot_size * 0.5 * screen.dpi_factor()

        current = time.perf_counter()
        fade_time_in = addon.preference().display.dot_fade_time_in * 0.001
        # fade_time_out = addon.preference().display.dot_fade_time_out * 0.001
        color = Vector(addon.preference().color.dot[:])
        bevel_color = Vector(addon.preference().color.dot_bevel[:])

        for dot in self.dots:
            # dot.exit = True
            # dot.enable = False
            dot.time = current
            # dot.time_out = fade_time_out
            dot.fade = False
            dot.fade_type = 'NONE'
            dot.fade_time = fade_time_in
            dot.alpha = 0.0
            dot.color = color if dot.operation != 'BEVEL' else bevel_color
            dot.size = size
            dot.vert = []
            dot.location = Vector()

        self.shaders = {'uniform2d': gpu.shader.from_builtin('2D_UNIFORM_COLOR')}
        setup = self.shader
        setup(dots=True, dots2d=True, batch=True, operator=op)

        draw_arguments = (self.draw_handler, (None, bpy.context), 'WINDOW', 'POST_PIXEL')
        self.handler = SpaceView3D.draw_handler_add(*draw_arguments)


    def shader(self, dots=False, dots2d=False, batch=False, alpha=False, operator=None):
        bc = bpy.context.scene.bc if dots or dots2d else None

        if dots and bc.shape and operator:
            self.origin = operator.origin
            self.modified = operator.modified
            self.rotated = operator.rotated
            self.scaled = operator.scaled
            self.shape_type = operator.shape_type
            self.mode = operator.mode
            self.operation = operator.operation
            self.mouse = operator.mouse['location']

            op = operator
            matrix = bc.shape.matrix_world

            thin = bc.lattice.dimensions[2] <= addon.preference().shape.offset
            front = (1, 2, 5, 6)
            back = (0, 3, 4, 7)
            left = (4, 5, 6, 7)
            right = (0, 1, 2, 3)

            for dot in self.dots:
                # dot.enable = (op.operation == 'NONE' or op.operation == dot.operation) and op.modified

                # if (dot.operation == 'DRAW' and op.shape_type == 'NGON') or hide_draw:
                #     dot.enable = False

                # elif op.mode in {'MAKE', 'JOIN'}:
                #     if dot.operation == 'EXTRUDE' and thin:
                #         dot.enable = False

                #     if dot.operation == 'OFFSET' and op.modified:
                #         dot.enable = True

                # elif dot.operation == 'OFFSET' and thin:
                #     dot.enable = False

                # elif dot.operation == 'DISPLACE' and not displace:
                #     dot.enable = False

                # elif dot.operation == 'BEVEL' and op.shape_type == 'CUSTOM':
                #     dot.enable = False

                if dot.operation in {'OFFSET', 'EXTRUDE'}:
                    indices = front if dot.operation == 'OFFSET' else back
                    points = [op.bounds[index] for index in indices]

                    dot.location = matrix @ (0.25 * math.vector_sum(points))

                elif dot.operation == 'DRAW':
                    if op.shape_type in {'BOX', 'CUSTOM'}:
                        dot.location = matrix @ op.bounds[op.draw_dot_index]

                    elif op.shape_type == 'CIRCLE':
                        indices = (5, 6) if op.draw_dot_index in {5, 6} else (1, 2)
                        points = [op.bounds[index] for index in indices]

                        dot.location = matrix @ (0.5 * math.vector_sum(points))

                elif dot.operation == 'DISPLACE':
                    indices = right if op.draw_dot_index in {5, 6} else left
                    points = [op.bounds[point] for point in indices]

                    dot.location = matrix @ (0.25 * math.vector_sum(points))

                elif dot.operation == 'BEVEL':
                    index_keys = {1: 7, 2: 4, 5: 3, 6: 0}
                    offset = 0.05
                    dot_index = op.draw_dot_index if op.draw_dot_index in index_keys.keys() else 1

                    dot.location = Vector(op.bounds[index_keys[dot_index]])
                    dot.location.x -= offset if op.draw_dot_index in {5, 6} else -offset
                    dot.location.y -= offset if op.draw_dot_index in {2, 6} else -offset

                    if not thin:
                        dot.location.z -= offset

                    dot.location = matrix @ dot.location

        if dots2d and bc.lattice:
            color = Vector(addon.preference().color.dot[:])
            bevel_color = Vector(addon.preference().color.dot_bevel[:])

            thin = bc.lattice.dimensions[2] <= addon.preference().shape.offset
            displace = len([mod for mod in bc.shape.modifiers if mod.type == 'DISPLACE'])

            #XXX: rotate and scale support
            set_origin = addon.preference().behavior.set_origin
            rotated_or_scaled = self.rotated or self.scaled
            hide_corner = rotated_or_scaled and set_origin != 'MOUSE' and self.origin == 'CORNER'
            hide_center = rotated_or_scaled and set_origin != 'CENTER' and self.origin == 'CENTER'
            hide_draw = hide_corner and hide_center

            for dot in self.dots:
                dot.enable = (self.operation == 'NONE' or self.operation == dot.operation) and self.modified

                if (dot.operation == 'DRAW' and self.shape_type == 'NGON') or hide_draw:
                    dot.enable = False

                elif self.mode in {'MAKE', 'JOIN'}:
                    if dot.operation == 'EXTRUDE' and thin:
                        dot.enable = False

                    if dot.operation == 'OFFSET' and self.modified:
                        dot.enable = True

                elif dot.operation == 'OFFSET' and thin:
                    dot.enable = False

                elif dot.operation == 'DISPLACE' and not displace:
                    dot.enable = False

                elif dot.operation == 'BEVEL' and self.shape_type == 'CUSTOM':
                    dot.enable = False

                dot.location2d = view3d.location3d_to_location2d(dot.location)

                if dot.location2d:
                    dot.highlight = math.coordinate_overlap2d(
                        # op.mouse['location'],
                        self.mouse,
                        dot.location2d,
                        size = highlight_distance())
                else:
                    dot.highlight = False
                    dot.location2d = Vector((0, 0))

                # if dot.operation == op.operation:
                if dot.operation == self.operation:
                    dot.highlight = True

            # self.active = ''
            dots = [dot for dot in self.dots if dot.enable]
            # locations = [op.mouse['location'] - dot.location2d for dot in dots]
            locations = [self.mouse - dot.location2d for dot in dots]

            closest = dots[locations.index(min(locations))] if locations else None
            self.active = closest.operation if locations and closest.highlight else ''

            for dot in self.dots:
                # if (dot != closest or not dot.highlight or not dot.enable) and op.operation != dot.operation:
                if (dot != closest or not dot.highlight or not dot.enable) and self.operation != dot.operation:
                    dot.highlight = False
                    dot.color = color if dot.operation != 'BEVEL' else bevel_color

                # elif dot.highlight or op.operation == dot.operation:
                elif dot.highlight or self.operation == dot.operation:
                    dot.color = Vector(addon.preference().color.dot_highlight[:])

        if batch:
            uniform = self.shaders['uniform2d']
            # size = self.size

            for dot in self.dots:
                if not dot.enable and not dot.fade or not dot.location2d:
                    continue

                x = dot.location2d.x
                y = dot.location2d.y
                vert, loop_index, edge_vert, edge_index = shader.circle_coordinates(x, y,
                    size=dot.size)

                if vert != dot.vert:
                    dot.vert = vert
                    verts = {'pos': vert}
                    edge_verts = {'pos': edge_vert}
                    dot.batch = shader.batch(uniform, 'TRIS', verts, indices=loop_index)
                    dot.outline = shader.batch(uniform, 'LINES', edge_verts, indices=edge_index)

            if bpy.context.area:
                bpy.context.area.tag_redraw()

        if alpha:
            current = time.perf_counter()
            for dot in self.dots:
                if not dot.enable and not dot.fade and dot.alpha == 0.0:
                    continue

                if dot.fade:
                    normalized = (current - dot.time) / dot.fade_time
                    dot.alpha = 1.0 - normalized if dot.fade_type == 'OUT' else normalized

                if dot.alpha <= 0.0 and dot.fade:
                    dot.fade = False
                    dot.fade_type = 'NONE'
                    dot.alpha = 0.0

                elif dot.alpha >= 1.0 and dot.fade:
                    dot.fade = False
                    dot.fade_type = 'NONE'
                    dot.alpha = 1.0

                elif dot.enable and dot.fade_type == 'NONE' and not dot.alpha:
                    dot.time = current
                    dot.fade = True
                    dot.fade_time = addon.preference().display.dot_fade_time_in * 0.001
                    dot.fade_type = 'IN'

                elif not dot.enable and dot.fade_type == 'NONE' and dot.alpha == 1.0:
                    dot.time = current
                    dot.fade = True
                    dot.fade_time = addon.preference().display.dot_fade_time_out * 0.001
                    dot.fade_type = 'OUT'

        if self.exit or self.cancel:
            fade_time = addon.preference().display.dot_fade_time_out * 0.001
            current = time.perf_counter()
            for dot in self.dots:
                if not dot.fade and dot.alpha:
                    dot.fade = True
                    dot.fade_type = 'OUT'
                    dot.fade_time = fade_time
                    dot.time = current
                # elif not dot.alpha:
                    # dot.fade

            #     elif dot.fade and dot.fade_type == 'IN' and self.exit:
            #         dot.fade_type = 'NONE'

            # self.remove(force=self.cancel)
            # if not self.fade and self.fade_type == 'OUT':
            #     self.fade = True
            #     self.fade_time = addon.preference().display.shape_fade_time_out * 0.001
            #     self.time = time.perf_counter()

            #     if self.fade_time > 0.1:
            #         bpy.ops.bc.shape_timer_redraw(time=self.time, length=self.fade_time)

            # elif self.fade and self.fade_type == 'IN' and self.exit and self.fade_time > 0.1:
            #     self.fade_type = 'NONE'

            #     fade = self.fade_time
            #     bpy.ops.bc.shape_timer_redraw(time=time.perf_counter(), length=fade - (fade * self.alpha))

            # self.remove(force=self.cancel)


    def draw_handler(self, _, context):
        method_handler(self.draw,
            arguments = (_, context),
            identifier = 'Dots Shader',
            exit_method = self.remove,
            exit_arguments = (True, ))


    def draw(self, _, context):
        setup = self.shader

        # setup(alpha=True)
        # if not self.exit and not self.cancel:
        #     if op:
        #         setup(dots=True, batch=True, alpha=True, operator=op)
        #     else:
        #         setup(alpha=True)
        # else:
        #     setup(alpha=True)
        update = not self.exit and not self.cancel
        setup(dots2d=update, batch=update, alpha=True)

        for dot in self.dots:
            if not dot.alpha:
                continue

            color = dot.color
            color[3] *= dot.alpha
            self.outline(dot.outline, self.shaders['uniform2d'], color, width=wire_width())
            self.dot(dot.batch, self.shaders['uniform2d'], color)


    def update_handler(self, op, context):
        method_handler(self.update,
            arguments = (op, context),
            identifier = 'Dots Update',
            exit_method = self.remove,
            exit_arguments = (True, ))


    def update(self, op, context):
        if not self.exit and not self.cancel:
            setup = self.shader
            setup(dots=True, operator=op)


    def remove(self, force=False):
        fade = False
        for dot in self.dots:
            if dot.fade:
                fade = True
                break

        if self.handler and (not fade or force):
            # self.handler = SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
            SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
            self.handler = None
            # self.__init__(None, exit=True)
