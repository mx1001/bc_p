from ...... utility import addon, screen


def shape(op, context, event):
    preference = addon.preference()
    bc = context.scene.bc
    snap = preference.snap.enable and preference.snap.incremental

    objects = [bc.shape] if op.mode != 'INSET' else op.datablock['slices']
    last = op.last['modifier']['thickness'] if op.mode != 'INSET' else op.last['thickness']

    thickness = (op.mouse['location'].x - op.last['mouse'].x) / screen.dpi_factor(ui_scale=False, integer=True) * 0.001

    if snap and event.ctrl:
        if event.shift:
            thickness = -round(thickness, 1)

        else:
            thickness = -round(thickness)

    elif event.shift:
        thickness = (op.mouse['location'].x - op.last['mouse'].x) / screen.dpi_factor(ui_scale=False, integer=True) * 0.0001

    for obj in objects:
        solidify = None
        for mod in obj.modifiers:
            if mod.type == 'SOLIDIFY':
                solidify = mod
                mod.thickness = last + thickness

                if op.mode != 'INSET':
                    preference.shape['solidify_thickness'] = mod.thickness
                else:
                    preference.shape['inset_thickness'] = mod.thickness

                if event.ctrl:
                    mod.thickness = round(mod.thickness, 2 if event.shift else 1)
                else:
                    if op.mode != 'INSET':
                        op.last['modifier']['thickness'] = mod.thickness
                    else:
                        op.last['thickness'] = mod.thickness
                    op.last['mouse'].x = op.mouse['location'].x

                if mod.thickness > 0:

                    if mod.thickness < 0.001:
                        mod.thickness = 0.001

                    mod.thickness = -mod.thickness

                if mod.thickness > -0.001:
                    mod.thickness = -0.001

                break

        if not solidify:
            mod = obj.modifiers.new(name='Solidify', type='SOLIDIFY')
            mod.show_in_editmode = False
            mod.offset = -1 if (op.shape_type != 'NGON' or op.extruded) else 0
            mod.use_even_offset = True
            mod.use_quality_normals = True
            mod.thickness = last

    del objects
