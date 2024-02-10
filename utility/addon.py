import os

import bpy

from .. utility import new_type, method_handler

name = __name__.partition('.')[0]
path = new_type(default=lambda new: os.path.abspath(os.path.join(__file__, '..', '..')))
path.icon = os.path.join(path(), 'addon', 'icons')


def preference():
    return bpy.context.preferences.addons[name].preferences


def hops():
    wm = bpy.context.window_manager

    if hasattr(wm, 'Hard_Ops_folder_name'):
        return bpy.context.preferences.addons[wm.Hard_Ops_folder_name].preferences

    return False


def bc():
    wm = bpy.context.window_manager

    if hasattr(wm, 'bc'):
        return bpy.context.preferences.addons[wm.bc.addon].preferences

    return False


def kitops():
    wm = bpy.context.window_manager

    if hasattr(wm, 'kitops'):
        return bpy.context.preferences.addons[wm.kitops.addon].preferences

    return False
