import time

import bpy
import bmesh
import gpu

from bgl import *

from gpu.types import GPUShader

from bpy.types import SpaceView3D
from mathutils import Vector

from ...... utility import method_handler, addon, shader, screen

shapes: list = []


def wire_width():
    preference = addon.preference()
    bc = bpy.context.scene.bc
    # if not hasattr(preference, 'display'):
        # return 1

    width = preference.display.wire_width * screen.dpi_factor(rounded=True, integer=True)
    if preference.display.wire_only and preference.display.thick_wire:
        width *= preference.display.wire_size_factor

    return round(width) if (not bc.shape or len(bc.shape.data.vertices) > 2) else round(width * 1.5)


class setup:
    handler = None

    exit: bool = False
    cancel: bool = False

    @staticmethod
    def geometry(batch, shader, color, xray=False):
        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)

        if not xray:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_CULL_FACE)
            glEnable(GL_BACK)

        batch.draw(shader)

        if not xray:
            glDisable(GL_CULL_FACE)
            glDisable(GL_DEPTH_TEST)

        glDisable(GL_BLEND)

    @staticmethod
    def wireframe(batch, shader, color, width, xray=False):
        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)
        glEnable(GL_LINE_SMOOTH)

        glLineWidth(width)

        if not xray:
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)

        batch.draw(shader)

        if not xray:
            glDisable(GL_DEPTH_TEST)

        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)


    def __init__(self, op):# , exit=False):
        # if not self.handler:
        self.verts = []
        self.verts_shell = []
        self.index_tri = []
        self.index_edge = []
        self.alpha = 1.0
        self.polygons = 0

        # if not exit:
        # preference = addon.preference()

        self.mode = op.mode
        # self.fade_time = preference.display.shape_fade_time_in * 0.001
        self.fade_time = 0.0

        self.time = time.perf_counter()
        self.fade = bool(self.fade_time)
        self.fade_type = 'IN'

        # bpy.ops.bc.shape_timer_redraw(time=self.time, length=self.fade_time)

        self.shaders = {
            'uniform': gpu.shader.from_builtin('3D_UNIFORM_COLOR')}
            # 'stipple': GPUShader(self.vertex_stipple, self.fragment_stipple)}

        setup = self.shader
        # setup(geometry=True, batch=True, alpha=True, color=True)
        setup(geometry=True, batch=True, color=True, operator=op)

        draw_arguments = (self.draw_handler, (op, bpy.context), 'WINDOW', 'POST_VIEW')
        self.handler = SpaceView3D.draw_handler_add(*draw_arguments)


    def shader(self, geometry=False, batch=False, alpha=False, color=False, operator=None):
        bc = bpy.context.scene.bc if geometry else None

        if bc:
            self.polygons = len(bc.shape.data.polygons)

        if geometry and bc.shape:
            self.verts, self.index_tri, self.index_edge, mesh = shader.coordinates_from_mesh(bc.shape)

            bm = bmesh.new()
            bm.from_mesh(mesh)

            self.verts_shell = []

            offset = min(bc.shape.dimensions[:-1]) * 0.001

            for vert in bm.verts:
                location = vert.co + (offset * vert.normal)
                self.verts_shell.append(bc.shape.matrix_world @ location)

            bm.free()

        if batch and self.shaders:
            uniform = self.shaders['uniform']
            verts = {'pos': self.verts}
            shell = {'pos': self.verts_shell}
            edges = self.index_edge

            self.batches = {
                'geometry': shader.batch(uniform, 'TRIS', verts, indices=self.index_tri),
                'wireframe': shader.batch(uniform, 'LINES', verts, indices=edges),
                'shell': shader.batch(uniform, 'LINES', shell, indices=edges)}
                # 'stipple': shader.batch(self.shaders['stipple'], 'LINES')}

            if bpy.context.area:
                bpy.context.area.tag_redraw()

        if alpha and self.fade_time:
            current = (time.perf_counter() - self.time) / self.fade_time

            if self.fade:
                self.alpha = 1 - current if self.fade_type == 'OUT' else current

            if self.alpha <= 0.0 and self.fade:
                self.fade = False
                self.fade_type = 'NONE'
                self.alpha = 0.0

            elif self.alpha >= 1.0 and self.fade:
                self.fade = False
                self.fade_type = 'OUT'
                self.alpha = 1.0

        if color:
            preference = addon.preference()

            self.color = Vector(getattr(preference.color, operator.mode.lower()))
            self.color[3] = self.color[3] * self.alpha

            self.negative_color = Vector(preference.color.negative)
            self.negative_color[3] = self.negative_color[3] * self.alpha

            self.wire_color = Vector(preference.color.show_shape_wire[:]) if preference.behavior.show_shape else Vector(preference.color.wire[:])
            self.wire_color[3] = self.wire_color[3] * self.alpha

        if self.exit or self.cancel:
            if not self.fade and self.fade_type == 'OUT':
                self.fade = True
                self.fade_time = addon.preference().display.shape_fade_time_out * 0.001
                self.time = time.perf_counter()

            elif self.fade and self.fade_type == 'IN' and self.exit:
                self.fade_type = 'NONE'

            # self.remove(force=self.cancel)


    def draw_handler(self, op, context):
        method_handler(self.draw,
            arguments = (op, context),
            identifier = 'Shape Shader',
            exit_method = self.remove,
            exit_arguments = (True, ))


    def draw(self, op, context):
        preference = addon.preference()
        bc = context.scene.bc
        setup = self.shader

        setup(alpha=True, color=True, operator=op)

        # color = Vector(getattr(preference.color, self.mode.lower()))
        # color[3] = color[3] * self.alpha

        # negative_color = Vector(preference.color.negative)
        # negative_color[3] = negative_color[3] * self.alpha

        # wire_color = Vector(preference.color.show_shape_wire[:]) if preference.behavior.show_shape else Vector(preference.color.wire[:])

        # wire_color[3] = wire_color[3] * self.alpha

        color = Vector(self.color)
        negative_color = Vector(self.negative_color)
        wire_color = Vector(self.wire_color)

        uniform = self.shaders['uniform']
        geometry = self.batches['geometry']
        wireframe = self.batches['wireframe']
        shell = self.batches['shell']

        if preference.display.wire_only or (bc.shape and len(bc.shape.data.vertices) < 3):
            mode_color = (color[0], color[1], color[2], wire_color[3])

            if self.polygons:
                negative_color[3] *= 0.5
                self.geometry(geometry, uniform, negative_color, xray=True)

            xray_wire_color = Vector(mode_color)
            xray_wire_color[3] *= 0.5
            self.wireframe(wireframe, uniform, xray_wire_color, wire_width(), xray=True)
            self.wireframe(shell, uniform, mode_color, wire_width())

            # self.stipple(op, context, color)

        else:

            if self.polygons or op.shape_type == 'CIRCLE':
                xray = op.shape_type == 'NGON' and op.thin
                self.geometry(geometry, uniform, negative_color, xray=True)
                self.geometry(geometry, uniform, color, xray=xray)

            xray_wire_color = Vector(wire_color)
            xray_wire_color[3] *= 0.5
            self.wireframe(wireframe, uniform, xray_wire_color, wire_width(), xray=True)
            self.wireframe(shell, uniform, wire_color, wire_width())

            # self.stipple(op, context, color)

        # if not self.exit and not self.cancel:
        #     if op:
        #         op.modified # referencing for handler remove


    def update_handler(self, op, context):
        method_handler(self.update,
            arguments = (op, context),
            identifier = 'Shape Shader Update',
            exit_method = self.remove,
            exit_arguments = (True, ))


    def update(self, op, context):
        if not self.exit and not self.cancel:
            self.mode = op.mode

            setup = self.shader
            setup(geometry=True, batch=True)


    def remove(self, force=False):
        if self.handler and (not self.fade or force):
            SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
            self.handler = None
            # self.handler = SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
            # self.__init__(None, exit=True)


    # def stipple(self, op, context, color):
    #     preference = addon.preference()
    #     bc = context.scene.bc

    #     if bc.shape and bc.shape.data and op.shape_type == 'NGON' and preference.behavior.line_box and len(bc.shape.data.vertices) < 3:
    #         self.wireframe(self.batches['stipple'], self.shaders['stipple'], color, wire_width() * 2)
