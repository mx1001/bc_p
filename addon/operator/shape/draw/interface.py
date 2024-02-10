import bpy
from bpy.types import Operator, SpaceView3D
from bpy.props import BoolProperty

from .. utility import shader, statusbar
from .. utility import tracked_events, tracked_states
from ..... utility import addon


class BC_OT_draw_interface(Operator):
    bl_idname = 'bc.draw_interface'
    bl_label = 'Draw Interface'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'INTERNAL'}


    def execute(self, context):
        preference = addon.preference()

        self.timer = None
        self.use_widgets = True

        self.update_states()

        self.shader = shader.shape.setup(self)
        self.widgets = shader.widgets.setup(self)
        tracked_states.widgets = self.widgets

        if not preference.display.dots:
            self.widgets.exit = True

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        # bc = context.scene.bc
        # if not self.shader.handler and not self.widgets.handler:

        # if not self.shader.handler:
        #     tracked_states.widgets = None

        #     if not tracked_states.running:
        #         self.clear_states()

        #     if self.timer:
        #         context.window_manager.event_timer_remove(self.timer)
        #         self.timer = None

        #     return {'FINISHED'}

        # elif not tracked_states.running and self.shader.handler:
        #     self.clear_states()

        #     if not self.cancelled:
        #         SpaceView3D.draw_handler_remove(self.shader.handler, 'WINDOW')
        #         # self.shader.exit = True
        #         # self.widgets.exit = True
        #     else:
        #         SpaceView3D.draw_handler_remove(self.shader.handler, 'WINDOW')
        #         # self.shader.cancel = True
        #         # self.widgets.cancel = True

        #         # return {'CANCELLED'}

        #     if not self.timer:
        #         self.timer = context.window_manager.event_timer_add(0.05, window=context.window)

        # elif tracked_states.running and not self.shader.exit and not self.shader.cancel:
        #     self.update_states()

        #     self.shader.update_handler(self, context)
            # self.widgets.update_handler(self, context)

        preference = addon.preference()
        bc = context.scene.bc

        if not self.timer:
            # self.timer = context.window_manager.event_timer_add(0.05, window=context.window)
            self.timer = context.window_manager.event_timer_add(1 / preference.display.update_fps, window=context.window)

        # if not tracked_states.running:
        if not bc.running:
            clear_states()
            if self.shader.handler:
                SpaceView3D.draw_handler_remove(self.shader.handler, 'WINDOW')
                self.shader.handler = None

            if self.widgets.handler:
                SpaceView3D.draw_handler_remove(self.widgets.handler, 'WINDOW')
                self.widgets.handler = None

            context.window_manager.event_timer_remove(self.timer)
            self.timer = None

            del self.shader
            del self.widgets

            return {'FINISHED'}

        if event.type == 'TIMER' and context.area and not self.shader.exit and not self.shader.cancel:
            context.area.tag_redraw()

            self.update_states()
            self.shader.update_handler(self, context)

            if preference.display.dots:
                if not self.widgets.handler:
                    self.widgets = shader.widgets.setup(self)
                    tracked_states.widgets = self.widgets

                self.widgets.update_handler(self, context)

            elif self.widgets.handler:
                # SpaceView3D.draw_handler_remove(self.widgets.handler, 'WINDOW')
                # self.widgets.handler = None
                self.widgets.exit = True
                tracked_states.widgets = None

                for dot in self.widgets.dots:
                    if not dot.alpha:
                        SpaceView3D.draw_handler_remove(self.widgets.handler, 'WINDOW')
                        self.widgets.handler = None
                        break

        return {'PASS_THROUGH'}


    def update_states(self):
        self.mouse = tracked_events.mouse

        self.mode = tracked_states.mode
        self.operation = tracked_states.operation
        self.shape_type = tracked_states.shape_type
        self.origin = tracked_states.origin
        self.rotated = tracked_states.rotated
        self.scaled = tracked_states.scaled
        self.cancelled = tracked_states.cancelled

        self.rmb_lock = tracked_states.rmb_lock
        self.modified = tracked_states.modified
        self.bounds = tracked_states.bounds
        self.thin = tracked_states.thin
        self.draw_dot_index = tracked_states.draw_dot_index


def clear_states():
    tracked_states.widgets = None

    tracked_states.mode = 'CUT'
    tracked_states.operation = 'NONE'
    tracked_states.shape_type = 'BOX'
    tracked_states.rotated = False
    tracked_states.scaled = False
    tracked_states.cancelled = False

    tracked_states.rmb_lock = False
    tracked_states.modified = False
    tracked_states.bounds = []
    tracked_states.thin = False
    tracked_states.draw_dot_index = 0
