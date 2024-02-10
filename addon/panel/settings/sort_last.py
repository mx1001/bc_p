import bpy

from bpy.types import Panel

from .... utility import addon, tool, modifier


class BC_PT_sort_last(Panel):
    bl_label = 'Sort Last'
    bl_space_type = 'TOPBAR'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    # @classmethod
    # def poll(cls, context):
    #     active = tool.active()
    #     return active and active.idname == tool.name


    def draw(self, context):
        preference = addon.preference()
        layout = self.layout

        row = layout.row(align=True)
        # row.scale_x = 1.5
        # row.scale_y = 1.5

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
            sub = row.row(align=True)
            sub.enabled = getattr(preference.behavior, F'sort_{type.lower()}')
            sub.prop(preference.behavior, F'sort_{type.lower()}_last', text='', icon=icon)

        if preference.behavior.sort_bevel:
            label_row(preference.behavior, 'sort_bevel_ignore_vgroup', layout.row(), label='Ignore Bevels with VGroups')
            label_row(preference.behavior, 'sort_bevel_ignore_only_verts', layout.row(), label='Ignore Bevels using Only Verts')


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')
