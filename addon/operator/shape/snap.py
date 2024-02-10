import traceback
import string

from mathutils import Vector

import bpy
from bpy.types import Operator

from .. shape.utility.shader import snap
from .... utility import method_handler, tool, addon


class BC_OT_shape_snap(Operator):
    bl_idname = 'bc.shape_snap'
    bl_label = 'Snap'
    bl_options = {'INTERNAL'}

    clearing: bool = False


    @classmethod
    def poll(cls, context):
        activetool = tool.active().idname == tool.name
        snap = addon.preference().snap.enable
        active = context.active_object
        return activetool and snap and ((active and active.type == 'MESH') or not active)


    def invoke(self, context, event):
        return method_handler(invoke,
            arguments = (self, context, event),
            identifier = 'Invoke',
            exit_method = self.exit,
            exit_arguments = (context, ))


    def modal(self, context, event):
        return method_handler(modal,
            arguments = (self, context, event),
            identifier = 'Modal',
            exit_method = self.exit,
            exit_arguments = (context, ))


    def exit(self, context):
        return method_handler(exit,
            arguments=(self, context),
            identifier='Exit')


def invoke(op, context, event):
    op.region = bpy.context.region
    op.key_events = set(string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation)

    op.snap = snap.setup(context, event)
    op.cleaning = False

    context.window_manager.modal_handler_add(op)
    return {'RUNNING_MODAL'}


def modal(op, context, event):
    preference = addon.preference()

    op.pass_through = event.type in op.key_events
    if op.pass_through or not event.ctrl or op.cleaning or context.region != op.region:
        return op.exit(context)

    op.snap.update(context, event)

    step = 0
    factor = 10 if preference.snap.increment <= 0.1 else 1
    if op.snap.grid_active and 'WHEEL' in event.type:
        increment = preference.snap.increment
        direction = event.type[5:-5]

        if round(preference.snap.increment, 2) == 0.25:
            if direction == 'UP':
                preference.snap.increment = 0.2
            else:
                preference.snap.increment = 0.3

            increment = preference.snap.increment

        if increment < 1:
            if increment >= 0.1:
                if direction == 'UP':
                    preference.snap.increment = 0.1 * (increment / 0.1) + 0.1
                elif 0.1 * (increment / 0.1) - 0.1 >= 0.1:
                    preference.snap.increment = 0.1 * (increment / 0.1) - 0.1
                else:
                    preference.snap.increment = 0.09

            else:
                if direction == 'UP':
                    preference.snap.increment = 0.01 * (increment / 0.01) + 0.01
                elif 0.01 * (increment / 0.01) - 0.01 >= 0.01:
                    preference.snap.increment = 0.01 * (increment / 0.01) - 0.01
                else:
                    preference.snap.increment = 0.01

        else:
            if direction == 'UP':
                preference.snap.increment = (increment / 1) + 1

                if preference.snap.increment > 10:
                    preference.snap.increment = 10
            else:
                if (increment / 1) - 1 >= 1:
                    preference.snap.increment = (increment / 1) - 1
                else:
                    preference.snap.increment = 0.9

        if round(preference.snap.increment, 2) == 0.11:
            preference.snap.increment = 0.2

        # preference.snap.increment = float(F'{preference.snap.increment:.2f}')
        op.report({'INFO'}, F'Grid Size: {preference.snap.increment:.2f}')

        return {'RUNNING_MODAL'}

    return {'PASS_THROUGH'}


def exit(op, context):
    bc = context.scene.bc
    pass_through = bool(op.pass_through)
    op.pass_through = False

    # op.snap.exit = True
    op.snap.remove(context)

    bc.snap.hit = False
    bc.snap.location = Vector()

    op.cleaning = True

    return {'FINISHED' if not op.snap.handler and not pass_through else 'PASS_THROUGH'}
