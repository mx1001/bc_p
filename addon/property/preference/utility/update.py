import bpy

from bpy.utils import register_class, unregister_class

from ..... utility import addon
from .... panel import classes as panels
from .... import toolbar

sort_options = (
    'sort_modifiers',
    'sort_bevel',
    'sort_array',
    'sort_mirror',
    'sort_solidify',
    'sort_weighted_normal',
    'sort_simple_deform',
    'sort_triangulate',
    'sort_decimate',
    'sort_remesh',
    'sort_subsurf',
    'sort_bevel_last',
    'sort_array_last',
    'sort_mirror_last',
    'sort_solidify_last',
    'sort_weighted_normal_last',
    'sort_simple_deform_last',
    'sort_triangulate_last',
    'sort_decimate_last',
    'sort_remesh_last',
    'sort_subsurf_last')


def sync_sort(behavior, context):
    for option in sort_options:

        if addon.hops() and hasattr(addon.hops().property, option):
            addon.hops().property[option] = getattr(behavior, option)

        else:
            print(F'Unable to sync sorting options with Hard Ops; Box Cutter {option}\nUpdate Hard Ops!')

        if addon.kitops() and hasattr(addon.kitops(), option):
            addon.kitops()[option] = getattr(behavior, option)

        else:
            print(F'Unable to sync sorting options with KIT OPS; Box Cutter {option}\nUpdate KIT OPS!')


def simple_topbar(display, context):
    toggle = not display.simple_topbar
    display.topbar_pad = toggle
    display.pad_menus = toggle


def release_lock(keymap, context):
    bpy.ops.bc.release_lock('INVOKE_DEFAULT')


def tab(display, context):
    for panel in panels:
        if hasattr(panel, 'bl_category') and panel.bl_category and panel.bl_category != 'Tool':
            unregister_class(panel)
            panel.bl_category = display.tab
            register_class(panel)


def shape_type(behavior, context):
    option = toolbar.options()

    if option.shape_type != 'BOX' and behavior.line_box:
        option.shape_type = 'BOX'
