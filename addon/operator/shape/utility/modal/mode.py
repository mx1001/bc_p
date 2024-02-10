import time

import bpy

from mathutils import Matrix, Vector

from . import refresh, flip
from ..... import toolbar

from .. import modifier
from ...... utility import addon


def change(op, context, event, to='CUT', init=False, force=False):
    preference = addon.preference()
    bc = context.scene.bc

    if op.datablock['targets'] or init:
        value = to if init or to != op.mode or force else op.last['mode']

        offset = preference.shape.offset

        was_flip_z = op.flip_z

        if value == 'MAKE':
            op.flip_z = False
            offset = 0
        elif value == 'JOIN':
            op.flip_z = True
            offset = -offset
        else:
            op.flip_z = False

        matrix = op.start['matrix'] @ Matrix.Translation(Vector((0, 0, offset)))
        bc.shape.matrix_world.translation = matrix.translation
        bc.plane.matrix_world.translation = matrix.translation
        bc.lattice.matrix_world.translation = matrix.translation

        if not op.flip_z and was_flip_z or op.flip_z and not was_flip_z:
            flip.shape(op, context, event, report=False)

        def store_last(value, to):
            if value != to:
                op.last['mode'] = value
            else:
                op.last['mode'] = 'CUT' if value != 'CUT' else value

        if not force:
            store_last(value, to)

        for obj in op.datablock['targets']:
            for mod in obj.modifiers:
                if mod == modifier.shape_bool(obj) or mod.type == 'BOOLEAN' and not mod.object:
                    obj.modifiers.remove(mod)

        if not init and op.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            for pair in zip(op.datablock['targets'], op.datablock['overrides']):
                obj = pair[0]
                override = pair[1]

                name = obj.data.name
                obj.data.name = 'tmp'
                obj.data = override
                obj.data.name = name

            bpy.ops.object.mode_set(mode='EDIT')

        for obj in op.datablock['slices']:
            bpy.data.objects.remove(obj)

        op.datablock['slices'] = list()

        if value == 'KNIFE':
            for obj in op.datablock['targets']:
                for mod in obj.modifiers:
                    if mod.type == 'MIRROR':
                        mod.show_viewport = False

        else:
            for obj in op.datablock['targets']:
                for mod in obj.modifiers:
                    if mod.type == 'MIRROR':
                        mod.show_viewport = True

        op.mode = value
        toolbar.change_prop(context, 'mode', value)

        if not init:

            refresh.shape(op, context, event)

            wm = context.window_manager
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

            op.report({'INFO'}, '{}{}{}'.format(
                value.title()[:-1 if value in {'SLICE', 'MAKE'} else len(value)] if value != 'KNIFE' else 'Using Knife',
                't' if value in {'CUT', 'INSET'} else '',
                'ing' if value != 'KNIFE' else ''))
