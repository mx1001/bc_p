import bpy
import bmesh

from mathutils import Vector, Matrix

from ..... utility import addon, tool, ray, view3d, context_copy, math, object
from .... import toolbar
from ... shape.utility.change import last
from ... shape.utility import modifier
# from ... utility import shape #, lattice, mesh
from .. import utility
# from .. utility import statusbar
# from .. utility import shader
# from .. draw import new
from .... property import new
from .. utility import statusbar


def operator(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc

    bc.running = True
    # prop.running = True
    # prop.extruded = False
    # prop.lazorcut = False
    op.cancelled = False

    if op.shape_type != 'CUSTOM' or not hasattr(bc.collection, 'objects'):

        if 'Cutters' not in bpy.data.collections:
            bc['collection'] = bpy.data.collections.new(name='Cutters')
            context.scene.collection.children.link(bc.collection)

        else:
            bc['collection'] = bpy.data.collections['Cutters']

    if op.shape_type != 'CUSTOM':
        bc.shape = None

    elif not bc.shape:
        dat = bpy.data.meshes.new(name='Cutter')

        dat.from_pydata(new.verts, new.edges, new.faces)
        dat.validate()

        bc.shape = bpy.data.objects.new(name='Cutter', object_data=dat)
        del dat

        bc.shape.display_type = 'WIRE' if op.mode != 'MAKE' else 'TEXTURED'
        bc.shape.bc.shape = True

        bc.collection.objects.link(bc.shape)

        if addon.preference().behavior.auto_smooth:
            bc.shape.data.use_auto_smooth = True

            for face in bc.shape.data.polygons:
                face.use_smooth = True

        bc.shape.hide_set(True)

    if bc.shape:
        collected = False
        for col in bpy.data.collections:
            if bc.shape.name in col.objects:
                collected = True
                bc['collection'] = col

                break

        if not collected:
            if 'Cutters' not in bpy.data.collections:
                bc['collection'] = bpy.data.collections.new(name='Cutters')
                context.scene.collection.children.link(bc.collection)

            else:
                bc['collection'] = bpy.data.collections['Cutters']

            bc.collection.objects.link(bc.shape)

    op.alt_skip = True
    op.alt = event.alt
    op.ctrl = event.ctrl
    op.shift = event.shift
    op.lmb = True
    op.mmb = False
    op.rmb = False
    op.alt_lock = False
    op.click_count = 0
    op.add_point_lock = False
    op.modified = False
    op.datablock = new.datablock.copy()
    op.last = last
    op.ray = new.ray_cast.copy()
    op.start = new.start.copy()
    op.start['extrude'] = 0.0
    op.geo = new.geo.copy()
    op.mouse = new.mouse.copy()
    op.rotated = False
    op.scaled = False
    op.view3d = new.view3d.copy()
    op.segment_state = False
    op.width_state = False
    op.wires_displayed = False
    op.orthographic = False
    op.auto_ortho = False
    op.existing = {}
    op.release_lock = preference.keymap.release_lock
    op.move_lock = False
    op.lazorcut_performed = False
    op.plane_checks = 0

    op.mouse['location'] = Vector((event.mouse_region_x, event.mouse_region_y))
    op.start['mouse'] = Vector((event.mouse_region_x, event.mouse_region_y))
    op.last['mouse'] = op.mouse['location']
    op.init_mouse = op.last['mouse']
    op.datablock['targets'] = [obj for obj in context.selected_objects if obj.type == 'MESH']
    op.datablock['slices'] = []
    op.datablock['wire_targets'] = [obj for obj in op.datablock['targets'] if obj.show_wire]
    op.datablock['bounds'] = []
    op.datablock['dimensions'] = Vector((1, 1, 1))

    if preference.behavior.show_wire:
        for obj in op.datablock['targets']:
            if obj not in op.datablock['wire_targets']:
                obj.show_wire = True
                obj.show_all_edges = True

    op.original_mode = tool.active().mode

    if not op.datablock['targets'] and op.original_mode != 'EDIT_MESH':
        context.view_layer.objects.active = None
    elif op.original_mode == 'EDIT_MESH':
        context.active_object.select_set(True)
        if context.active_object not in op.datablock['targets']:
            op.datablock['targets'].append(context.active_object)

    for obj in bpy.data.objects:
        if obj.type == 'LATTICE':
            obj.data.bc.removeable = False

    for obj in op.datablock['targets']:
        obj.data.use_customdata_vertex_bevel = True
        obj.data.use_customdata_edge_bevel = True
        obj.data.use_customdata_edge_crease = True

        op.existing[obj] = {}
        op.existing[obj]['materials'] = [slot.material for slot in obj.material_slots if slot.material]

    op.snap = preference.snap.enable and event.ctrl

    obj = context.active_object

    if obj and obj.select_get():
        bc.original_active = obj
        op.original_selected = context.selected_objects[:]
        op.original_visible = context.visible_objects[:]

        if preference.behavior.apply_scale and op.original_mode != 'EDIT_MESH':
            for axis in obj.scale:
                if axis != 1.0:
                    matrix = Matrix()
                    matrix[0][0] = obj.scale[0]
                    matrix[1][1] = obj.scale[1]
                    matrix[2][2] = obj.scale[2]

                    obj.data.transform(matrix)

                    for child in obj.children:
                        child.matrix_local = matrix @ child.matrix_local

                    obj.scale = Vector((1.0, 1.0, 1.0))

                    break
    del obj

    if op.datablock['targets']:
        selection_bounds=[]
        for obj in op.datablock['targets']:
            selection_bounds.extend(object.bound_coordinates(obj, obj.matrix_world))

        op.datablock['bounds'] = math.coordinate_bounds(selection_bounds)
        op.datablock['dimensions'] = math.coordinates_dimension(op.datablock['bounds'])

        del selection_bounds


    updated = toolbar.update_operator(op, context)
    if not updated:
        bc.running = False
        return {'PASS_THROUGH'}

    if preference.keymap.allow_selection and preference.keymap.edit_disable_modifiers:
        if op.original_mode == 'EDIT_MESH':
            if not bc.snap.hit:
                if event.ctrl or (event.ctrl and event.shift):
                    bc.running = False

                    return {'PASS_THROUGH'}

    op.last['start_mode'] = op.mode
    op.last['start_operation'] = op.operation
    op.last['shape_type'] = op.shape_type
    op.last['line_box'] = preference.behavior.line_box

    if op.shape_type == 'BOX' and preference.behavior.line_box:
        op.shape_type = 'NGON'
    elif op.shape_type == 'NGON' and preference.behavior.line_box:
        preference.behavior.line_box = False

    if not op.datablock['targets'] and preference.surface != 'WORLD':
        op.last['surface'] = preference.surface
        preference.surface = 'WORLD'

    else:
        op.last['surface'] = preference.surface

    if preference.behavior.auto_smooth:
        for obj in op.datablock['targets']:

            if not obj.data.use_auto_smooth:
                obj.data.use_auto_smooth = True

                for face in obj.data.polygons:
                    face.use_smooth = True

        context.view_layer.update()

    objects = bc.collection.objects[:]
    name = bc.collection.name
    bpy.data.collections.remove(bc.collection)
    bc.collection = bpy.data.collections.new(name=name)
    bc.collection.hide_render = True
    context.scene.collection.children.link(bc.collection)

    for obj in objects:
        bc.collection.objects.link(obj)

    for obj in objects:
        active = bc.original_active and obj == bc.original_active
        selected = obj in op.original_selected[:]
        visible = obj in op.original_visible[:]
        hide = preference.behavior.autohide_shapes and not active and not selected

        if (not active and (not selected and not visible or hide) and obj.display_type in {'WIRE', 'BOUNDS'}) and not obj.hide_get():
            obj.hide_set(True)
        elif not obj.hide_get():
            obj.hide_set(False)

    del objects

    if bc.original_active and bc.original_active.select_get():
        bpy.context.view_layer.objects.active = bc.original_active

    for obj in op.original_selected:
        obj.select_set(True)

    if op.mode == 'KNIFE':
        overlay = context.space_data.overlay
        if not overlay.show_wireframes:
            overlay.show_wireframes = True
            op.wires_displayed = True

    # XXX: edit mode can lose active object info on undo
    if op.original_mode == 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

    utility.data.create(op, context, event, custom_cutter=bc.shape)

    if op.operation == 'SOLIDIFY':
        bc.shape.bc.solidify = True
        utility.modal.solidify.shape(op, context, event)

    elif op.operation == 'ARRAY':
        bc.shape.bc.array = True

        if bc.axis == 'NONE':
            utility.modal.axis.change(op, context, to='X')

        utility.modal.array.shape(op, context, event)

    elif op.operation == 'BEVEL':
        bc.shape.data.bc.q_beveled = bc.q_bevel

        utility.modal.bevel.shape(op, context, event)

    utility.modal.operation.change(op, context, event, to='DRAW', modified=False, init=True)

    op.bounds = modifier.unmodified_bounds(bc.shape, exclude={'LATTICE', 'SCREW', 'SOLIDIFY', 'DISPLACE'})

    op.report({'INFO'}, 'Drawing')

    # op.shader = shader.shape.setup(op)
    # op.widgets = shader.widgets.setup(op)
    statusbar.add()
    op.mode = op.mode # trigger update method

    # if not preference.display.dots:
    #     op.widgets.exit = True

    if not context.space_data.region_3d.is_perspective:
        op.orthographic = True
        bpy.ops.view3d.view_persportho('INVOKE_DEFAULT')

    hops = getattr(context.window_manager, 'Hard_Ops_material_options', False)

    if hops:
        if hops.material_mode == "BLANK":
            bpy.types.HOPS_PT_material_hops.blank_cut()

        if op.mode == 'MAKE' and hops.active_material:
            bc.shape.data.materials.append(bpy.data.materials[hops.active_material])

    if preference.surface == 'OBJECT':
        hit, op.ray['location'], op.ray['normal'], *_ = ray.cast(*op.mouse['location'], selected=True)

        if hit or bc.snap.hit:
            utility.modal.ray.surface(op, context, event)

            if op.last['start_operation'] == 'MIRROR':
                bc.shape.bc.mirror = True
                utility.modal.mirror.shape(op, context, event)

            if bc.rotated_inside:
                utility.modal.rotate.by_90(op, context, event, init=True)

            if op.repeat:
                op.execute(context)
                op.update()
                return {'FINISHED'}

            op.start['alignment'] = 'OBJECT'
            utility.modal.mode.change(op, context, event, to=op.mode, init=True)

            if op.orthographic:
                bpy.ops.view3d.view_persportho('INVOKE_DEFAULT')

            context.window_manager.modal_handler_add(op)
            op.update()
            bpy.ops.bc.draw_interface()
            return {'RUNNING_MODAL'}

    if preference.surface in {'OBJECT', 'VIEW'}:
        op.start['alignment'] = preference.surface
        preference.surface = 'VIEW'
        utility.modal.ray.screen(op, context, event)

        if op.last['start_operation'] == 'MIRROR':
            bc.shape.bc.mirror = True
            utility.modal.mirror.shape(op, context, event)

        if bc.rotated_inside:
            utility.modal.rotate.by_90(op, context, event, init=True)

        if op.repeat:
            op.execute(context)
            op.update()
            return {'PASS_THROUGH'}

        utility.modal.mode.change(op, context, event, to=op.mode, init=True)

        if op.orthographic:
            bpy.ops.view3d.view_persportho('INVOKE_DEFAULT')

        if preference.behavior.auto_ortho and context.space_data.region_3d.is_perspective:
            op.auto_ortho = True
            bpy.ops.view3d.view_persportho('INVOKE_DEFAULT')

        context.window_manager.modal_handler_add(op)
        op.update()
        bpy.ops.bc.draw_interface()
        return {'RUNNING_MODAL'}

    else:
        utility.modal.ray.custom(op, context, event)

        if op.plane_checks > 3:
            op.cancel(context)
            op.update()
            op.report({'WARNING'}, 'No coordinates for placing the shape were found')
            return {'PASS_THROUGH'}

        if op.last['start_operation'] == 'MIRROR':
            bc.shape.bc.mirror = True
            utility.modal.mirror.shape(op, context, event)

        if bc.rotated_inside:
            utility.modal.rotate.by_90(op, context, event, init=True)

        if op.repeat:
            op.execute(context)
            op.update()
            return {'FINISHED'}

        op.start['alignment'] = preference.surface

        if op.datablock['targets']:
            mode = op.mode
        else:
            mode = 'MAKE'
            bc.shape.display_type = 'TEXTURED'

        utility.modal.mode.change(op, context, event, to=mode, init=True)

        if op.orthographic:
            bpy.ops.view3d.view_persportho('INVOKE_DEFAULT')

        context.window_manager.modal_handler_add(op)
        op.update()
        bpy.ops.bc.draw_interface()
        return {'RUNNING_MODAL'}

    bc.running = False

    op.update()
    return {'PASS_THROUGH'}
