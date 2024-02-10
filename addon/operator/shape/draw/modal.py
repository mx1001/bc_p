import bpy

from mathutils import Vector, Matrix

from ..... utility import addon, modifier, view3d, context_copy
from .. import utility
from .. utility import tracked_states, shader
from .... import toolbar


def method(op, context, event):
    preference = addon.preference()
    # bc = context.scene.bc
    bc = context.scene.bc

    bc.snap.display = op.operation == 'DRAW'

    option = op.tool.operator_properties('bc.shape_draw')
    # option = toolbar.options()

    if option.mode != op.mode:
        utility.modal.mode.change(op, context, event, to=option.mode)

    if option.operation != op.operation:
        utility.modal.operation.change(op, context, event, to=option.operation)

    if option.behavior != op.behavior:
        utility.modal.behavior.change(op, context, to=option.behavior)

    # if option.axis != bc.axis:
    #     utility.modal.axis.change(op, context, to=option.axis)

    if option.origin != op.origin:
        utility.modal.origin.change(op, context, event, to=option.origin)

    op.alt = event.alt
    op.ctrl = event.ctrl
    op.shift = event.shift

    op.mouse['location'] = Vector((event.mouse_region_x, event.mouse_region_y))

    op.show_shape = True if preference.behavior.show_shape else event.shift

    op.use_cursor_depth = event.alt

    # TODO: when operation is updated from the topbar wait for lmb press before modal update
    pass_through = False

    tool_region = [region for region in context.area.regions if region.type == 'TOOL_HEADER'][0]

    within_region_tool_header = False
    within_region_tool_header_x = event.mouse_region_x > 0 and event.mouse_region_x < tool_region.width

    if context.space_data.show_region_tool_header:
        if tool_region.alignment == 'TOP':
            within_region_tool_header = within_region_tool_header_x and event.mouse_region_y > context.region.height and event.mouse_region_y < context.region.height + tool_region.height
        else:
            within_region_tool_header = within_region_tool_header_x and event.mouse_region_y > 0 - tool_region.height and event.mouse_region_y < 0

    within_region_3d_x = event.mouse_region_x > 0 and event.mouse_region_x < context.region.width
    within_region_3d = within_region_3d_x and event.mouse_region_y > 0 and event.mouse_region_y < context.region.height

    if within_region_3d:
        op.bounds = modifier.unmodified_bounds(bc.shape, exclude={'LATTICE', 'SCREW', 'SOLIDIFY', 'DISPLACE'})
        bc.empty.matrix_parent_inverse = Matrix()

        # MOUSEMOVE
        if event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            op.mmb = False

        if event.type == 'MOUSEMOVE' and op.add_point and op.operation == 'DRAW':
            within_x = op.last['placed_mouse'].x - 0.5 < op.mouse['location'].x and op.last['placed_mouse'].x + 0.5 > op.mouse['location'].x
            within_y = op.last['placed_mouse'].y - 0.5 < op.mouse['location'].y and op.last['placed_mouse'].y + 0.5 > op.mouse['location'].y

            if not within_x and not within_y:
                utility.mesh.add_point(op, context, event)

                if preference.behavior.line_box:
                    utility.mesh.add_point(op, context, event)

                op.add_point = False

            pass_through = True

        elif op.operation != 'DRAW':
            op.add_point = False

        # LEFTMOUSE
        if event.type == 'LEFTMOUSE':
            if preference.keymap.alt_preserve and op.alt and not op.alt_skip:
                return {'PASS_THROUGH'}

            widget = ''

            if event.value == 'PRESS':
                op.lmb = True
                op.alt_skip = True

                if tracked_states.widgets and tracked_states.widgets.active:
                   widget = tracked_states.widgets.active

            if event.value == 'RELEASE':
                op.lmb = False
                op.allow_menu = False
                op.alt_skip = False

            if not widget:
                if event.value == 'RELEASE':

                    if preference.keymap.quick_execute:
                        quick_execute = op.operation == 'DRAW' and not op.modified and not op.shape_type == 'NGON'
                    else:
                        quick_execute = False

                    execute_in_none = op.operation == 'NONE' and op.modified
                    execute_in_extrude = op.operation in {'EXTRUDE', 'OFFSET'} and not op.modified
                    op.lazorcut = bc.shape.dimensions[2] < preference.shape.lazorcut_limit

                    extrude_if_unmodified = op.operation == 'DRAW' and not op.modified and op.shape_type != 'NGON' and not op.release_lock

                    # overlap = False
                    extrude_if_overlap = False
                    add_point = False

                    if op.shape_type == 'NGON':
                        # matrix = bc.shape.matrix_world
                        # enough_verts = len(bc.shape.data.vertices) > 1
                        extrude_if_overlap = op.operation == 'DRAW' and not op.modified and op.add_point
                        add_point = op.shape_type == 'NGON' and op.operation == 'DRAW' and not op.add_point

                    op.alt_lock = op.rmb
                    if not op.alt_lock:
                        if (quick_execute or execute_in_none or execute_in_extrude or (op.lazorcut and execute_in_none)) and not op.modified_lock:
                            if (quick_execute and not op.release_lock) and op.mode not in {'KNIFE', 'MAKE'}:
                                utility.modifier.create.boolean(op, show=True)

                            if (op.lazorcut_performed and preference.keymap.release_lock_lazorcut) or not preference.keymap.release_lock_lazorcut or (event.ctrl and op.release_lock) or not op.lazorcut or (op.mode == 'KNIFE' and preference.surface == 'VIEW'):
                                op.execute(context)

                                op.update()
                                return {'FINISHED'}

                            elif op.lazorcut and (preference.keymap.release_lock_lazorcut or (preference.keymap.release_lock and preference.keymap.quick_execute)):
                                utility.lazorcut(op, context)

                                if op.mode == 'KNIFE' and preference.surface != 'VIEW':
                                    # context.view_layer.update()
                                    # op.lazorcut_performed = True
                                    op.extruded = True
                                    utility.mesh.knife(op, bpy.context, None)

                                if not preference.keymap.quick_execute:
                                    utility.modal.operation.change(op, context, event, to='NONE')

                        elif op.modified and not add_point or op.release_lock and op.shape_type != 'NGON':
                            op.last['operation'] = op.operation
                            utility.modal.operation.change(op, context, event, to='NONE')

                        elif extrude_if_unmodified or extrude_if_overlap or (op.add_point_lock or (preference.behavior.line_box and len(bc.shape.data.vertices) > 2)):
                            op.last['mouse'] = op.mouse['location']
                            extrude = op.mode not in {'MAKE', 'JOIN'}
                            to = 'EXTRUDE' if extrude else 'OFFSET'

                            if op.shape_type == 'NGON' and op.release_lock:
                                to = 'NONE'

                            utility.modal.operation.change(op, context, event, to=to, modified=to == 'NONE')
                            op.lazorcut_performed = False

                        elif add_point and not op.add_point_lock:
                            op.add_point = True
                            op.last['placed_mouse'] = op.mouse['location']

            elif widget and op.operation != tracked_states.widgets.active and not event.ctrl:
                op.lazorcut_performed = False

                if (widget == 'OFFSET' or widget == 'EXTRUDE' and bc.shape.dimensions[2] < preference.shape.lazorcut_limit) and event.shift and not op.move_lock:
                    bounds = [bc.shape.bound_box[i] for i in (1, 2, 5, 6)]
                    op.view3d['location'] = (0.25 * sum((Vector(b) for b in bounds), Vector()))

                    # utility.modal.move.invoke(op, context, event)
                    utility.modal.operation.change(op, context, event, to='MOVE')

                    op.move_lock = True
                elif not event.shift:
                    utility.modal.operation.change(op, context, event, to=tracked_states.widgets.active, dot=True)

            op.update()
            return {'RUNNING_MODAL'}

        # RIGHTMOUSE | BACKSPACE
        elif event.type == 'RIGHTMOUSE' or event.type == 'BACK_SPACE':

            if preference.keymap.rmb_preserve:
                return {'PASS_THROUGH'}

            removing_points = False
            if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
                op.rmb = True

            if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
                op.rmb = False
                op.allow_menu = False

            if event.value == 'RELEASE':
                op.modified = True

                if op.add_point_lock:
                    utility.modal.operation.change(op, context, event, to='DRAW')

                ngon = op.shape_type == 'NGON' and op.operation == 'DRAW'
                rmb_cancel = preference.keymap.rmb_cancel_ngon
                # last_count = 0

                if op.alt_lock or (not rmb_cancel and event.type == 'RIGHTMOUSE' and ngon and len(bc.shape.data.vertices) == 2) or (rmb_cancel and event.type == 'RIGHTMOUSE' and ngon):
                    op.cancel(context)

                    op.update()
                    return {'CANCELLED'}
                    # return {'RUNNING_MODAL'}

                elif ngon:
                    if event.type != 'RIGHTMOUSE' or (event.type == 'RIGHTMOUSE' and not rmb_cancel):
                        if not op.add_point and not op.add_point_lock:
                            op.add_point_lock = True
                            op.add_point = True

                            utility.modal.operation.change(op, context, event, to='NONE')

                        elif op.add_point_lock:
                            op.add_point_lock = False

                        if op.add_point and not preference.behavior.line_box:
                            utility.mesh.remove_point(op, context, event)
                            removing_points = True

                    # elif event.type == 'RIGHTMOUSE':
                        # utility.modal.operation.change(op, context, event, to='NONE')

                elif op.operation != 'NONE':
                    utility.modal.operation.change(op, context, event, to='NONE', clear_mods=[op.last['operation']] if op.last['operation'] in {'ARRAY', 'SOLIDIFY', 'BEVEL'} else [], modified=op.modified)

                op.alt_lock = True if op.lmb else False

                if not removing_points and not op.alt_lock and (op.operation == 'NONE' and not op.allow_menu or not op.modified):
                    op.cancel(context)

                    op.update()
                    return {'CANCELLED'}

            op.update()
            return {'RUNNING_MODAL'}

        # MIDDLEMOUSE
        elif event.type == 'MIDDLEMOUSE':
            op.mmb = True # set False on mouse move release
            op.update()
            return {'PASS_THROUGH'}

        # WHEELUPMOUSE, EQUAL
        elif event.type in {'WHEELUPMOUSE', 'EQUAL'}:
            if event.type == 'WHEELUPMOUSE' or event.value == 'PRESS':
                if preference.keymap.scroll_adjust_circle and op.shape_type == 'CIRCLE' and op.operation not in {'BEVEL', 'ARRAY'}:
                    preference.shape.circle_vertices += 1
                    op.report({'INFO'}, F'Circle Vertices: {preference.shape.circle_vertices}')

                elif op.operation == 'BEVEL':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'BEVEL':
                            mod.segments += 1
                            preference.shape.bevel_segments = mod.segments
                            op.report({'INFO'}, F'Bevel Segments: {preference.shape.bevel_segments}')

                            break

                elif op.operation == 'ARRAY':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'ARRAY':
                            mod.count += 1
                            # op.last['modifier']['count'] = mod.count
                            preference.shape.array_count = mod.count
                            op.report({'INFO'}, F'Array Count: {preference.shape.array_count}')

                            break

                elif event.alt:
                    utility.custom.cutter(op, context)

                else:
                    op.update()
                    return {'PASS_THROUGH'}

            else:
                op.update()
                return {'PASS_THROUGH'}

        # WHEELDOWNMOUSE, MINUS
        elif event.type in {'WHEELDOWNMOUSE', 'MINUS'}:
            if event.type == 'WHEELDOWNMOUSE' or event.value == 'PRESS':
                if preference.keymap.scroll_adjust_circle and op.shape_type == 'CIRCLE' and op.operation not in {'BEVEL', 'ARRAY'}:
                    if preference.shape.circle_vertices > 3:
                        preference.shape.circle_vertices -= 1
                        op.report({'INFO'}, F'Circle Vertices: {preference.shape.circle_vertices}')

                elif op.operation == 'BEVEL':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'BEVEL':
                            mod.segments -= 1
                            preference.shape.bevel_segments = mod.segments
                            op.report({'INFO'}, F'Bevel Segments: {preference.shape.bevel_segments}')

                            break

                elif op.operation == 'ARRAY':
                    for mod in bc.shape.modifiers:
                        if mod.type == 'ARRAY':
                            mod.count -= 1
                            preference.shape.array_count = mod.count
                            op.report({'INFO'}, F'Array Count: {preference.shape.array_count}')

                            break

                elif event.alt:
                    utility.custom.cutter(op, context, index=-1)

                else:
                    op.update()
                    return {'PASS_THROUGH'}
            else:
                op.update()
                return {'PASS_THROUGH'}

        # elif 'CTRL' in event.type:
        #     if event.value == 'PRESS':
        #         op.widgets.exit = True

        #     elif event.value == 'RELEASE':
        #         op.widgets = shader.widgets.setup(op)

        # ESC
        elif event.type == 'ESC':
            if event.value == 'RELEASE':
                op.allow_menu = False

                ngon = op.shape_type == 'NGON' and op.operation == 'DRAW' and not op.add_point
                if op.operation == 'NONE' and not op.allow_menu or (not op.modified and (not ngon or preference.behavior.line_box)):
                    op.cancel(context)
                    op.update()
                    return {'CANCELLED'}
                elif op.operation != 'NONE':
                    remove = [op.operation] if op.operation in {'ARRAY', 'SOLIDIFY', 'BEVEL'} else []

                    if op.operation == 'ARRAY':

                        if bc.shape.bc.array_circle:
                            bc.shape.bc.array_circle = False

                        remove.append('DISPLACE')

                    utility.modal.operation.change(op, context, event, to='NONE', clear_mods=remove)

        # RET
        elif event.type in {'RET', 'SPACE'}:
            op.execute(context)

            op.update()
            return {'FINISHED'}

        # ACCENT GRAVE / TILDE
        elif event.type == 'ACCENT_GRAVE':
            if event.value == 'RELEASE':
                op.allow_menu = op.operation == 'NONE'

                if event.shift or not preference.keymap.view_pie:
                    utility.modal.rotate.by_90(op, context, event)
                elif op.allow_menu:
                    bpy.ops.wm.call_menu_pie(name='VIEW3D_MT_view_pie')

        # TAB
        elif event.type == 'TAB':
            if event.value == 'RELEASE':
                op.modified = True
                utility.modal.operation.change(op, context, event, to='NONE', modified=op.modified)

        # .
        elif event.type == 'PERIOD' and op.shape_type != 'NGON':
            if event.value == 'RELEASE':
                utility.modal.origin.change(op, context, event, to='CENTER' if op.origin == 'CORNER' else 'CORNER')

        # 1, 2, 3
        elif event.type in {'ONE', 'TWO', 'THREE'}:
            if event.value == 'RELEASE':
                axis = {
                    'ONE': 'X',
                    'NUMPAD_1': 'X',
                    'TWO': 'Y',
                    'NUMPAD_2': 'Y',
                    'THREE': 'Z',
                    'NUMPAD_3': 'Z'}

                if op.operation != 'SOLIDIFY':

                    if not op.mirrored:
                        for i in range(3):
                            bc.mirror_axis[i] = 0
                            bc.mirror_axis_flip[i] = 0

                        op.mirrored = True

                    utility.modal.mirror.shape(op, context, event, to=axis[event.type], flip=event.shift)
                else:
                    for mod in bc.shape.modifiers:
                        if mod.type == 'SOLIDIFY':
                            mod.offset = -1 if event.type == 'ONE' else 1
                            mod.offset = 0 if event.type == 'TWO' else mod.offset

        # A
        elif event.type == 'A':
            if event.value == 'RELEASE':
                utility.modal.mode.change(op, context, event, to='MAKE')

        # B
        elif event.type == 'B':
            if event.value == 'RELEASE':
                op.last['mouse'] = op.mouse['location']
                bc.shape.data.bc.q_beveled = bc.q_bevel
                utility.modal.operation.change(op, context, event, to='BEVEL', clear_mods=[] if op.operation != 'BEVEL' else ['BEVEL'], modified=True)

        # C
        elif event.type == 'C':
            if event.value == 'RELEASE':
                if op.shape_type == 'NGON' and op.operation == 'DRAW' and not preference.behavior.line_box:
                    bc.cyclic = not bc.cyclic

                    if len(bc.shape.data.vertices) > 2:
                        utility.mesh.remove_point(op, context, event)
                        utility.mesh.add_point(op, context, event)

                    op.report({'INFO'}, F'{"En" if bc.cyclic else "Dis"}abled Cyclic')

                elif op.shape_type != 'NGON' or preference.behavior.line_box:
                    utility.custom.cutter(op, context, index=1)

        # D
        elif event.type == 'D':
            # if event.value == 'RELEASE':
            op.allow_menu = op.operation == 'NONE'

            if op.allow_menu and not event.shift and not event.alt:
                op.update()
                return {'PASS_THROUGH'}

            elif event.alt and event.value == 'RELEASE':
                preference.display.dots = not preference.display.dots
                # widgets.exit = True

                # if preference.display.dots:
                #     widgets = shader.widgets.setup(op)

                # utility.modal.dots.collect(op)

                # if preference.display.dots:
                #     op.dots = shader.widgets.setup(op, context)

                op.report({'INFO'}, F'{"En" if preference.display.dots else "Dis"}abled Dots')

        # E
        elif event.type == 'E':
            if event.value == 'RELEASE':
                mode = 'OFFSET' if op.operation == 'EXTRUDE' else 'EXTRUDE'
                utility.modal.operation.change(op, context, event, to=mode)

        # F
        elif event.type == 'F':
            if event.shift and op.shape_type != 'NGON':
                if event.value == 'RELEASE':
                    utility.modal.flip.shape(op, context, event)
                    op.flip_z = not op.flip_z

            elif event.value == 'RELEASE':
                bc.flip = not bc.flip

                if op.operation == 'EXTRUDE':
                    utility.modal.operation.change(op, context, event, to='OFFSET')

                elif op.operation == 'OFFSET':
                    utility.modal.operation.change(op, context, event, to='EXTRUDE')

        # G
        elif event.type == 'G':
            if event.value == 'RELEASE':
                # utility.modal.move.invoke(op, context, event)
                utility.modal.operation.change(op, context, event, to='MOVE')

        # H
        elif event.type == 'H':
            if event.value == 'RELEASE':
                preference.display.wire_only = not preference.display.wire_only

        # I
        elif event.type == 'I':
            if event.value == 'RELEASE':
                utility.modal.mode.change(op, context, event, to='INSET')

        # O
        elif event.type == 'O':
            if event.value == 'RELEASE':
                utility.modal.operation.change(op, context, event, to='OFFSET')

        # J
        elif event.type == 'J':
            if event.value == 'RELEASE':
                utility.modal.mode.change(op, context, event, to='JOIN')

        # K
        elif event.type == 'K':
            if event.value == 'RELEASE':
                if addon.hops() and op.mode == 'KNIFE' and (event.shift or event.alt):
                    preference.behavior.hops_mark = not preference.behavior.hops_mark
                    op.report({'INFO'}, F'{"En" if preference.behavior.hops_mark else "Dis"}abled HOps Marking')
                else:
                    utility.modal.mode.change(op, context, event, to='KNIFE')

        # L
        elif event.type == 'L':
            if event.value == 'RELEASE':
                preference.behavior.show_shape = not preference.behavior.show_shape
                preference.behavior.autohide_shapes = not preference.behavior.show_shape
                op.report({'INFO'}, F'Shape is{"nt" if not preference.behavior.show_shape else ""} live')

        # M TODO: object material link type (obj.material_slots[i].link)
        elif event.type == 'M':
            if event.value == 'RELEASE' and op.mode in {'CUT', 'SLICE', 'INSET'}:
                wm = context.window_manager
                hops = wm.Hard_Ops_material_options if hasattr(wm, 'Hard_Ops_material_options') else False

                if not len(bpy.data.materials[:]):
                    hops = False

                if hops and bpy.data.materials[:]:
                    if not hops.active_material:
                        hops.active_material = bpy.data.materials[0].name

                    active_material = bpy.data.materials[hops.active_material]
                    active_index = bpy.data.materials[:].index(active_material)

                    hops.active_material = bpy.data.materials[active_index - 1].name

                    if hops.active_material != active_material.name:
                        bc.shape.data.materials.clear()

                        if op.mode not in {'SLICE', 'INSET', 'KNIFE', 'EXTRACT'}:
                            bc.shape.data.materials.append(bpy.data.materials[hops.active_material])

                            if op.mode != 'MAKE':
                                for obj in op.datablock['targets']:
                                    mats = [slot.material for slot in obj.material_slots if slot.material]

                                    obj.data.materials.clear()

                                    for index, mat in enumerate(mats):
                                        if not index or (mat != active_material or mat in op.existing[obj]['materials']):
                                            obj.data.materials.append(mat)

                                    if bpy.data.materials[hops.active_material] not in obj.data.materials[:]:
                                        obj.data.materials.append(bpy.data.materials[hops.active_material])

                        elif op.mode in {'SLICE', 'INSET'}:
                            for obj in op.datablock['targets']:
                                mats = [slot.material for slot in obj.material_slots if slot.material]

                                obj.data.materials.clear()

                                for index, mat in enumerate(mats):
                                    if not index or (mat != active_material or mat in op.existing[obj]['materials']):
                                        obj.data.materials.append(mat)

                                if op.mode == 'INSET' and bpy.data.materials[hops.active_material] not in obj.data.materials[:]:
                                    obj.data.materials.append(bpy.data.materials[hops.active_material])

                            for obj in op.datablock['slices']:
                                if op.mode != 'INSET':
                                    obj.data.materials.clear()
                                obj.data.materials.append(bpy.data.materials[hops.active_material])

                                if op.mode == 'INSET':
                                    mats = [slot.material for slot in obj.material_slots]
                                    index = mats.index(bpy.data.materials[hops.active_material])

                                    for mod in obj.modifiers:
                                        if mod.type == 'SOLIDIFY':
                                            mod.material_offset = index

                                            break

        # Q
        elif event.type == 'Q':
            if event.value == 'RELEASE' and op.operation == 'BEVEL':
                bc.q_bevel = not bc.q_bevel
                bc.shape.data.bc.q_beveled = bc.q_bevel

                for mod in bc.shape.modifiers:
                    if mod.type == 'BEVEL':
                        preference.shape.bevel_segments = mod.segments
                        bc.shape.modifiers.remove(mod)

                utility.modal.bevel.shape(op, context, event)

        # R
        elif event.type == 'R':
            if event.value == 'RELEASE':
                if event.shift:
                    if op.operation not in {'NONE', 'DRAW', 'EXTRUDE', 'OFFSET'}:
                        op.last['thickness'] = -0.1
                        op.last['angle'] = 0.0
                        op.last['modifier']['thickness'] = -0.01
                        op.last['modifier']['offset'] = 0.01
                        op.last['modifier']['count'] = 2
                        op.last['modifier']['segments'] = 6
                        op.last['modifier']['width'] = 0.02
                    else:
                        utility.modal.rotate.by_90(op, context, event)
                else:
                    # utility.modal.rotate.invoke(op, context, event)
                    utility.modal.operation.change(op, context, event, to='ROTATE')

        # S
        elif event.type == 'S':
            if event.value == 'RELEASE':
                # utility.modal.scale.invoke(op, context, event)
                utility.modal.operation.change(op, context, event, to='SCALE')

        # T
        elif event.type == 'T':
            if event.value == 'RELEASE':
                utility.modal.operation.change(op, context, event, to='SOLIDIFY', clear_mods=[] if op.operation != 'SOLIDIFY' else ['SOLIDIFY'])

        # V
        elif event.type == 'V':
            if event.value == 'RELEASE':
                to = 'ARRAY'
                remove = [] if op.operation != 'ARRAY' else ['ARRAY']

                if bc.shape.bc.array_circle:
                    bc.shape.bc.array_circle = False
                    to = 'NONE'
                    remove.append('DISPLACE')

                utility.modal.operation.change(op, context, event, to=to, clear_mods=remove)

        # W
        elif event.type == 'W':
            if event.value == 'RELEASE':
                if op.shape_type == 'NGON' and preference.behavior.line_box:
                    preference.shape.wedge = not preference.shape.wedge
                    op.report({'INFO'}, F'{"En" if preference.shape.wedge else "Dis"}abled Wedge')

        # X, Y, Z
        elif event.type in {'X', 'Y', 'Z'}:
            if event.type == 'Z' and event.alt or event.shift:
                return {'PASS_THROUGH'}

            if event.value == 'RELEASE':
                if op.shape_type == 'NGON' and op.operation == 'DRAW' and event.type == 'Z' and event.ctrl:
                    utility.mesh.remove_point(op, context, event)

                elif op.operation in {'NONE', 'DRAW', 'EXTRUDE', 'OFFSET', 'BEVEL', 'SOLIDIFY'}:
                    if event.type == 'X':
                        if not event.ctrl:
                            if op.mode in {'SLICE', 'INSET'} and event.alt:
                                preference.behavior.recut = not preference.behavior.recut
                                utility.modal.mode.change(op, context, event, to=op.mode, force=True)
                                prefix = 'En' if preference.behavior.recut else 'Dis'
                                op.report({'INFO'}, f'{prefix}abling Recut')

                            else:
                                to = 'CUT' if op.mode != 'CUT' else 'SLICE'
                                if op.mode == 'SLICE':
                                    to = 'INTERSECT'
                                elif op.mode == 'INTERSECT':
                                    to = 'INSET'
                                elif op.mode == 'INSET':
                                    to = 'CUT'
                                utility.modal.mode.change(op, context, event, to=to)
                        else:
                            utility.modal.mode.change(op, context, event, to='KNIFE')

                    elif event.type == 'Y':
                        utility.modal.mode.change(op, context, event, to='EXTRACT')

                    elif event.type == 'Z':
                        for obj in op.datablock['targets']:
                            if obj in op.datablock['wire_targets']:
                                continue

                            obj.show_wire = not obj.show_wire
                            obj.show_all_edges = obj.show_wire

                elif op.operation in {'MOVE', 'ROTATE', 'SCALE'}:
                    utility.modal.axis.change(op, context, to=event.type)

        elif op.operation == 'NONE':
            op.update()
            return {'PASS_THROUGH'}

        op.snap = preference.snap.enable and event.ctrl

        utility.modal.refresh.shape(op, context, event)

    elif within_region_tool_header or preference.debug:
        pass_through = True

    if pass_through:

        op.update()
        return {'PASS_THROUGH'}

    op.update()
    return {'RUNNING_MODAL'}
