import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, EnumProperty

from . utility import update
from .... utility import addon, modifier
from ... property.utility import names

class bc(PropertyGroup):

    # quick_execute: BoolProperty(
    #     name = names['quick_execute'],
    #     description = '\n Quickly execute cuts on release',
    #     default = False)

    auto_ortho: BoolProperty(
        name = names['auto_ortho'],
        description = '\n Automatically enter orthographic for view project cuts',
        default = False)

    parent_shape: BoolProperty(
        name = names['parent_shape'],
        description = '\n Parent cutters to the target',
        default = True)

    autohide_shapes: BoolProperty(
        name = 'Auto Hide Shapes',
        description = '\n Hide previously made unselected cutters on cut',
        default = True)

    apply_slices: BoolProperty(
        name = names['apply_slices'],
        description = '\n Apply slice cuts on the slice objects',
        default = False)

    recut: BoolProperty(
        name = names['recut'],
        description = '\n Strip slice objects of previousely existing booleans',
        default = False)

    show_wire: BoolProperty(
        name = names['show_wire'],
        description = '\n Display wires on target',
        default = False)

    apply_scale: BoolProperty(
        name = names['apply_scale'],
        description = '\n Apply scale on the target if it is scaled',
        default = True)

    auto_smooth: BoolProperty(
        name = names['auto_smooth'],
        description = '\n Auto smooth geometry when cutting into it',
        default = True)

    join_flip_z: BoolProperty(
        name = names['join_flip_z'],
        description = '\n Flip the shape fitted for custom shape on the z axis during a join operation',
        default = True)

    # make_active: BoolProperty(
    #     name = names['make_active'],
    #     description = '\n Make the shape active when holding shift to keep it',
    #     default = True)

    line_box: BoolProperty(
        name = names['line_box'],
        description = '\n Extrude the initial line when drawing an NGon',
        update = update.shape_type,
        default = False)

    hops_mark: BoolProperty(
        name = names['hops_mark'],
        description = '\n Marks boundary using hardOps helper specified markings ',
        default = False)

    set_origin: EnumProperty(
        name = names['set_origin'],
        description = 'Origin',
        items = [
            ('MOUSE', 'Mouse Position', '\n Mouse Position', 'RESTRICT_SELECT_OFF', 1),
            ('CENTER', 'Center', '\n Initial Centered', 'SNAP_FACE_CENTER', 2),
            ('BBOX', 'Bounding Box Center', '\n Bounding Box Center', 'PIVOT_BOUNDBOX', 3),
            ('ACTIVE', 'Active Element', '\n Active Element', 'PIVOT_ACTIVE', 4)],
        default = 'BBOX')

    show_shape: BoolProperty(
        name = names['show_shape'],
        description = '\n Display the shape object when finished',
        default = False)

    lazorcut_trim: BoolProperty(
        name = names['lazorcut_trim'],
        description = 'Trim the cutter on lazorcut for better fit',
        default = True)

    simple_trace: BoolProperty(
        name = names['simple_trace'],
        description = '\n Use simple bound cubes when ray tracing (Faster)',
        default = False)

    sort_modifiers: BoolProperty(
        name = names['sort_modifiers'],
        description = '\n Sort modifier order',
        update = update.sync_sort,
        default = True)

    sort_bevel: BoolProperty(
        name = 'Sort Bevel',
        description = '\n Ensure bevel modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_weighted_normal: BoolProperty(
        name = 'Sort Weighted Normal',
        description = '\n Ensure weighted normal modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_array: BoolProperty(
        name = 'Sort Array',
        description = '\n Ensure array modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_mirror: BoolProperty(
        name = 'Sort Mirror',
        description = '\n Ensure mirror modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_solidify: BoolProperty(
        name = 'Sort Soldify',
        description = '\n Ensure solidify modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = False)

    sort_triangulate: BoolProperty(
        name = 'Sort Triangulate',
        description = '\n Ensure triangulate modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_simple_deform: BoolProperty(
        name = 'Sort Simple Deform',
        description = '\n Ensure simple deform modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_decimate: BoolProperty(
        name = 'Sort Decimate',
        description = '\n Ensure decimate modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = False)

    sort_remesh: BoolProperty(
        name = 'Sort Remesh',
        description = '\n Ensure remesh modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_subsurf: BoolProperty(
        name = 'Sort Subsurf',
        description = '\n Ensure subsurf modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = False)

    sort_weld: BoolProperty(
        name = 'Sort Weld',
        description = '\n Ensure weld modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = False)

    sort_uv_project: BoolProperty(
        name = 'Sort UV Project',
        description = '\n Ensure uv project modifiers are placed after any boolean modifiers created',
        update = update.sync_sort,
        default = True)

    sort_bevel_last: BoolProperty(
        name = 'Sort Bevel',
        description = '\n Only effect the most recent bevel modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_weighted_normal_last: BoolProperty(
        name = 'Sort Weighted Normal Last',
        description = '\n Only effect the most recent weighted normal modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_array_last: BoolProperty(
        name = 'Sort Array Last',
        description = '\n Only effect the most recent array modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_mirror_last: BoolProperty(
        name = 'Sort Mirror Last',
        description = '\n Only effect the most recent mirror modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_solidify_last: BoolProperty(
        name = 'Sort Soldify Last',
        description = '\n Only effect the most recent solidify modifier when sorting',
        update = update.sync_sort,
        default = False)

    sort_triangulate_last: BoolProperty(
        name = 'Sort Triangulate Last',
        description = '\n Only effect the most recent triangulate modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_simple_deform_last: BoolProperty(
        name = 'Sort Simple Deform Last',
        description = '\n Only effect the most recent simple deform modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_decimate_last: BoolProperty(
        name = 'Sort Decimate Last',
        description = '\n Only effect the most recent decimate modifier when sorting',
        update = update.sync_sort,
        default = False)

    sort_remesh_last: BoolProperty(
        name = 'Sort Remesh Last',
        description = '\n Only effect the most recent remesh modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_subsurf_last: BoolProperty(
        name = 'Sort Subsurf Last',
        description = '\n Only effect the most recent subsurface modifier when sorting',
        update = update.sync_sort,
        default = False)

    sort_weld_last: BoolProperty(
        name = 'Sort Weld Last',
        description = '\n Only effect the most recent weld modifier when sorting',
        update = update.sync_sort,
        default = True)

    sort_uv_project_last: BoolProperty(
        name = 'Sort UV Project Last',
        description = '\n Only effect the most recent uv project modifier when sorting',
        update = update.sync_sort,
        default = True)

    keep_modifiers: BoolProperty(
        name = names['keep_modifiers'],
        description = '\n Choose what modifiers are applied on the shape',
        default = True)

    sort_bevel_ignore_vgroup: BoolProperty(
        name = 'Ignore VGroup Bevels',
        description = '\n Ignore bevel modifiers that are using the vertex group limit method while sorting',
        update = update.sync_sort,
        default = True)

    sort_bevel_ignore_only_verts: BoolProperty(
        name = 'Ignore Only Vert Bevels',
        description = '\n Ignore bevel modifiers that are using the only vertices option while sorting',
        update = update.sync_sort,
        default = True)

    keep_array: BoolProperty(
        name = 'Keep Array',
        description = '\n Keep shape array modifier',
        default = True)

    keep_bevel: BoolProperty(
        name = 'Keep Bevel',
        description = '\n Keep shape bevel modifiers',
        default = True)

    keep_solidify: BoolProperty(
        name = 'Keep Soldify',
        description = '\n Keep shape solidify modifier',
        default = True)

    keep_weld: BoolProperty(
        name = 'Keep Weld',
        description = '\n Keep shape weld modifier',
        default = True)

    keep_mirror: BoolProperty(
        name = 'Keep Mirror',
        description = '\n Keep shape mirror modifier',
        default = True)

    keep_screw: BoolProperty(
        name = 'Keep Screw',
        description = '\n Keep shape spin modifier',
        default = False)

    keep_lattice: BoolProperty(
        name = 'Keep Lattice',
        description = '\n Keep shape lattice modifier',
        default = False)

    cutter_uv: BoolProperty(
        name = 'Cutter UV',
        description = '\n Add UV to cutters',
        default = False)

    use_dpi_factor: BoolProperty(
        name = 'Use DPI Factor',
        description = ('\n Use DPI factoring when drawing and choosing dimensions.\n'
                       ' Note: Having this enabled can cause behavior issues on some machines'),
        default = True)

    surface_extract: BoolProperty(
        name = 'Surface Extract',
        description = ('\n Use Suface Extract algorithm for Extract mode. Uncheck to use classic Boolean Extraction\n'
                        'ALT+X to toggle during Extract'),
        default = True)



def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.behavior, 'sort_modifiers', layout.row())

    if preference.behavior.sort_modifiers:
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        split = row.split(align=True, factor=0.85)

        row = split.row(align=True)
        for type in modifier.sort_types:
            icon = F'MOD_{type}'
            if icon == 'MOD_WEIGHTED_NORMAL':
                icon = 'MOD_NORMALEDIT'
            elif icon == 'MOD_SIMPLE_DEFORM':
                icon = 'MOD_SIMPLEDEFORM'
            elif icon == 'MOD_DECIMATE':
                icon = 'MOD_DECIM'
            elif icon == 'MOD_WELD':
                icon = 'AUTOMERGE_OFF'
            elif icon == 'MOD_UV_PROJECT':
                icon = 'MOD_UVPROJECT'
            row.prop(preference.behavior, F'sort_{type.lower()}', text='', icon=icon)

        row = split.row(align=True)
        row.scale_x = 1.5
        row.popover('BC_PT_sort_last', text='', icon='SORT_ASC')

    label_row(preference.behavior, 'keep_modifiers', layout.row())

    if preference.behavior.keep_modifiers:
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(preference.behavior, 'keep_bevel', text='', icon='MOD_BEVEL')
        row.prop(preference.behavior, 'keep_solidify', text='', icon='MOD_SOLIDIFY')
        row.prop(preference.behavior, 'keep_array', text='', icon='MOD_ARRAY')
        if bpy.app.version[1] >= 82:
            row.prop(preference.behavior, 'keep_weld', text='', icon='AUTOMERGE_OFF')
        row.prop(preference.behavior, 'keep_mirror', text='', icon='MOD_MIRROR')
        row.prop(preference.behavior, 'keep_screw', text='', icon='MOD_SCREW')
        row.prop(preference.behavior, 'keep_lattice', text='', icon='MOD_LATTICE')

    # label_row(preference.behavior, 'quick_execute', layout.row())
    label_row(preference.behavior, 'line_box', layout.row())
    label_row(preference.behavior, 'auto_ortho', layout.row())
    label_row(preference.behavior, 'apply_slices', layout.row())
    label_row(preference.behavior, 'recut', layout.row())
    label_row(preference.behavior, 'show_wire', layout.row())
    label_row(preference.behavior, 'apply_scale', layout.row())
    # label_row(preference.behavior, 'make_active', layout.row())
    label_row(preference.behavior, 'show_shape', layout.row())
    label_row(preference.behavior, 'auto_smooth', layout.row())
    label_row(preference.behavior, 'join_flip_z', layout.row())
    label_row(preference.behavior, 'parent_shape', layout.row())
    label_row(preference.behavior, 'cutter_uv', layout.row(), label='Cutter UV')
    label_row(preference.behavior, 'surface_extract', layout.row(), label='Surface Extract')
    label_row(preference.behavior, 'lazorcut_trim', layout.row())
    # label_row(preference.behavior, 'simple_trace', layout.row())

    layout.separator()

    label_row(preference.behavior, 'use_dpi_factor', layout.row(), label='Use DPI Factoring')
