from ..... utility import addon
from .. import utility
from .. utility import statusbar
# from .. utility import statusbar
# from ... utility import shape
# from .. draw import prop

# from .... property import prop


def operator(op, context):
    wm = context.window_manager
    bc = context.scene.bc

    # op.shader.cancel = True
    # op.widgets.cancel = True

    bc.running = False
    statusbar.remove()
    # prop.running = False

    op.cancelled = True

    op.update()

    op.geo['indices']['extrusion'].clear()

    if op.datablock['overrides']:
        for pair in zip(op.datablock['targets'], op.datablock['overrides']):
            obj = pair[0]
            override = pair[1]

            obj.data = override

    hops = getattr(wm, 'Hard_Ops_material_options', False)
    if hops and hops.active_material:
        for obj in op.datablock['targets']:
            obj.data.materials.clear()

            for mat in op.existing[obj]['materials']:
                obj.data.materials.append(mat)

    utility.data.clean(op, context, all=True)
    # bpy.types.SpaceView3D.draw_handler_remove(op.dot_handler, 'WINDOW')
    # op.widgets.exit = True

    # if preference.display.dots:
        # op.widgets.remove()
    op.report({'INFO'}, 'Cancelled')

    return {'CANCELLED'}
