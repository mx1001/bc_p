import bpy

from bpy.types import Panel

from .... utility import tool, addon, modifier
from ... property.utility import names
from ... import toolbar


class BC_PT_behavior_settings(Panel):
    bl_label = 'Behavior'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_parent_id = 'BC_PT_settings'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name and context.region.type == 'UI'


    def draw(self, context):
        preference = addon.preference()
        option = toolbar.options()
        layout = self.layout

        # option = None
        # for tool in context.workspace.tools:
        #     if tool.idname == tool.name and tool.mode == tool.active().mode:
        #         option = tool.operator_properties('bc.shape_draw')

        #         break

        # if not option:
            # return

        row = layout.row(align=True)
        self.label_row(layout.row(), preference.behavior, 'sort_modifiers')

        if preference.behavior.sort_modifiers:
            row = layout.row(align=True)
            split = row.split(align=True, factor=0.85)

            row = split.row(align=True)
            for type in modifier.sort_types:
                icon = F'MOD_{type}'
                if icon == 'MOD_WEIGHTED_NORMAL':
                    icon = 'MOD_NORMALEDIT'
                elif icon == 'MOD_SIMPLE_DEFORM':
                    icon = 'MOD_SIMPLEDEFORM'
                elif icon == 'MOD_DECIMATE':
                    icon = 'MOD_DECIM'
                elif icon == 'MOD_WELD':
                    icon = 'AUTOMERGE_OFF'
                elif icon == 'MOD_UV_PROJECT':
                    icon = 'MOD_UVPROJECT'
                row.prop(preference.behavior, F'sort_{type.lower()}', text='', icon=icon)

            row = split.row(align=True)
            row.scale_x = 1.5
            row.popover('BC_PT_sort_last', text='', icon='SORT_ASC')

        self.label_row(layout.row(), preference.behavior, 'keep_modifiers')

        if preference.behavior.keep_modifiers:
            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(preference.behavior, 'keep_bevel', text='', icon='MOD_BEVEL')
            row.prop(preference.behavior, 'keep_solidify', text='', icon='MOD_SOLIDIFY')
            row.prop(preference.behavior, 'keep_array', text='', icon='MOD_ARRAY')
            if bpy.app.version[1] >= 82:
                row.prop(preference.behavior, 'keep_weld', text='', icon='AUTOMERGE_OFF')
            row.prop(preference.behavior, 'keep_mirror', text='', icon='MOD_MIRROR')
            row.prop(preference.behavior, 'keep_screw', text='', icon='MOD_SCREW')
            row.prop(preference.behavior, 'keep_lattice', text='', icon='MOD_LATTICE')

        self.label_row(layout.row(), option, 'active_only', label='Active only')
        # self.label_row(layout.row(), preference.behavior, 'quick_execute')
        self.label_row(layout.row(), preference.behavior, 'line_box')
        self.label_row(layout.row(), preference.behavior, 'auto_ortho')
        self.label_row(layout.row(), preference.behavior, 'apply_slices')
        self.label_row(layout.row(), preference.behavior, 'recut')
        self.label_row(layout.row(), preference.behavior, 'show_wire')
        self.label_row(layout.row(), preference.behavior, 'apply_scale')
        # self.label_row(layout.row(), preference.behavior, 'make_active')
        self.label_row(layout.row(), preference.behavior, 'show_shape')
        self.label_row(layout.row(), preference.behavior, 'auto_smooth')
        self.label_row(layout.row(), preference.behavior, 'parent_shape')
        self.label_row(layout.row(), preference.behavior, 'cutter_uv', label='Cutter UV')
        self.label_row(layout.row(), preference.behavior, 'autohide_shapes', label='Auto Hide')
        self.label_row(layout.row(), preference.behavior, 'surface_extract', label='Surface Extract')
        self.label_row(layout.row(), preference.behavior, 'lazorcut_trim')
        # self.label_row(layout.row(), preference.behavior, 'simple_trace')


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
