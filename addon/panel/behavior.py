import bpy

from bpy.types import Panel

from . settings import hardops
from ... utility import tool, addon
from . utility import preset
from .. import toolbar
from .. property.utility import names


class BC_PT_helper(Panel):
    bl_label = 'Helper'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    # bl_category = 'BoxCutter'


    @classmethod
    def poll(cls, context):
        active = tool.active()
        return active and active.idname == tool.name


    def draw(self, context):
        wm = context.window_manager
        preference = addon.preference()
        bc = context.scene.bc
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
        row.scale_x = 2
        row.scale_y = 1.5
        row.prop(option, 'mode', text='', expand=True)

        if not bc.running:

            layout.separator()

            row = layout.row()
            row.scale_x = 2
            row.scale_y = 1.25

            sub = row.row()
            sub.enabled = not bc.running
            sub.prop(option, 'shape_type', expand=True, text='')

            sub = row.row()
            sub.enabled = option.shape_type != 'NGON'
            sub.prop(option, 'origin', expand=True, text='')

            layout.separator()

            snap = layout.row(align=True)
            snap.scale_x = 1.5
            snap.scale_y = 1.5
            row = snap.row(align=True)
            row.prop(preference.snap, 'enable', text='', icon='SNAP_OFF' if not preference.snap.enable else 'SNAP_ON')

            sub = row.row(align=True)
            sub.active = preference.snap.enable
            sub.prop(preference.snap, 'incremental', text='', icon='SNAP_INCREMENT')

            if preference.snap.incremental or preference.snap.grid:
                sub.prop(preference.snap, 'increment', text='')
                sub.prop(preference.snap, 'increment_lock', text='', icon=F'{"" if preference.snap.increment_lock else "UN"}LOCKED')
                sub = row.row(align=True)
                sub.scale_x = 1.2
                sub.popover('BC_PT_grid', text='', icon='SNAP_GRID')

                row = layout.row(align=True)
                row.alignment = 'RIGHT'
                row.scale_x = 1.22
                row.scale_y = 1.5
                row.active = preference.snap.enable

                row.prop(preference.snap, 'grid', text='', icon='SNAP_GRID')
                row.prop(preference.snap, 'verts', text='', icon='VERTEXSEL')
                row.prop(preference.snap, 'edges', text='', icon='EDGESEL')
                row.prop(preference.snap, 'faces', text='', icon='FACESEL')

            else:

                for _ in range(6):
                    sub.separator()

                sub.prop(preference.snap, 'grid', text='', icon='SNAP_GRID')
                sub.prop(preference.snap, 'verts', text='', icon='VERTEXSEL')
                sub.prop(preference.snap, 'edges', text='', icon='EDGESEL')
                sub.prop(preference.snap, 'faces', text='', icon='FACESEL')

        if option.mode == 'INSET':
            layout.row().label(text='\u2022 Inset')
            self.label_row(layout.row(align=True), preference.shape, 'inset_thickness', label='Thickness')
            self.label_row(layout.row(align=True), preference.behavior, 'recut')

        elif option.mode == 'SLICE':
            layout.row().label(text=f'\u2022 Slice')
            self.label_row(layout.row(align=True), preference.behavior, 'recut')

        elif option.mode == 'KNIFE' and addon.hops():
            layout.row().label(text=f'\u2022 Knife')
            self.label_row(layout.row(align=True), preference.behavior, 'hops_mark')

        if option.shape_type == 'BOX':
            # layout.row().label(text='\u2022 Line Box')
            self.label_row(layout.row(align=True), preference.behavior, 'line_box', label='\u2022 Line Box')
            if preference.behavior.line_box:
                self.label_row(layout.row(align=True), preference.snap, 'line_box_angle', label='Line Angle')
                self.label_row(layout.row(align=True), preference.shape, 'wedge')

        elif option.shape_type == 'NGON':
            layout.row().label(text='\u2022 Ngon')
            self.label_row(layout.row(align=True), preference.snap, 'ngon_angle', label='Ngon Angle')
            self.label_row(layout.row(align=True), context.scene.bc, 'cyclic', label='Cyclic')

        elif option.shape_type == 'CIRCLE':
            layout.row().label(text='\u2022 Circle')
            self.label_row(layout.row(align=True), preference.shape, 'circle_vertices', label='Vertices')

        elif option.shape_type == 'CUSTOM':
            layout.row().label(text='\u2022 Custom')
            self.label_row(layout.row(align=True), bc, 'collection', label='Collection')

            if not bc.collection:
                self.label_row(layout.row(align=True), bc, 'shape', label='Shape')

            else:
                row = layout.row(align=True)
                split = row.split(factor=0.5)
                split.label(text='Shape')
                split.prop_search(bc, 'shape', bc.collection, 'objects', text='')

        layout.row().label(text='\u2022 Rotation')
        self.label_row(layout.row(align=True), preference.snap, 'rotate_angle', label='Snap Angle')

        if bc.shape:

            if bc.shape.bc.array:
                layout.row().label(text='\u2022 Array')
                self.label_row(layout.row(align=True), preference.shape, 'array_count', label='Count')

            if bc.shape.bc.solidify:
                layout.row().label(text='\u2022 Solidify')
                self.label_row(layout.row(align=True), preference.shape, 'solidify_thickness', label='Thickness')

            if bc.shape.bc.bevel:
                layout.row().label(text='\u2022 Bevel')
                self.label_row(layout.row(align=True), preference.shape, 'bevel_width', label='Width')
                self.label_row(layout.row(align=True), preference.shape, 'bevel_segments', label='Segments')

        elif bc.start_operation == 'ARRAY':
            layout.row().label(text='\u2022 Array')
            self.label_row(layout.row(align=True), preference.shape, 'array_count', label='Count')

        elif bc.start_operation == 'SOLIDIFY':
            layout.row().label(text='\u2022 Solidify')
            self.label_row(layout.row(align=True), preference.shape, 'solidify_thickness', label='Thickness')

        elif bc.start_operation == 'BEVEL':
            self.label_row(layout.row(align=True), preference.shape, 'bevel_width', label='Width')
            self.label_row(layout.row(align=True), preference.shape, 'bevel_segments', label='Segments')

        if option.mode == 'JOIN' and option.shape_type == 'CUSTOM':
            self.label_row(layout.row(align=True), preference.behavior, 'join_flip_z', label='Flip Z')

        hops = hasattr(wm, 'Hard_Ops_material_options')
        if hops:
            self.layout.separator()
            self.header_row(layout.row(align=True), 'hops', label='HardOps')
            if preference.expand.hops:
                hardops.BC_PT_hardops_settings.draw(self, context)


    def header_row(self, row, prop, label='', emboss=False):
        preference = addon.preference()
        icon = 'DISCLOSURE_TRI_RIGHT' if not getattr(preference.expand, prop) else 'DISCLOSURE_TRI_DOWN'
        row.alignment = 'LEFT'
        row.prop(preference.expand, prop, text='', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.25
        sub.prop(preference.expand, prop, text='', icon=icon, emboss=emboss)
        row.prop(preference.expand, prop, text=F'{label}', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.75
        sub.prop(preference.expand, prop, text=' ', icon='BLANK1', emboss=emboss)


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')


    def label_row(self, row, path, prop, label=''):
        if prop in {'line_box_angle', 'circle_vertices', 'ngon_angle', 'rotate_angle', 'array_count', 'bevel_width', 'bevel_segments', 'recut'}:
            column = self.layout.column(align=True)
            row = column.row(align=True)

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        values = {
            'Line Angle': preset.line_angle,
            'Vertices': preset.vertice,
            'Count': preset.array,
            'Width': preset.width,
            'Segments': preset.segment,
            'Snap Angle': preset.angle,
            'Ngon Angle': preset.angle}

        if prop in {'line_box_angle', 'circle_vertices', 'ngon_angle', 'rotate_angle', 'array_count', 'bevel_width', 'bevel_segments'}:
            row = column.row(align=True)
            split = row.split(factor=0.48, align=True)
            sub = split.row(align=True)
            sub = split.row(align=True)

            pointer = '.snap.' if prop in {'line_box_angle', 'ngon_angle', 'rotate_angle'} else '.shape.'
            for value in values[label]:
                op = sub.operator(F'wm.context_set_{"int" if prop != "bevel_width" else "float"}', text=str(value))
                op.data_path = F'preferences.addons["{__name__.partition(".")[0]}"].preferences{pointer}{prop}'
                op.value = value

            column.separator()
