import bpy

from bpy.types import Panel

from .. keymap import keys

from ... utility import tool, addon
from .. property.utility import names
from .. import toolbar


class BC_PT_mode(Panel):
    bl_label = 'Mode'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'


    @classmethod
    def poll(cls, context):
        return tool.active().mode in {'OBJECT', 'EDIT_MESH'}


    def draw(self, context):
        preference = addon.preference()
        option = toolbar.options()

        layout = self.layout
        bc = context.scene.bc

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        #         break

        if not option:
            hotkey = [kmi[1] for kmi in keys if kmi[1].idname == 'bc.tool_activate'][0]

            shift = 'Shift' if hotkey.shift else ''
            ctrl = 'Ctrl' if hotkey.ctrl else ''
            alt = 'Alt' if hotkey.alt else ''
            cmd = 'Cmd+' if hotkey.oskey else '+'

            shift += '+' if hotkey.ctrl and hotkey.shift else ''
            ctrl += '+' if hotkey.alt and hotkey.ctrl else ''
            alt += '+' if hotkey.oskey and hotkey.alt else ''

            key = hotkey.type

            row = layout.row()
            row.alignment = 'LEFT'
            row.operator('bc.tool_activate', emboss=False)
            layout.label(text=F'\u2022 {shift+ctrl+alt+cmd+key}')

            return

        row = layout.row(align=True)
        row.scale_x = 2
        row.scale_y = 1.5
        row.prop(option, 'mode', text='', expand=True)

        if option and option.mode in {'SLICE', 'INSET'} and self.is_popover:
            self.label_row(layout.row(), preference.behavior, 'recut')

        elif addon.hops() and option and option.mode  == 'KNIFE' and self.is_popover:
            self.label_row(layout.row(), preference.behavior, 'hops_mark')
        elif addon.hops() and option and option.mode  == 'EXTRACT' and self.is_popover:
            self.label_row(layout.row(), preference.behavior, 'surface_extract', label='Surface Extract')


    #TODO: create generic util
    # requires row, path, str of prop
    # label: label to use
    # preset: set, props to enable presets
    # peset_values: values in preset
    # preset_type: type() if prop (INTEGER or FLOAT only)
    def label_row(self, row, path, prop, label=''):
        # if prop in {'recut'}:
        column = self.layout.column(align=True)
        row = column.row(align=True)
        # else:
        #     row.scale_x = 1.2

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        # values = {
        #     'Count': preset.array,
        #     'Width': preset.width,
        #     'Segments': preset.segment}

        # if prop in {'array_count', 'bevel_width', 'bevel_segments'}:
        # if prop in {''}:
        #     row = column.row(align=True)
        #     split = row.split(factor=0.49, align=True)
        #     sub = split.row(align=True)
        #     sub = split.row(align=True)

        #     for value in values[label]:
        #         op = sub.operator(F'wm.context_set_{"int" if prop != "bevel_width" else "float"}', text=str(value))
        #         op.data_path = F'preferences.addons["{__name__.partition(".")[0]}"].preferences.shape.{prop}'
        #         op.value = value

        #     column.separator()
