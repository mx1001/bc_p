import bpy
import bmesh

from mathutils import Vector

from ..... utility import addon, mesh
from ..... utility.modifier import apply, sort, new, unmodified_bounds, bevels

sort_types = [
    'ARRAY',
    'MIRROR',
    'BEVEL',
    'SOLIDIFY',
    'DISPLACE',
    'LATTICE',
    'DECIMATE'
    'SCREW',
]

if bpy.app.version[1] >= 82:
    sort_types.insert(1, 'WELD')


def shape_bool(obj):
    bc = bpy.context.scene.bc

    if obj:
        for mod in reversed(obj.modifiers):
            if mod.type == 'BOOLEAN' and mod.object == bc.shape:
                return mod

    return None


def update(op, context, force_edit_mode=True):
    bc = context.scene.bc
    original_active = context.active_object
    slices = op.datablock['slices'] if op.mode != 'INSET' else []
    targets = op.datablock['targets'] + slices

    if not op.datablock['overrides']:
        op.datablock['overrides'] = [obj.data for obj in targets]

    for pair in zip(targets, op.datablock['overrides']):
        obj = pair[0]
        override = pair[1]

        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')

        old_data = obj.data

        if obj.data != override:
            obj.data = override
        else:
            obj.data = obj.data.copy()

        if old_data not in op.datablock['overrides']:
            bpy.data.meshes.remove(old_data)

        new_obj = obj.copy()
        coords = [vert.co for vert in new_obj.data.vertices]

        for mod in new_obj.modifiers:
            if mod.type == 'BOOLEAN':
                if mod.object == bc.shape or mod.object in op.datablock['slices']:
                    new_obj.modifiers.remove(mod)

        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN':
                if mod.object != bc.shape and mod.object not in op.datablock['slices']:
                    obj.modifiers.remove(mod)
            else:
                obj.modifiers.remove(mod)

        obj.data = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))

        for mod in new_obj.modifiers:
            new(obj, mod=mod)

        bpy.data.objects.remove(new_obj)

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        new_verts = []
        for v in bm.verts:
            if v.co not in coords:
                v.select_set(True)
                new_verts.append(v)

        bm.select_flush(True)

        bm.edges.ensure_lookup_table()
        bw = bm.edges.layers.bevel_weight.verify()
        for e in bm.edges:
            if False not in [v in new_verts for v in e.verts]:
                e[bw] = 0

        bm.to_mesh(obj.data)
        bm.free()

    del targets
    # del overrides

    context.view_layer.objects.active = original_active

    if force_edit_mode:
        bpy.ops.object.mode_set(mode='EDIT')


def clean(op, modifier_only=False):
    for obj in op.datablock['targets']:
        if shape_bool(obj):
            obj.modifiers.remove(shape_bool(obj))

    if not modifier_only:
        for obj in op.datablock['slices']:
            bpy.data.meshes.remove(obj.data)

        op.datablock['slices'] = list()


# TODO: move array here
class create:


    def __init__(self, op):
        # op.datablocks['overrides']

        if op.datablock['overrides']:
            slices = op.datablock['slices'] if op.mode != 'INSET' else []
            for pair in zip(op.datablock['targets'] + slices, op.datablock['overrides']):
                obj = pair[0]
                override = pair[1]

                name = obj.data.name
                obj.data.name = 'tmp'

                obj.data = override
                obj.data.name = name

                for mod in obj.modifiers:
                    mod.show_viewport = True

            op.datablock['overrides'] = list()

        self.boolean(op)


    @staticmethod
    def boolean(op, show=False):
        wm = bpy.context.window_manager
        preference = addon.preference()
        bc = bpy.context.scene.bc

        if not op.datablock['targets']:
            return

        if shape_bool(op.datablock['targets'][0]):
            for obj in op.datablock['targets']:
                if shape_bool(obj):
                    obj.modifiers.remove(shape_bool(obj))

            for obj in op.datablock['slices']:
                bpy.data.meshes.remove(obj.data)

            op.datablock['slices'] = []

        bc.shape.display_type = 'WIRE' if op.mode != 'MAKE' else 'TEXTURED'
        bc.shape.hide_set(True)

        for obj in op.datablock['targets']:
            if not op.active_only or obj == bpy.context.view_layer.objects.active:
                mod = obj.modifiers.new(name='Boolean', type='BOOLEAN')
                mod.show_viewport = show
                mod.show_expanded = False
                mod.object = bc.shape
                mod.operation = 'DIFFERENCE' if op.mode not in {'JOIN', 'INTERSECT'} else 'UNION' if op.mode == 'JOIN' else 'INTERSECT'

                if op.mode != 'EXTRACT' or (op.mode == 'EXTRACT' and not preference.behavior.surface_extract):
                    ignore_vgroup = preference.behavior.sort_bevel_ignore_vgroup
                    ignore_verts = preference.behavior.sort_bevel_ignore_only_verts
                    props = {'use_only_vertices': True} if bpy.app.version < (2, 90, 0) else {'affect': 'VERTICES'}
                    bvls = bevels(obj, vertex_group=ignore_vgroup, props=props if ignore_verts else {})
                    sort(obj, option=preference.behavior, ignore=bvls)
                else:
                    sort(obj, sort_types={'WEIGHTED_NORMAL'})

                if op.mode in {'INSET', 'SLICE', 'EXTRACT'}:
                    new = obj.copy()
                    new.data = obj.data.copy()

                    if op.mode in {'SLICE', 'EXTRACT'}:
                        if obj.users_collection:
                            for collection in obj.users_collection:
                                if bpy.context.scene.rigidbody_world and collection == bpy.context.scene.rigidbody_world.collection:
                                    continue

                                collection.objects.link(new)
                        else:
                            bpy.context.scene.collection.objects.link(new)

                        bc.slice = new

                    else:
                        bc.collection.objects.link(new)
                        new.bc.inset = True

                    new.select_set(True)

                    new.name = op.mode.title()
                    new.data.name = op.mode.title()

                    if op.mode in {'SLICE', 'INSET'} and preference.behavior.recut:
                        for mod in new.modifiers:
                            if mod.type == 'BOOLEAN' and mod != shape_bool(new):
                                new.modifiers.remove(mod)

                    if op.mode not in {'SLICE', 'EXTRACT'}:
                        new.hide_set(True)

                    shape_bool(new).operation = 'INTERSECT'

                    if op.mode == 'INSET':
                        for mod in new.modifiers[:]:
                            if mod.type == 'BEVEL':
                                if bpy.app.version < (2, 90, 0):
                                    if mod.use_only_vertices or mod.limit_method == 'VGROUP':
                                        mod.show_viewport = False
                                        mod.show_render = False
                                        continue
                                else:
                                    if mod.affect == 'VERTICES' or mod.limit_method == 'VGROUP':
                                        mod.show_viewport = False
                                        mod.show_render = False
                                        continue

                                new.modifiers.remove(mod)

                        ignore = [mod for mod in new.modifiers if mod.type == 'BEVEL']
                        ignore.append(shape_bool(new))
                        apply(new, ignore=ignore, types={'BOOLEAN'} if op.mode == 'SLICE' else {})

                    if op.mode == 'INSET':
                        new.display_type = 'WIRE'
                        new.hide_render = True
                        # new.data.use_customdata_vertex_bevel = False
                        # new.data.use_customdata_edge_bevel = False
                        # new.data.use_customdata_edge_crease = False

                        if hasattr(new, 'cycles_visibility'):
                            new.cycles_visibility.camera = False
                            new.cycles_visibility.diffuse = False
                            new.cycles_visibility.glossy = False
                            new.cycles_visibility.transmission = False
                            new.cycles_visibility.scatter = False
                            new.cycles_visibility.shadow = False
                            new.cycles.is_shadow_catcher = False
                            new.cycles.is_holdout = False

                        solidify = new.modifiers.new(name='Solidify', type='SOLIDIFY')
                        solidify.thickness = op.last['thickness']
                        solidify.offset = 0
                        solidify.show_on_cage = True
                        solidify.use_even_offset = True
                        solidify.use_quality_normals = True

                        new.modifiers.remove(shape_bool(new))

                        mod = new.modifiers.new(name='Boolean', type='BOOLEAN')
                        mod.show_viewport = show
                        mod.show_expanded = False
                        mod.object = bc.shape
                        mod.operation = 'INTERSECT'

                        for mod in bc.shape.modifiers:
                            if mod.type == 'SOLIDIFY':
                                bc.shape.modifiers.remove(mod)

                        bool = None
                        for mod in reversed(obj.modifiers):
                            if mod.type == 'BOOLEAN' and mod.object == new:
                                bool = mod
                                break

                        if not bool:
                            mod = obj.modifiers.new(name='Boolean', type='BOOLEAN')
                            mod.show_viewport = show
                            mod.show_expanded = False
                            mod.object = new
                            mod.operation = 'DIFFERENCE'

                            if hasattr(wm, 'Hard_Ops_material_options'):
                                new.hops.status = 'BOOLSHAPE'

                            ignore_vgroup = preference.behavior.sort_bevel_ignore_vgroup
                            ignore_verts = preference.behavior.sort_bevel_ignore_only_verts
                            props = {'use_only_vertices': True} if bpy.app.version < (2, 90, 0) else {'affect': 'VERTICES'}
                            bvls = bevels(obj, vertex_group=ignore_vgroup, props=props if ignore_verts else {})
                            sort(obj, option=preference.behavior, ignore=bvls)

                        bc.inset = new

                        for mod in bc.inset.modifiers:
                            if mod.type == 'WEIGHTED_NORMAL':
                                bc.inset.modifiers.remove(mod)

                        original_active = bpy.context.active_object
                        bpy.context.view_layer.objects.active = new
                        bpy.ops.mesh.customdata_custom_splitnormals_clear()
                        bpy.context.view_layer.objects.active = original_active

                    op.datablock['slices'].append(new)

        hops = getattr(wm, 'Hard_Ops_material_options', False)

        if not len(bpy.data.materials[:]):
            hops = False

        if hops and hops.active_material:
            active_material = bpy.data.materials[hops.active_material]

            bc.shape.data.materials.clear()

            if op.mode not in {'SLICE', 'INSET', 'KNIFE', 'EXTRACT'}:
                bc.shape.data.materials.append(active_material)

                if op.mode != 'MAKE':
                    for obj in op.datablock['targets']:
                        mats = [slot.material for slot in obj.material_slots if slot.material]

                        obj.data.materials.clear()

                        for index, mat in enumerate(mats):
                            if not index or (mat != active_material or mat in op.existing[obj]['materials']):
                                obj.data.materials.append(mat)

                        if active_material not in obj.data.materials[:]:
                            obj.data.materials.append(active_material)

            elif op.mode in {'SLICE', 'INSET'}:
                for obj in op.datablock['targets']:
                    mats = [slot.material for slot in obj.material_slots if slot.material]

                    obj.data.materials.clear()

                    for index, mat in enumerate(mats):
                        if not index or (mat != active_material or mat in op.existing[obj]['materials']):
                            obj.data.materials.append(mat)

                    if op.mode == 'INSET' and active_material not in obj.data.materials[:]:
                        obj.data.materials.append(active_material)

                for obj in op.datablock['slices']:
                    if op.mode != 'INSET':
                            obj.data.materials.clear()

                    obj.data.materials.append(active_material)

                    if op.mode == 'INSET':
                        mats = [slot.material for slot in obj.material_slots]
                        index = mats.index(active_material)

                        for mod in obj.modifiers:
                            if mod.type == 'SOLIDIFY':
                                mod.material_offset = index

                                break
