import traceback

import bpy
import bmesh

from math import radians

from mathutils import Matrix, Vector

from .... import toolbar

from ..... utility import addon, object, math
from ..... utility import mesh as _mesh
# from .. shape import lattice, mesh, modifier, modal
from . import lattice, mesh, modifier, modal, custom
# from .. shape import custom as _custom


def restore_overrides(op, clear=True):
    slices = op.datablock['slices'] if op.mode != 'INSET' else []
    for pair in zip(op.datablock['targets'] + slices, op.datablock['overrides']):
        obj = pair[0]
        override = pair[1]

        bpy.context.view_layer.objects.active = obj
        name = obj.data.name
        obj.data.name = 'tmp'

        obj.data = override
        obj.data.name = name

    if clear:
        op.datablock['overrides'] = list()


def create(op, context, event, custom_cutter=None):
    bc = context.scene.bc

    mesh.create.shape(op, context, event)
    lattice.create(op, context, event)

    if custom_cutter:
        custom.cutter(op, context, custom=custom_cutter)

    bc.empty = bpy.data.objects.new(name=F'{bc.shape.name} Array Target', object_data=None)
    bc.collection.objects.link(bc.empty)
    bc.empty.empty_display_type = 'SINGLE_ARROW'
    bc.empty.parent = bc.shape
    bc.empty.hide_set(True)


def clean(op, context, all=False):
    preference = addon.preference()
    bc = bpy.context.scene.bc
    type_to_custom = False

    for obj in context.selected_objects:
        obj.select_set(False)

    if op.wires_displayed:
        context.space_data.overlay.show_wireframes = False

    if not op.live and op.mode in {'CUT', 'SLICE', 'INTERSECT', 'INSET', 'JOIN', 'EXTRACT'}:
        modifier.create.boolean(op, show=True)

    bc.shape.hide_set(False)
    bc.lattice.hide_set(False)

    if context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    context.view_layer.update()
    bc.shape.data.update()

    for mod in bc.shape.modifiers:
        mod.show_viewport = True

        if mod.type == 'BEVEL':
            preference.shape['bevel_segments'] = mod.segments

    for obj in op.datablock['targets']:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and (mod.object == bc.shape or op.original_mode == 'EDIT_MESH'):
                mod.show_viewport = True

    for obj in op.datablock['slices']:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and (mod.object == bc.shape or op.original_mode == 'EDIT_MESH'):
                mod.show_viewport = True

    for obj in context.visible_objects:
        if obj not in op.datablock['wire_targets']:
            obj.show_wire = False
            obj.show_all_edges = False

    keep_types = [type for type in ('BEVEL', 'SOLIDIFY', 'ARRAY', 'MIRROR', 'SCREW', 'LATTICE') if getattr(preference.behavior, F'keep_{type.lower()}')] if preference.behavior.keep_modifiers else []
    keep_types.append('DISPLACE')
    keep_types.append('DECIMATE')

    if bpy.app.version[1] >= 82:
        keep_types.append('WELD')

    modifier.apply(bc.shape, ignore=[mod for mod in bc.shape.modifiers if mod.type in keep_types])

    if not op.live and op.original_mode == 'EDIT_MESH' and op.mode != 'EXTRACT':
        modifier.update(op, bpy.context, force_edit_mode=False)

    if op.shape_type == 'CIRCLE' and not preference.behavior.keep_screw:
        for mod in bc.shape.modifiers:
            if mod.type == 'DECIMATE':
                bc.shape.modifiers.remove(mod)

        bm = bmesh.new()
        bm.from_mesh(bc.shape.data)

        #XXX: ran twice to ensure success
        bmesh.ops.dissolve_limit(bm, angle_limit=0.01, use_dissolve_boundaries=True, verts=bm.verts, edges=bm.edges)
        bmesh.ops.dissolve_limit(bm, angle_limit=0.01, use_dissolve_boundaries=True, verts=bm.verts, edges=bm.edges)

        bm.to_mesh(bc.shape.data)
        bm.free()

        indices = []
        for vert in bc.shape.data.vertices:
            index = 5 if not op.flip_z else 1

            if round(vert.co.z, 5) == round(bc.lattice.data.points[index].co_deform.z, 5):
                indices.append(vert.index)

        if len(bc.shape.vertex_groups) and len(indices):
            bc.shape.vertex_groups[0].add(index=indices, weight=1.0, type='ADD')

    context.view_layer.objects.active = bc.shape

    if op.lazorcut:
        if op.mode not in {'MAKE', 'KNIFE', 'EXTRACT'} and op.original_mode == 'EDIT_MESH':
            modifier.update(op, bpy.context, force_edit_mode=False)

        elif op.mode == 'KNIFE':

            bc.shape.select_set(True)

            if preference.surface != 'VIEW':
                op.extruded = True
                mesh.knife(op, bpy.context, None)

            elif not all:
                all = True

                modifier.apply(bc.shape)

                bpy.ops.object.mode_set(mode='EDIT')

                original_selection_mode = tuple(bpy.context.tool_settings.mesh_select_mode)

                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=preference.shape.offset + 0.001)
                bpy.ops.object.mode_set(mode='OBJECT')

                bc.shape.data.update()

    #             context.view_layer.update()

                for obj in op.datablock['targets']:
                    context.view_layer.objects.active = obj
                    obj.select_set(True)

                    context.view_layer.update()

                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.knife_project(cut_through=True)
                    bpy.ops.object.mode_set(mode='OBJECT')

                    if addon.hops() and addon.preference().behavior.hops_mark:
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.context.scene.tool_settings.mesh_select_mode = (False, True, False)
                        bpy.ops.mesh.region_to_loop()
                        bpy.ops.object.mode_set(mode='OBJECT')

                        pref = addon.hops().property

                        for edge in obj.data.edges:
                            if not edge.select:
                                continue

                            edge.crease = float(pref.sharp_use_crease)
                            edge.use_seam = float(pref.sharp_use_seam)
                            edge.bevel_weight = float(pref.sharp_use_bweight)
                            edge.use_edge_sharp = float(pref.sharp_use_sharp)

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.loop_to_region()

                        bpy.context.tool_settings.mesh_select_mode = original_selection_mode

                    bpy.ops.object.mode_set(mode='OBJECT')

                    obj.select_set(False)

                context.view_layer.objects.active = bc.shape

                if op.original_mode == 'EDIT_MESH':
                    bpy.ops.object.mode_set(mode='EDIT')

                    bpy.context.tool_settings.mesh_select_mode = original_selection_mode

        elif op.mode == 'MAKE':
            bm = bmesh.new()
            bm.from_mesh(bc.shape.data)

            bmesh.ops.recalc_face_normals(bm, faces = bm.faces)

            bm.to_mesh(bc.shape.data)
            bc.shape.data.update()
            bm.free()

    # modal.bevel_modifiers = list()

    if not all:
        if op.mode == 'EXTRACT':
            type_to_custom = True

            restore_overrides(op)

            for obj in op.datablock['targets']:
                for mod in obj.modifiers:
                    if mod.type == 'BOOLEAN' and mod.object == bc.shape:
                        obj.modifiers.remove(mod)

            if preference.behavior.surface_extract:
                slice_bound_coordinates = []

                for obj in op.datablock['slices']:
                    for mod in obj.modifiers:
                        if mod.type == 'BEVEL':
                            obj.modifiers.remove(mod)

                    bpy.context.view_layer.update()

                    modifier.apply(obj)

                    object.apply_transforms(obj)
                    obj.data.transform(bc.shape.matrix_world.inverted())

                    slice_bound_coordinates.extend(object.bound_coordinates(obj))

                if slice_bound_coordinates:
                    new = bc.shape.copy()
                    new.data = bc.shape.data.copy()
                    new.name = 'Extraction'

                    object.clear_transforms(new)

                    bc.collection.objects.link(new)

                    trim = bpy.data.objects.new('trim', bpy.data.meshes.new('trim'))
                    bc.collection.objects.link(trim)

                    bm = bmesh.new()

                    bmesh.ops.create_cube(bm)

                    bm.to_mesh(trim.data)
                    bm.free()

                    bbox_coords = math.coordinate_bounds(slice_bound_coordinates)
                    trim.location = math.coordinates_center(bbox_coords)
                    trim.dimensions = math.coordinates_dimension(bbox_coords)

                    mod = new.modifiers.new(name='Displace', type='DISPLACE')
                    mod.mid_level = 0
                    mod.strength = -0.0001

                    mod = new.modifiers.new(name='Boolean', type='BOOLEAN')
                    mod.operation = 'INTERSECT'
                    mod.object = trim

                    mod = new.modifiers.new(name='Displace', type='DISPLACE')
                    mod.mid_level = 0
                    mod.strength = -0.002

                    for obj in op.datablock['slices']:
                        mod = new.modifiers.new(name='Boolean', type='BOOLEAN')
                        mod.operation = 'DIFFERENCE'
                        mod.object = obj

                    modifier.apply(new)
                    bpy.data.objects.remove(trim)

            else:

                slice_duplicates = []
                for obj in op.datablock['slices']:

                    for mod in obj.modifiers:
                        if mod.type in {'BEVEL', 'MIRROR'}:
                            obj.modifiers.remove(mod)

                    bpy.context.view_layer.update()

                    object.apply_transforms(obj)

                    new = obj.copy()
                    slice_duplicates.append(new)
                    obj.data = obj.data.copy()

                    bc.collection.objects.link(new)

                    modifier.apply(obj)

                me = bpy.data.meshes.new(name='Extraction')
                bm = bmesh.new()
                for obj in slice_duplicates:
                    for mod in obj.modifiers:

                        if mod.type == 'BOOLEAN' and mod.operation != 'INTERSECT':
                            obj.modifiers.remove(mod)

                    bpy.context.view_layer.update()

                    modifier.apply(obj)

                    center = object.center(obj)
                    obj.location = obj.matrix_world @ center
                    obj.data.transform(Matrix.Translation(-center))

                    _mesh.transform_scale(obj.data, uniform=0.998)

                    obj.data.transform(Matrix.Translation(obj.location))

                    bm.from_mesh(obj.data)

                    bpy.data.objects.remove(obj)
                bm.to_mesh(me)
                bm.free()

                new = bpy.data.objects.new(name='Extraction', object_data=me)
                bc.collection.objects.link(new)

                for obj in op.datablock['slices']:
                    mod = new.modifiers.new(name='Boolean', type='BOOLEAN')
                    mod.operation = 'DIFFERENCE'
                    mod.object = obj

                bpy.context.view_layer.update()

                modifier.apply(new)

                new.data.transform(bc.shape.matrix_world.inverted())

            bpy.context.view_layer.update()

            for face in obj.data.polygons:
                face.use_smooth = True

            new.data.use_auto_smooth = True
            new.data.auto_smooth_angle = radians(15)
            new.data.use_customdata_vertex_bevel = True
            new.data.use_customdata_edge_bevel = True
            new.data.use_customdata_edge_crease = True

            if sum(new.dimensions) > 0.001:
                center = object.center(new)
                new.location = obj.matrix_world @ center
                new.data.transform(Matrix.Translation(-center))

                object.clear_transforms(new)
                bc.stored_shape = new
                new.hide_set(True)

            else:
                bpy.data.objects.remove(new)
                op.report({'INFO'}, F'Cancelled. Extracted volume is too small')

            bpy.data.objects.remove(bc.shape)
            bc.shape = None

            for obj in op.datablock['slices']:
                bpy.data.objects.remove(obj)

            if bc.original_active:
                bpy.context.view_layer.objects.active = bc.original_active

            for obj in op.original_selected:
                obj.select_set(True)

            restore_overrides(op)

        elif op.mode != 'KNIFE':
            if op.mode != 'MAKE':
                if op.original_mode != 'EDIT_MESH':
                    if op.shape_type in {'CIRCLE', 'NGON'}:
                        bc.shape.hide_set(False)
                        bpy.ops.object.mode_set(mode='EDIT')
                        original_selection_mode = tuple(bpy.context.tool_settings.mesh_select_mode)
                        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.remove_doubles(threshold=0.0006)

                        if (bc.cyclic and not preference.behavior.line_box) or op.shape_type == 'CIRCLE':
                            bpy.ops.mesh.normals_make_consistent(inside=False)

                        bpy.context.tool_settings.mesh_select_mode = original_selection_mode
                        bpy.ops.object.mode_set(mode='OBJECT')

                        # bpy.context.view_layer.update()

                    if op.behavior != 'DESTRUCTIVE':
                        bc.shape.bc.applied = True

            else:
                # TODO: if in edit mode join made geo with active object
                bc.collection.objects.unlink(bc.shape)

                if bc.original_active and bc.original_active.users_collection:
                    for collection in bc.original_active.users_collection:
                        collection.objects.link(bc.shape)
                else:
                    bpy.context.scene.collection.objects.link(bc.shape)

                bpy.context.view_layer.objects.active = bc.shape

                if op.shape_type in {'CIRCLE', 'NGON'}:
                    bpy.ops.object.mode_set(mode='EDIT')
                    original_selection_mode = tuple(bpy.context.tool_settings.mesh_select_mode)
                    bpy.context.tool_settings.mesh_select_mode = (True, False, False)
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.remove_doubles(threshold=0.0006)
                    bpy.ops.mesh.normals_make_consistent(inside=False)
                    bpy.context.tool_settings.mesh_select_mode = original_selection_mode
                    bpy.ops.object.mode_set(mode='OBJECT')

                bc.shape.name = op.shape_type.title()
                bc.shape.data.name = op.shape_type.title()
                bc.shape.bc.applied = True
                bc.shape.hide_render = False
                bc.shape.hide_set(False)

                if hasattr(bc.shape, 'cycles_visibility'):
                    bc.shape.cycles_visibility.camera = True
                    bc.shape.cycles_visibility.diffuse = True
                    bc.shape.cycles_visibility.glossy = True
                    bc.shape.cycles_visibility.transmission = True
                    bc.shape.cycles_visibility.scatter = True
                    bc.shape.cycles_visibility.shadow = True

            if op.show_shape:
                bc.shape.hide_set(False)

                if (not preference.keymap.make_active and op.datablock['targets']) or (not op.shift and op.datablock['targets']):
                    bpy.context.view_layer.objects.active = bc.original_active
                    bc.original_active.select_set(True)
                    bc.shape.select_set(False)

                else:
                    bc.shape.select_set(op.mode != 'INSET')

                    for obj in bpy.context.visible_objects:
                        if obj != bc.shape:
                            obj.select_set(False)

                        elif not bc.original_active:
                            bpy.context.view_layer.objects.active = obj
                            obj.select_set(True)

                    if op.mode == 'INSET':
                        bc.inset.hide_set(False)
                        bc.inset.select_set(True)
                        bpy.context.view_layer.objects.active = bc.inset

                if op.original_mode == 'EDIT_MESH' and op.datablock['targets']:
                    restore_overrides(op)
                    context.view_layer.objects.active = bc.shape

            else:
                if op.mode != 'MAKE':
                    bc.shape.hide_set(True)

                    if op.mode == 'INSET':
                        bc.shape.select_set(False)

                        for obj in op.datablock['slices']:
                            obj.hide_set(True)

                    if op.original_mode == 'EDIT_MESH':

                        for obj in op.datablock['slices']:
                            obj.select_set(True)

                            for mod in obj.modifiers:
                                if mod.type == 'BOOLEAN' and mod.object == bc.shape:
                                    obj.modifiers.remove(mod)

                if op.datablock['targets']:
                    bpy.context.view_layer.objects.active = bc.original_active
                    bc.original_active.select_set(True)

                    bpy.ops.object.mode_set(mode='OBJECT')

                    for obj in op.original_selected:
                        obj.select_set(True)

                    if op.behavior == 'DESTRUCTIVE' and op.original_mode != 'EDIT_MESH' and op.mode not in {'MAKE', 'EXTRACT'}:
                        for obj in op.datablock['targets']:
                            for mod in obj.modifiers:
                                if op.mode == 'INSET' and mod.type == 'BOOLEAN' and mod.object == bc.shape:
                                    obj.modifiers.remove(mod)

                        for obj in op.datablock['targets']:
                            # modifier.apply(obj, mod=modifier.shape_bool(obj))

                            if op.mode == 'INSET':

                                for mod in obj.modifiers:
                                    if mod.type == 'BOOLEAN' and mod.object in op.datablock['slices']:
                                        modifier.apply(obj, mod=mod)

                            else:
                                modifier.apply(obj, mod=modifier.shape_bool(obj))

                        for obj in op.datablock['slices']:
                            modifier.apply(obj, mod=modifier.shape_bool(obj))

                        for obj in op.datablock['slices']:
                            if op.mode == 'INSET':
                                bpy.data.objects.remove(obj)
                            else:
                                obj.select_set(True)

                    elif op.mode == 'SLICE' and preference.behavior.apply_slices and op.original_mode != 'EDIT_MESH':

                        for obj in op.datablock['slices']:

                            bvls = [mod for mod in obj.modifiers if mod.type == 'BEVEL'][-1:]
                            wns = [mod for mod in obj.modifiers if mod.type == 'WEIGHTED_NORMAL']
                            ignore = bvls + wns

                            modifier.apply(obj, ignore=ignore)
                            obj.select_set(True)

                            bvl = [mod for mod in obj.modifiers if mod.type == 'BEVEL'][-1:]
                            wn = [mod for mod in obj.modifiers if mod.type == 'WEIGHTED_NORMAL'][-1:]

                            if bvl and True not in [d < 0.0001 for d in obj.dimensions]:
                                if bpy.app.version < (2, 90, 0):
                                    bvl[0].use_only_vertices = False
                                else:
                                    bvl[0].affect = 'EDGES'

                            for mod in obj.modifiers:
                                if (not bvl or mod != bvl[0]) and (not wn or mod != wn[0]):
                                    obj.modifiers.remove(mod)

                    elif op.mode == 'SLICE':
                        for obj in op.datablock['slices']:
                            obj.select_set(True)

                    if op.original_mode == 'EDIT_MESH':
                        for obj in op.datablock['targets']:
                            for mod in obj.modifiers:
                                if mod.type == 'BOOLEAN':
                                    if mod.object == bc.shape or mod.object in op.datablock['slices']:
                                        obj.modifiers.remove(mod)

                        bpy.ops.object.mode_set(mode='EDIT')

            if op.mode == 'INSET':
                for obj in op.datablock['targets']:
                    for mod in obj.modifiers:
                        if mod.type == 'BOOLEAN' and mod.object == bc.shape:
                            obj.modifiers.remove(mod)

            if hasattr(bc.shape, 'hops'):
                bc.shape.hops.status = 'BOOLSHAPE' if op.mode != 'MAKE' else 'UNDEFINED'

        else:

            if not op.live:
                op.extruded = True
                mesh.knife(op, bpy.context, None)

            bpy.data.objects.remove(bc.shape)
            bc.shape = None

            bpy.context.view_layer.objects.active = bc.original_active
            bc.original_active.select_set(True)

            for obj in op.original_selected:
                obj.select_set(True)

            if op.original_mode == 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='EDIT')

        if not preference.behavior.keep_lattice:
            bpy.data.objects.remove(bc.lattice)

        else:
            bc.lattice.data.bc.removeable = False
            bc.lattice.hide_set(not op.show_shape)

        bpy.data.objects.remove(op.datablock['plane'])

        for me in bpy.data.meshes:
            if me.bc.removeable:
                bpy.data.meshes.remove(me)

        for lat in bpy.data.lattices:
            if lat.bc.removeable:
                bpy.data.lattices.remove(lat)

        array = None

        if bc.shape:
            bc.shape.data.name = bc.shape.name

            for mod in bc.shape.modifiers:
                if mod.type == 'ARRAY':
                    array = mod

                    break

            if array and array.use_object_offset:

                bc.empty.driver_remove('rotation_euler', 2)
                driver = bc.empty.driver_add('rotation_euler', 2).driver
                driver.type == 'SCRIPTED'

                count = driver.variables.new()
                count.name = 'count'
                count.targets[0].id_type = 'OBJECT'
                count.targets[0].id = bc.shape
                count.targets[0].data_path = F'modifiers["{array.name}"].count'

                driver.expression = 'radians(360 / count)'

            else:
                bpy.data.objects.remove(bc.empty)
                bc.empty = None

        else:
            bpy.data.objects.remove(bc.empty)
            bc.empty = None

    else:
        if bc.original_active:
            bpy.ops.object.mode_set(mode='OBJECT')
            try:
                bpy.context.view_layer.objects.active = bc.original_active
                bc.original_active.select_set(True)

                if op.cancelled:
                    if op.datablock['overrides']:
                        for pair in zip(op.datablock['targets'], op.datablock['overrides']):
                            obj = pair[0]
                            override = pair[1]

                            name = obj.data.name
                            obj.data.name = 'tmp'

                            obj.data = override
                            obj.data.name = name

                            for mod in obj.modifiers:
                                mod.show_viewport = True

                        op.datablock['overrides'] = list()
            except:
                traceback.print_exc()

        for obj in bc.shape.children:
            if obj.data:
                obj.data.bc.removeable = True

            bpy.data.objects.remove(obj)

        bpy.data.objects.remove(bc.shape)
        bpy.data.objects.remove(bc.lattice)

        for obj in op.datablock['slices']:
            bpy.data.objects.remove(obj)

        for obj in op.datablock['targets']:
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN' and not mod.object:

                    obj.modifiers.remove(mod)

        if op.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')

    if bc.shape and op.original_mode == 'EDIT_MESH' and not op.show_shape and op.mode != 'MAKE':
        bc.shape.data.bc.removeable = True
        bpy.data.objects.remove(bc.shape)

    for me in bpy.data.meshes:
        if me.bc.removeable:
            bpy.data.meshes.remove(me)

    for lat in bpy.data.lattices:
        if lat.bc.removeable:
            bpy.data.lattices.remove(lat)

    bc.lattice = None

    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and mod.object == bc.shape and op.mode == 'MAKE':
                obj.modifiers.remove(mod)

            elif mod.type == 'BOOLEAN' and not mod.object:
                obj.modifiers.remove(mod)

        applied_cycle = (obj.bc.shape and obj.bc.shape != bc.shape and obj.bc.applied_cycle)
        if (obj.type == 'MESH' and obj.data.bc.removeable) or applied_cycle:
            bpy.data.objects.remove(obj)

        elif obj.bc.shape and obj.bc.applied_cycle:
            obj.bc.applied = True
            obj.bc.applied_cycle = False

    if op.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

    mesh.set_pivot(op, context)

    if op.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')

    if not all and bc.original_active and bc.original_active.select_get() and preference.behavior.parent_shape and op.mode not in {'KNIFE', 'EXTRACT'}:
        if bc.shape:
            object.parent(bc.shape, bc.original_active)

        for obj in op.datablock['slices']:
            object.parent(obj, bc.original_active)
            obj.matrix_world = bc.original_active.matrix_world

    bc.slice = None
    bc.inset = None
    bc.plane = None
    bc.location = Vector()

    bc.snap.display = True

    for me in bpy.data.meshes:
        if me.users == 0:
            bpy.data.meshes.remove(me)

    if preference.surface != op.last['surface'] and op.last['surface'] != 'WORLD':
        preference.surface = op.last['surface']
    # else: #TODO: Add pref for return to object
        # preference.surface = 'OBJECT'

    if op.behavior == 'DESTRUCTIVE' and op.mode != 'MAKE' and bc.shape and not op.show_shape:
        bpy.data.meshes.remove(bc.shape.data)

    if 'Cutters' in bpy.data.collections and not bc.collection.objects:
        bpy.data.collections.remove(bc.collection)

    if type_to_custom:
        toolbar.change_prop(bpy.context, 'shape_type', 'CUSTOM')

    if op.mode != 'KNIFE':
        toolbar.change_prop(bpy.context, 'mode', op.last['start_mode'] if not type_to_custom else 'CUT')
    elif preference.behavior.hops_mark:
        preference.behavior.hops_mark = False

    if preference.behavior.recut:
        preference.behavior.recut = False

    toolbar.change_prop(bpy.context, 'operation', op.last['start_operation'])

    if not type_to_custom:
        toolbar.change_prop(bpy.context, 'shape_type', op.last['shape_type'])

    preference.behavior['line_box'] = op.last['line_box']

    if not op.datablock['targets'] and op.mode == 'MAKE':
        if bc.shape:
            bc.shape.select_set(False)
        context.view_layer.objects.active = None

    for obj in op.datablock['targets']:
        for mod in obj.modifiers:
            if mod.type == 'MIRROR' and (op.mode == 'KNIFE' or op.original_mode == 'EDIT_MESH'):
                mod.show_viewport = True

    if all:
        context.view_layer.objects.active = bc.original_active

        for obj in op.datablock['targets']:
            obj.select_set(True)

        if op.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')

        if bc.shape and op.shape_type != 'CUSTOM':
            bpy.data.objects.remove(bc.shape)

        if bc.lattice:
            bpy.data.objects.remove(bc.lattice)

    op.datablock['targets'] = []
    op.datablock['slices'] = []
    op.view3d['location'] = Vector((0, 0, 0))

    del op.tool
    bc.original_active = None
    op.original_selected = []
    op.original_visible = []
    op.material = ''
    del op.datablock
    del op.last
    del op.ray
    del op.start
    del op.geo
    del op.mouse
    del op.view3d
    del op.existing

    bc.shape = None if not bc.stored_shape else bc.stored_shape

    custom.clear_sum()

    if op.snap:
        op.snap = False

        bpy.ops.bc.shape_snap('INVOKE_DEFAULT')
