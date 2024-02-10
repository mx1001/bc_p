import bpy

from mathutils import Vector

from .. import mesh
from ...... utility import addon, screen, modifier


# XXX: bevel before array
def shape(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc
    snap = preference.snap.enable and preference.snap.incremental
    clamped = False

    if op.shape_type != 'NGON' or (op.shape_type == 'NGON' and len(bc.shape.data.vertices) > 2):
        max_dimension = max(bc.shape.dimensions[:-1])
        width = ((op.mouse['location'].x - op.last['mouse'].x) / screen.dpi_factor(ui_scale=False, integer=True)) * max_dimension
        factor = 0.0001 if event and event.shift else 0.001

        if preference.shape.quad_bevel:
            if not preference.shape.straight_edges:
                mesh.bevel_weight(op, context, event)

            else:
                mesh.vertex_group(op, context, event)
        else:
            mesh.bevel_weight(op, context, event)

        m = None
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                m = mod
                break

        if not m:
            if op.shape_type == 'NGON' and not op.extruded:
                mod = bc.shape.modifiers.new(name='Bevel', type='BEVEL')
                mod.show_expanded = False
                if bpy.app.version < (2, 90, 0):
                    mod.use_only_vertices = True
                else:
                    mod.affect = 'VERTICES'
                mod.width = op.last['modifier']['width']
                mod.segments = preference.shape.bevel_segments
                mod.limit_method = 'ANGLE'
                mod.offset_type = 'OFFSET'

            elif not preference.shape.quad_bevel or (preference.shape.quad_bevel and not preference.shape.straight_edges):
                mod = bc.shape.modifiers.new(name='Bevel', type='BEVEL')
                mod.show_expanded = False
                mod.width = op.last['modifier']['width']
                mod.segments = preference.shape.bevel_segments
                mod.limit_method = 'WEIGHT'
                mod.offset_type = 'OFFSET'

                if width > clamp(op):
                    mod.width = clamp(op) - 0.0025 if bpy.app.version[1] < 82 else clamp(op)

            vertex_groups = bc.shape.vertex_groups if not preference.shape.straight_edges else reversed(bc.shape.vertex_groups)

            for group in vertex_groups:
                mod = bc.shape.modifiers.new(name='Bevel', type='BEVEL')
                mod.show_expanded = False
                mod.width = op.last['modifier']['width']
                mod.segments = preference.shape.bevel_segments
                mod.limit_method = 'VGROUP'
                mod.vertex_group = group.name
                mod.offset_type = 'OFFSET'

                if mod.vertex_group == 'bottom' and not preference.shape.straight_edges:
                    mod.offset_type = 'WIDTH'

                if width > clamp(op):
                    mod.width = clamp(op) - 0.0025 if bpy.app.version[1] < 82 else clamp(op)

            modifier.sort(bc.shape, sort_types=modifier.sort_types, static_sort=True)

        else:
            segment_state = False
            # width = 0.0
            update = True
            for mod in bc.shape.modifiers:
                if mod.type == 'BEVEL':
                    width = op.last['modifier']['width'] + width * factor if op.last['modifier']['width'] + width * factor > 0.0004 else 0.0004

                    if width > clamp(op):
                        clamped = True
                        width = clamp(op) - 0.0025 if bpy.app.version[1] < 82 else clamp(op)

                    if snap and event and event.ctrl:
                        width = round(width, 2 if event and event.shift else 1)

                    elif not clamped:
                        if width < 0.001 and not op.width_state or segment_state:
                            segment_state = True
                            op.width_state = True

                            if mod.segments == 1 and op.segment_state:
                                mod.segments = preference.shape.bevel_segments if preference.shape.bevel_segments != 1 else preference.shape.bevel_segments_default

                            else:
                                op.segment_state = True
                                mod.segments = 1

                        elif width > 0.0011 and op.width_state:
                            op.width_state = False

                        if update:
                            op.last['modifier']['width'] = width
                            op.last['mouse'].x = op.mouse['location'].x

                    if update:
                        preference.shape['bevel_width'] = width

                    mod.width = width

                    update = False


def clamp(op):
    bc = bpy.context.scene.bc

    vector1 = Vector(bc.shape.bound_box[0][:])
    vector2 = Vector(bc.shape.bound_box[1][:])
    vector3 = Vector(bc.shape.bound_box[5][:])
    vector4 = Vector(bc.shape.bound_box[6][:])
    distances = [vector4 - vector3, vector3 - vector2]

    if bc.shape.data.bc.q_beveled:
        distances.append((vector2 - vector1) * 2)

    return max(min(distances)) * 0.5
