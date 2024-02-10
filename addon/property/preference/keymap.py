import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty

from . utility import update
from ... operator.shape.utility import change
from ... property.utility import names


class bc(PropertyGroup):

    allow_selection: BoolProperty(
        name = names['allow_selection'],
        description = '\n Preserve mouse click for viewport selection',
        update = change.allow_selection,
        default = True)

    edit_disable_modifiers: BoolProperty(
        name = names['edit_disable_modifiers'],
        description = ('\n Disable CTRL and SHIFT key modifiers for drawing shapes in edit mode, allows path selection\n'
                       ' Note: Disables repeat shape (edit mode)'),
        default = True)

    enable_surface_toggle: BoolProperty(
        name = names['enable_surface_toggle'],
        description = '\n Toggle surface draw method from Object to Cursor with Alt-W',
        default = False)

    alt_preserve: BoolProperty(
        name = 'Preserve Alt',
        description = '\n Preserve Alt for other navigational controls during cut',
        default = False)

    rmb_preserve: BoolProperty(
        name = 'Preserve RMB',
        description = '\n Preserve RMB for other navigational controls during cut',
        default = False)

    release_lock: BoolProperty(
        name = 'Release Lock',
        description = '\n Lock the shape (Tab) after the first mouse release\n\n SHIFT or CTRL - Additional Lock Options',
        update = update.release_lock,
        default = False)

    release_lock_lazorcut: BoolProperty(
        name = 'Release Lock Lazorcut',
        description = '\n Lock the shape after performing a lazorcut',
        default = False)

    quick_execute: BoolProperty(
        name = names['quick_execute'],
        description = '\n Quickly execute cuts on release',
        default = False)

    make_active: BoolProperty(
        name = names['make_active'],
        description = '\n Make the shape active when holding shift to keep it',
        default = True)

    rmb_cancel_ngon: BoolProperty(
        name = 'RMB Cancel Ngon',
        description = '\n Cancel ngon on rmb click rather then remove points',
        default = False)

    alt_draw: BoolProperty(
        name = 'Alt Center',
        description = '\n Alt centers the cutter when held while drawing',
        default = True)

    shift_draw: BoolProperty(
        name = 'Shift Uniform',
        description = '\n Shift uniformely expands the cutter when held while drawing',
        default = True)

    scroll_adjust_circle: BoolProperty(
        name = names['scroll_adjust_circle'],
        description = '\n Scroll wheel adjusts circle vert count when drawing',
        default = False)

    enable_toolsettings: BoolProperty(
        name = 'Enable Tool Settings',
        description = '\n Enable tool settings area when activating boxcutter with the hotkey',
        default = True)

    view_pie: BoolProperty(
        name = 'View Pie',
        description = '\n Allow using the view pie with accent grave / tilde key',
        default = True)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    keymap = context.window_manager.keyconfigs.user.keymaps['3D View']
    keymap_items = keymap.keymap_items

    row = layout.row()
    row.label(text=keymap_items['bc.tool_activate'].name)

    row.prop(keymap_items['bc.tool_activate'], 'type', text='', full_event=True)
    label_row(preference.keymap, 'release_lock', layout.row(), label='Release Lock')
    label_row(preference.keymap, 'release_lock_lazorcut', layout.row(), label='Lazorcut Lock')
    label_row(preference.keymap, 'quick_execute', layout.row())

    # label_row(preference.keymap, 'enable_surface_toggle', layout.row())
    label_row(preference.keymap, 'enable_toolsettings', layout.row(), label='Enable Topbar')
    label_row(preference.keymap, 'allow_selection', layout.row(), label='Allow Selection')
    label_row(preference.keymap, 'edit_disable_modifiers', layout.row())
    label_row(preference.keymap, 'rmb_cancel_ngon', layout.row(), label='RMB Cancel Ngon')

    label_row(preference.keymap, 'alt_preserve', layout.row(), label='Preserve Alt')
    label_row(preference.keymap, 'rmb_preserve', layout.row(), label='Preserve RMB')
    label_row(preference.keymap, 'alt_draw', layout.row(), label='Alt Center')
    label_row(preference.keymap, 'shift_draw', layout.row(), label='Shift Uniform')
    label_row(preference.keymap, 'scroll_adjust_circle', layout.row())
    label_row(preference.keymap, 'view_pie', layout.row(), label='View Pie')
