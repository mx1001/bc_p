import bpy
import bmesh

from mathutils import Matrix, Vector, Euler

from . import modal, change, custom, data, lattice, mesh, modifier
from ..... utility import addon, object


class tracked_events:
    mouse: dict = {}
    lmb: bool = False
    mmb: bool = False
    rmb: bool = False
    ctrl: bool = False
    alt: bool = False
    shift: bool = False


class tracked_states:
    running = None
    widgets = None
    widget = None

    mode: str = 'CUT'
    operation: str = 'DRAW'
    shape_type: str = 'BOX'
    origin: str = 'CENTER'
    rotated: bool = False
    scaled: bool = False
    cancelled: bool = False
    rmb_lock: bool = False
    modified: bool = False
    bounds: list = []
    thin: bool = False
    draw_dot_index: int = 0

    # partition('_')[-1] is used in hops notification text
    array_distance: float = 0.0


def lazorcut(op, context):
    preference = addon.preference()
    bc = context.scene.bc
    boolean = False

    if op.mode == 'KNIFE' and preference.surface == 'VIEW':
        return

    if op.shape_type == 'NGON' and not bc.cyclic:
        for mod in bc.shape.modifiers:
            if mod.type == 'SCREW':
                bc.shape.modifiers.remove(mod)

                break

    if op.mode == 'MAKE':
        bc.shape.display_type = 'TEXTURED'

    for obj in op.datablock['targets']:
        for mod in reversed(obj.modifiers[:]):
            if mod.type == 'BOOLEAN' and mod.object == bc.shape:
                boolean = True
                mod.show_viewport = True

    op.lazorcut = True

    if op.datablock['targets']:
        init_point_positions(op, bc, context)

    else:
        init_point_positions(op, bc, context, depth=preference.shape.lazorcut_depth)

        return

    if not boolean:
        modifier.create.boolean(op, show=True)

    alignment = op.start['alignment']
    if not preference.behavior.lazorcut_trim or not alignment or not op.datablock['targets']:
        return

    objects = [obj.copy() for obj in op.datablock['targets'] if obj.type == 'MESH']

    for obj in objects:
        context.scene.collection.objects.link(obj)

    context.view_layer.update()

    for obj in objects:
        obj.data = obj.data.copy()

        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and mod.object == bc.shape:
                obj.modifiers.remove(mod)

            elif not mod.show_viewport:
                mod.show_viewport = True

        # modifier.apply(obj, hard_apply=False)
        modifier.apply(obj)

    mesh = bpy.data.meshes.new(name='TMP')
    bm = bmesh.new()

    # for o, obj in zip(op.datablock['targets'], objects):
    #     obj.matrix_world = o.matrix_world

    # context.view_layer.update()

    for obj in objects:
        obj.data.transform(obj.matrix_world)
        bm.from_mesh(obj.data)
        # obj.location = Vector()

        bpy.data.objects.remove(obj)

    del objects

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name='TMP', object_data=mesh)
    obj.display_type = 'WIRE'
    context.scene.collection.objects.link(obj)
    obj.bc.removeable = True
    obj.data.bc.removeable = True

    # mod = obj.modifiers.new(name='TMP', type='DISPLACE')
    # mod.mid_level = 0
    # mod.strength = preference.shape.offset

    if True in [dimension < 0.0001 for dimension in obj.dimensions[:]]:
        mod = obj.modifiers.new(name='TMP', type='SOLIDIFY')
        mod.offset = 0.0
        mod.thickness = 0.0001

    mod = obj.modifiers.new(name='TMP', type='BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.object = bc.shape

    obj.data.transform(bc.shape.matrix_world.inverted())
    obj.matrix_world = bc.shape.matrix_world

    context.view_layer.update()

    # if obj.dimensions[2] < 0.001:
    #     print('here')
    #     return

    # aligned = op.mode == 'KNIFE' and op.align_to_view
    depth = preference.shape.lazorcut_depth + preference.shape.offset
    for point in lattice.back:
        bc.lattice.data.points[point].co_deform.z = -(obj.dimensions[2] + (preference.shape.offset + 0.01) if not preference.shape.lazorcut_depth else depth)

    if op.shape_type == 'NGON':
        bevel = False
        segment_count = preference.shape.bevel_segments
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                bevel = True

                if mod.segments != segment_count:
                    segment_count = mod.segments

                bc.shape.modifiers.remove(mod)

        if not op.extruded:
            modal.extrude.shape(op, context, None, extrude_only=True)

        if bevel:
            modal.bevel.shape(op, context, None)

        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                if mod.segments != segment_count:
                    mod.segments = segment_count

        verts = [vert for vert in bc.shape.data.vertices[:] if vert.index in op.geo['indices']['extrusion']]

        for vert in verts:
            vert.co.z = -(obj.dimensions[2] + (preference.shape.offset + 0.01) if not preference.shape.lazorcut_depth else depth)

    front = (1, 2, 5, 6)

    # matrix = bc.shape.matrix_world.inverted()
    location = (0.25 * sum((Vector(bc.shape.bound_box[point][:]) for point in front), Vector()))
    location_to = (0.25 * sum((Vector(obj.bound_box[point][:]) for point in front), Vector()))
    difference = (location - location_to)
    difference.z -= preference.shape.offset

    current = bc.shape.location
    location = Vector((0, 0, -difference.z)) @ bc.shape.matrix_world.inverted()

    # for point in (0, 1, 2, 3, 4, 5, 6, 7):
    #     bc.lattice.data.points[point].co_deform = bc.lattice.data.points[point].co_deform + location
    bc.lattice.location = current + location
    bc.shape.location = current + location

    context.view_layer.update()

    op.start['matrix'] = bc.shape.matrix_world.copy()

    obj.data.bc.removeable = True
    bpy.data.objects.remove(obj)

    del obj

    op.lazorcut_performed = True
    op.start['offset'] = bc.lattice.data.points[1].co_deform.z
    op.start['extrude'] = bc.lattice.data.points[5].co_deform.z


def init_point_positions(op, bc, context, depth=None):
    aligned = op.mode == 'KNIFE' and op.align_to_view
    if op.shape_type != 'NGON':
        for point in lattice.back:
            if context.active_object:
                bc.lattice.data.points[point].co_deform.z -= max(op.datablock['dimensions']) * 2
            elif depth:
                if op.mode != 'MAKE':
                    bc.lattice.data.points[point].co_deform.z -= depth
                else:
                    bc.lattice.data.points[point].co_deform.z += depth
            else:
                if op.mode != 'MAKE':
                    bc.lattice.data.points[point].co_deform.z -= 0.5
                else:
                    bc.lattice.data.points[point].co_deform.z += 0.5

    elif not aligned:
        if not op.extruded:
            # modal.extrude.shape(op, context, None)
            mesh.extrude(op, context, None)

        verts = [vert for vert in bc.shape.data.vertices[:] if vert.index in op.geo['indices']['extrusion']]

        for vert in verts:
            if bc.original_active:
                vert.co.z -= max(op.datablock['dimensions']) * 2
            elif depth:
                if op.mode != 'MAKE':
                    vert.co.z -= depth
                else:
                    vert.co.z += depth
            else:
                if op.mode != 'MAKE':
                    vert.co.z -= 0.5
                else:
                    vert.co.z += 0.5
