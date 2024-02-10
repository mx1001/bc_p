import bpy
import bmesh

from math import pi, cos, sin, radians, degrees
from mathutils import Vector, Matrix

from . import modifier
from ..... utility import addon, object


def thickness_clamp(context):
    bc = context.scene.bc
    factor = 0.005
    thickness = min(bc.shape.dimensions[:-1]) * factor
    offset = addon.preference().shape.offset

    return thickness if thickness < offset else offset - 0.001


def remove_point(op, context, event, index=-1, fill=True):
    preference = addon.preference()
    bc = context.scene.bc

    bm = bmesh.new()
    bm.from_mesh(bc.shape.data)

    bm.verts.ensure_lookup_table()
    if len(bm.verts) > 2 or index != -1:
        bm.verts.remove(bm.verts[index])

        if fill and len(bm.verts) > 2 and bc.cyclic or preference.behavior.line_box:
            bm.verts.ensure_lookup_table()
            bm.faces.new(bm.verts[:])

    bm.to_mesh(bc.shape.data)
    bm.free()


def add_point(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc

    bm = bmesh.new()
    bm.from_mesh(bc.shape.data)

    if len(bm.verts) > 2:
        if len(bm.faces):
            bm.faces.ensure_lookup_table()
            bm.faces.remove(bm.faces[0])

    if len(bm.edges) == len(bm.verts):
        bm.edges.ensure_lookup_table()
        bm.edges.remove(bm.edges[-1])

    bm.verts.ensure_lookup_table()
    bm.verts.new((0.0, 0.0, 0.0))

    bm.verts.ensure_lookup_table()
    bm.edges.new(bm.verts[-2:])

    if len(bm.verts) > 2 and bc.cyclic or preference.behavior.line_box:
        bm.edges.ensure_lookup_table()
        bm.edges.new([bm.verts[0], bm.verts[-1]])

        bm.faces.ensure_lookup_table()
        bm.faces.new(bm.verts[:])

    bm.to_mesh(bc.shape.data)
    bm.free()


# edge length based on increment snap
# snap to draw dots
# last point snapping
def draw(op, context, event, index=-1):
    bc = context.scene.bc
    preference = addon.preference()

    if preference.keymap.alt_preserve and op.alt and not op.alt_skip:
        return {'PASS_THROUGH'}

    location_x = op.view3d['location'].x

    snap = preference.snap.enable and (preference.snap.incremental or preference.snap.grid)
    snap_lock = snap and preference.snap.increment_lock
    snap_angle_lock = preference.snap.angle_lock

    line_box = preference.behavior.line_box and len(bc.shape.data.vertices) > 3

    if bc.shape.bc.array and bc.shape.bc.array_circle:
        displace = None

        for mod in bc.shape.modifiers:
            if mod.type == 'DISPLACE':
                displace = mod

                break

        if displace:
            location_x = op.view3d['location'].x - displace.strength / 2

    if line_box:
        index -= 1

    point = bc.shape.data.vertices[index]

    if not op.add_point and not op.add_point_lock:
        increment_amount = round(preference.snap.increment, 8) * 10
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        point.co = (location_x, op.view3d['location'].y, point.co.z)

        if line_box:
            point_current = Vector(point.co[:-1])
            origin_point = Vector(bc.shape.data.vertices[0].co[:-1])
            end_point = Vector(bc.shape.data.vertices[1].co[:-1])
            follow_point = Vector(bc.shape.data.vertices[-1].co[:-1])

            edge_angle = (end_point - origin_point).angle_signed(Vector((1, 0)), 0.0)

            delta = point_current - end_point
            angle = delta.angle_signed(Vector((1, 0)), 0.0)

            step = radians(90)

            angle = round((angle - edge_angle)/step) * step + edge_angle

            if abs(round(degrees(angle - edge_angle))) not in {89, 90, 91, 269, 270, 271}:
                angle += radians(90)

            direction = Vector((cos(angle), sin(angle)))

            point_current = end_point + delta.project(direction)

            point.co = Vector((point_current.x, point_current.y, point.co.z))

            edge_angle = (point_current - end_point).angle_signed(Vector((1, 0)), 0.0)

            delta = follow_point - point_current
            angle = delta.angle_signed(Vector((1, 0)), 0.0)

            step = radians(90)

            angle = round((angle - edge_angle)/step) * step + edge_angle
            direction = Vector((cos(angle), sin(angle)))

            follow_point = point_current + delta.project(direction)

            bc.shape.data.vertices[-1].co = Vector((follow_point.x, follow_point.y, point.co.z))

        elif event.ctrl or snap_lock or snap_angle_lock:
            if (snap and event.ctrl) or (snap and snap_lock):
                location_x = round(round(point.co.x * 10 / increment_amount) * increment_amount, increment_length)
                location_x *= 0.1
                location_y = round(round(point.co.y * 10 / increment_amount) * increment_amount, increment_length)
                location_y *= 0.1

                point.co = Vector((location_x, location_y, point.co.z))

            #The minus fixes ngon permasnap so dont remove the minus without a better solution
            elif event.ctrl - snap_angle_lock:
                point1 = Vector(point.co[:-1])
                point2 = Vector(bc.shape.data.vertices[index-1].co[:-1])
                point3 = None
                edge_angle = 0.0

                if len(bc.shape.data.vertices) > 2:
                    point3 = Vector(bc.shape.data.vertices[index-2].co[:-1])
                    edge_angle = (point2 - point3).angle_signed(Vector((1, 0)), 0.0)

                delta = point1 - point2
                angle = delta.angle_signed(Vector((1, 0)), 0.0)

                pref = preference.snap.ngon_angle if not preference.behavior.line_box else preference.snap.line_box_angle
                step = pi*2/(360/pref)

                angle = round((angle - edge_angle)/step)*step + edge_angle
                direction = Vector((cos(angle), sin(angle)))

                point1 = point2 + delta.project(direction)

                point.co = Vector((point1.x, point1.y, point.co.z))

    del point


def offset(op, context, event):
    preference = addon.preference()
    offset = preference.shape.offset

    if not op.modified:
        if op.mode == 'MAKE':
            offset = 0
        elif op.mode == 'JOIN':
            offset = -offset
    else:
        offset = 0

    bc = context.scene.bc
    snap = preference.snap.enable and (preference.snap.incremental or preference.snap.grid)
    snap_lock = snap and preference.snap.increment_lock

    if not op.extruded:
        extrude(op, context, event)

    location_z = op.view3d['location'].z

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.snap.increment, 8)
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
            location_z *= 0.1

        else:
            location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

    if op.view3d['location'].z > op.start['extrude']:
        location = location_z + offset
        matrix = op.start['matrix'] @ Matrix.Translation(Vector((0, 0, location)))
        bc.shape.matrix_world.translation = matrix.translation
        bc.lattice.matrix_world.translation = matrix.translation

        points = [bc.shape.data.vertices[point] for point in op.geo['indices']['extrusion']]

        for point in points:
            point.co.z = -location_z + op.start['extrude']

    else:
        location = op.start['extrude'] + offset
        matrix = op.start['matrix'] @ Matrix.Translation(Vector((0, 0, location)))
        bc.shape.matrix_world.translation = matrix.translation
        bc.lattice.matrix_world.translation = matrix.translation

        points = [bc.shape.data.vertices[point] for point in op.geo['indices']['extrusion']]

        for point in points:
            point.co.z = 0.0


def extrude(op, context, event, extrude_only=True):
    preference = addon.preference()
    bc = context.scene.bc
    snap = preference.snap.enable and (preference.snap.incremental or preference.snap.grid)
    snap_lock = snap and preference.snap.increment_lock
    shape = bc.shape

    if not op.extruded:
        bm = bmesh.new()
        bm.from_mesh(shape.data)

        ret = bmesh.ops.extrude_face_region(bm, geom=bm.edges[:] + bm.faces[:])
        extruded_verts = [ele for ele in ret['geom'] if isinstance(ele, bmesh.types.BMVert)]
        op.geo['indices']['extrusion'] = [vert.index for vert in extruded_verts]
        del ret

        for point in extruded_verts:
            point.co.z = -0.001

        mid_edges = [e for e in bm.edges if (e.verts[0] in extruded_verts and e.verts[1] not in extruded_verts) or (e.verts[1] in extruded_verts and e.verts[0] not in extruded_verts)]
        bot_edges = [e for e in bm.edges if (e.verts[0] in extruded_verts and e.verts[1] in extruded_verts)]

        op.geo['indices']['mid_edge'] = [edge.index for edge in mid_edges]
        op.geo['indices']['bot_edge'] = [edge.index for edge in bot_edges]

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        for f in bm.faces:
            f.smooth = True

        bm.to_mesh(shape.data)
        bm.free()

        shape.data.update()

        op.extruded = True

    if not extrude_only:
        location_z = op.view3d['location'].z

        if snap and event.ctrl or snap_lock:
            increment_amount = round(preference.snap.increment, 8)
            split = str(increment_amount).split('.')[1]
            increment_length = len(split) if int(split) != 0 else 0

            if event.shift:
                location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
                location_z *= 0.1

            else:
                location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

        points = [shape.data.vertices[i] for i in op.geo['indices']['extrusion']]

        for point in points:
            point.co.z = location_z if location_z < 0.0 else -0.001

        shape.data.update()

    if op.shape_type == 'NGON' and preference.behavior.line_box and len(bc.shape.data.vertices) > 2 and preference.shape.wedge:
        for face in bc.shape.data.polygons:
            if 0 in face.vertices[:] and 1 in face.vertices[:]:
                for index in face.vertices[:]:
                    if index in op.geo['indices']['extrusion']:
                        bc.shape.data.vertices[index].co.z = -0.001


def vertex_group(op, context, event, q_only=False):
    bc = context.scene.bc
    shape = bc.shape

    if not (op.shape_type == 'NGON' and not op.extruded):
        if op.shape_type == 'CIRCLE':
            if 'bottom' not in shape.vertex_groups:
                group = shape.vertex_groups.new(name='bottom')
                group.add(index=[1], weight=1.0, type='ADD')

        if not q_only:
            mid_group = None
            for grp in shape.vertex_groups:
                if grp.name[:4] == 'edge':
                    mid_group = grp
                    break

            if not mid_group:
                for index, mid_edge in enumerate(op.geo['indices']['mid_edge']):
                    group = shape.vertex_groups.new(name=F'edge{index + 1}')
                    group.add(index=shape.data.edges[mid_edge].vertices[:], weight=1.0, type='ADD')

        bot_group = None
        for grp in shape.vertex_groups:
            if grp.name == 'bottom':
                bot_group = grp
                break

        if not bot_group and shape.data.bc.q_beveled:
            verts = []
            for index in op.geo['indices']['bot_edge']:
                for vert_index in shape.data.edges[index].vertices:
                    if vert_index not in verts:
                        verts.append(vert_index)

            group = shape.vertex_groups.new(name='bottom')
            group.add(index=verts, weight=1.0, type='ADD')

        elif op.shape_type != 'CIRCLE' and bot_group and not shape.data.bc.q_beveled:
            shape.vertex_groups.remove(shape.vertex_groups['bottom'])


def bevel_weight(op, context, event):
    bc = context.scene.bc
    preference = addon.preference()
    shape = bc.shape

    if not (op.shape_type == 'NGON' and not op.extruded):
        if op.shape_type == 'CIRCLE':
            vertex_group(op, context, event, q_only=True)

        else:
            shape.data.use_customdata_edge_bevel = True

            for index in op.geo['indices']['mid_edge']:
                edge = shape.data.edges[index]
                edge.bevel_weight = 1

            if preference.shape.quad_bevel:
                vertex_group(op, context, event, q_only=True)

            elif shape.data.bc.q_beveled:
                for index in op.geo['indices']['bot_edge']:
                    edge = shape.data.edges[index]
                    edge.bevel_weight = 1

            elif not shape.data.bc.q_beveled:
                for index in op.geo['indices']['bot_edge']:
                    edge = shape.data.edges[index]
                    edge.bevel_weight = 0

#             shape.data.validate()


def knife(op, context, event):
    bc = context.scene.bc

    targets = op.datablock['targets']
    overrides = op.datablock['overrides']

    original_active = context.active_object
    original_selected = context.selected_objects[:]

    dimension_z = bc.shape.dimensions[2]
    lazorcut_limit = addon.preference().shape.lazorcut_limit
    too_thin = dimension_z < lazorcut_limit and not op.extruded
    aligned = not op.extruded and op.align_to_view

    if (not op.extruded or too_thin or aligned) and not op.lazorcut_performed:
        return

    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in original_selected:
        obj.select_set(False)

    if not overrides:
        overrides = op.datablock['overrides'] = [obj.data for obj in targets]

    for pair in zip(targets, overrides):
        obj = pair[0]
        override = pair[1]
        original_auto_smooth = float(obj.data.auto_smooth_angle)
        bm = bmesh.new()
        bm.from_object(bc.shape, bpy.context.evaluated_depsgraph_get())

        shape_matrix = bc.shape.matrix_world.copy()
        obj_matrix = obj.matrix_world.copy()
        shape_matrix.translation -= obj_matrix.translation
        obj_matrix.translation = Vector((0, 0, 0))

        shape_vert_indices = list()

        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            v.tag = True
            v.select_set(True)
            v.co = bc.shape.matrix_world @ v.co
            shape_vert_indices.append(v.index)

        ret = bmesh.ops.bisect_edges(bm, edges=bm.edges[:], cuts=1)

        for ele in ret['geom_split']:
            if isinstance(ele, bmesh.types.BMVert):
                ele.select_set(True)
                shape_vert_indices.append(ele.index)

        bm.select_flush(True)

        bm.from_mesh(override)

        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            if not v.tag:
                v.select_set(False)
                v.co = obj.matrix_world @ v.co

        bm.select_flush(False)

        dat = bpy.data.meshes.new(name='bc-temporary-knife')
        new = bpy.data.objects.new(name='bc-temporary-knife', object_data=dat)
        new.data.use_auto_smooth = True
        new.data.auto_smooth_angle = original_auto_smooth

        bm.to_mesh(dat)
        bm.free()

        bc.collection.objects.link(new)

        bpy.context.view_layer.objects.active = new
        new.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT')
        original_selection_mode = tuple(bpy.context.tool_settings.mesh_select_mode)
        bpy.context.scene.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.intersect() # TODO: use bmesh edgenet

        if addon.hops() and addon.preference().behavior.hops_mark:
            bpy.context.scene.tool_settings.mesh_select_mode = (False, True, False)
            bpy.ops.object.mode_set(mode='OBJECT')

            pref = addon.hops().property

            for edge in new.data.edges:
                # if edge.index in shape_edge_indices:
                if not edge.select:
                    continue

                edge.crease = float(pref.sharp_use_crease)
                edge.use_seam = float(pref.sharp_use_seam)
                edge.bevel_weight = float(pref.sharp_use_bweight)
                edge.use_edge_sharp = float(pref.sharp_use_sharp)

            bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.loop_to_region(select_bigger=op.flip) # can use bmesh for this
        bpy.context.scene.tool_settings.mesh_select_mode = original_selection_mode
        bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(new.data)

        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[index] for index in shape_vert_indices], context='VERTS')
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)

        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            if not v.tag:
                v.co = obj.matrix_world.inverted() @ v.co

        bm.to_mesh(new.data)
        bm.free()

        original_name = obj.data.name
        original_data = obj.data
        obj.data.name = 'tmp'

        mats = [slot.material for slot in obj.material_slots]

        obj.data = new.data

        for mat in mats:
            obj.data.materials.append(mat)

        obj.data.name = original_name

        if original_data not in overrides:
            bpy.data.meshes.remove(original_data)

        bpy.data.objects.remove(new)

    del targets
    del overrides

    bpy.context.view_layer.objects.active = original_active
    original_active.select_set(True)

    del original_active

    for obj in original_selected:
        obj.select_set(True)

    del original_selected

    if op.original_mode == 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')


def inset(op, context, event):
    pass


def set_pivot(op, context):
    bc = context.scene.bc
    preference = addon.preference()

    if bc.shape and not bc.shape.bc.array_circle:
        if preference.behavior.set_origin == 'MOUSE':
            if op.mode not in {'MAKE', 'JOIN'}:
                return
            local_location = bc.shape.matrix_world.inverted() @ op.ray['location']
            global_location = op.ray['location']

        elif preference.behavior.set_origin == 'CENTER':
            bounds = [bc.shape.bound_box[i] for i in (1, 2, 5, 6)]
            local_location = 0.25 * sum((Vector(b) for b in bounds), Vector())
            global_location = bc.shape.matrix_world @ local_location

        elif preference.behavior.set_origin == 'BBOX':
            local_location = 0.125 * sum((Vector(b) for b in bc.shape.bound_box), Vector())
            global_location = bc.shape.matrix_world @ local_location

        elif preference.behavior.set_origin == 'ACTIVE':
            local_location = bc.shape.matrix_world.inverted() @ bc.original_active.location
            global_location = bc.original_active.location

        bc.shape.location = global_location
        bc.shape.data.transform(Matrix.Translation(-local_location))

        return local_location

    elif bc.shape and bc.shape.bc.array_circle and preference.shape.array_around_cursor:
        cursor_location = context.scene.cursor.location
        local_location = bc.shape.matrix_world.inverted() @ cursor_location
        global_location = cursor_location

        bc.shape.location = global_location
        bc.shape.data.transform(Matrix.Translation(-local_location))

        return local_location

    return Vector()


class create:

    @staticmethod
    def shape(op, context, event):
        preference = addon.preference()
        bc = context.scene.bc

        verts = [
            Vector((-0.5, -0.5, 0.0)), Vector(( 0.5, -0.5, 0.0)),
            Vector((-0.5,  0.5, 0.0)), Vector(( 0.5,  0.5, 0.0))]

        edges = [
            (0, 2), (0, 1),
            (1, 3), (2, 3)]

        faces = [(0, 1, 3, 2)]

        dat = bpy.data.meshes.new(name='Plane')
        dat.bc.removeable = True

        dat.from_pydata(verts, edges, faces)
        dat.validate()

        op.datablock['plane'] = bpy.data.objects.new(name='Plane', object_data=dat)
        bc.plane = op.datablock['plane']

        del dat

        if op.shape_type == 'BOX':
            verts = [
                Vector((-0.5, -0.5, -0.5)), Vector((-0.5, -0.5,  0.5)),
                Vector((-0.5,  0.5, -0.5)), Vector((-0.5,  0.5,  0.5)),
                Vector(( 0.5, -0.5, -0.5)), Vector(( 0.5, -0.5,  0.5)),
                Vector(( 0.5,  0.5, -0.5)), Vector(( 0.5,  0.5,  0.5))]

            edges = [
                (0, 2), (0, 1), (1, 3), (2, 3),
                (2, 6), (3, 7), (6, 7), (4, 6),
                (5, 7), (4, 5), (0, 4), (1, 5)]

            faces = [
                (0, 1, 3, 2), (2, 3, 7, 6),
                (6, 7, 5, 4), (4, 5, 1, 0),
                (2, 6, 4, 0), (7, 3, 1, 5)]

            op.geo['indices']['top_edge'] = [0, 4, 7, 10]
            op.geo['indices']['mid_edge'] = [1, 3, 6, 9]
            op.geo['indices']['bot_edge'] = [2, 5, 8, 11]

        elif op.shape_type == 'CIRCLE':
            verts = [
                Vector((0.0, -0.5, -0.5)), Vector((0.0, -0.5,  0.5)),
                Vector((0.0,  0.0, -0.5)), Vector((0.0,  0.0,  0.5))]

            edges = [(0, 2), (0, 1), (1, 3)]

            faces = []

            op.geo['indices']['top_edge'] = [0]
            op.geo['indices']['mid_edge'] = [1]
            op.geo['indices']['bot_edge'] = [2]


        elif op.shape_type == 'NGON':
            verts = [Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.0))]

            edges = [(0, 1)]

            faces = []

            op.geo['indices']['top_edge'] = [0]
            op.geo['indices']['mid_edge'] = []
            op.geo['indices']['bot_edge'] = []

        dat = bpy.data.meshes.new(name='Cutter')

        dat.from_pydata(verts, edges, faces)

        if op.shape_type == 'CIRCLE' and bc.snap.hit:
            dat.transform(Matrix.Rotation(radians(0.002), 4, Vector((0, 0, 1))))

        dat.validate()

        bc.shape = bpy.data.objects.new(name='Cutter', object_data=dat)
        bc.shape.bc.array_axis = preference.shape.array_axis

        del dat

        bc.shape.bc.shape = True

        bc.collection.objects.link(bc.shape)
        bc.shape.hide_render = True

        if op.mode != 'MAKE':
            bc.shape.display_type = 'WIRE'

            if hasattr(bc.shape, 'cycles_visibility'):
                bc.shape.cycles_visibility.camera = False
                bc.shape.cycles_visibility.diffuse = False
                bc.shape.cycles_visibility.glossy = False
                bc.shape.cycles_visibility.transmission = False
                bc.shape.cycles_visibility.scatter = False
                bc.shape.cycles_visibility.shadow = False

        if addon.preference().behavior.auto_smooth:
            bc.shape.data.use_auto_smooth = True

            for face in bc.shape.data.polygons:
                face.use_smooth = True

        if op.shape_type == 'CIRCLE':
            mod = bc.shape.modifiers.new(name='Screw', type='SCREW')
            mod.steps = preference.shape.circle_vertices
            mod.render_steps = mod.steps
            mod.use_normal_calculate = True
            mod.use_normal_flip = True
            mod.use_smooth_shade = True
            mod.use_merge_vertices = True
            mod.merge_threshold = 0.0000001

            mod = bc.shape.modifiers.new(name='Decimate', type='DECIMATE')
            mod.decimate_type = 'DISSOLVE'
            mod.angle_limit = radians(1)
            mod.use_dissolve_boundaries = True

        if addon.preference().behavior.cutter_uv:
            bc.shape.data.uv_layers.new(name='UVMap', do_init=True)

        bc.shape.data.use_customdata_vertex_bevel = True
        bc.shape.data.use_customdata_edge_bevel = True
        bc.shape.data.use_customdata_edge_crease = True

        if bpy.app.version[1] >= 82:
            bc.shape.modifiers.new(name='Weld', type='WELD')
