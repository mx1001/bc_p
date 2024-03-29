import bpy
from bl_ui import space_view3d
from .. utility import method_handler, tool

header = space_view3d.VIEW3D_HT_header
normalheader = None


def add():
    global normalheader

    if not normalheader:
        normalheader = header.draw

    header.draw = draw_handler


def remove():
    header.draw = normalheader


def draw_handler(hd, context):
    method_handler(draw,
        arguments = (hd, context),
        identifier = '3D Header',
        exit_method = remove)


def draw(hd, context):
    layout = hd.layout

    tool_settings = context.tool_settings
    view = context.space_data
    shading = view.shading
    show_region_tool_header = view.show_region_tool_header

    if not show_region_tool_header:
        layout.row(align=True).template_header()

    row = layout.row(align=True)
    obj = context.active_object
    # mode_string = context.mode
    object_mode = 'OBJECT' if obj is None else obj.mode
    has_pose_mode = (
        (object_mode == 'POSE') or
        (object_mode == 'WEIGHT_PAINT' and context.pose_object is not None)
    )

    # Note: This is actually deadly in case enum_items have to be dynamically generated
    #       (because internal RNA array iterator will free everything immediately...).
    # XXX This is an RNA internal issue, not sure how to fix it.
    # Note: Tried to add an accessor to get translated UI strings instead of manual call
    #       to pgettext_iface below, but this fails because translated enumitems
    #       are always dynamically allocated.
    act_mode_item = bpy.types.Object.bl_rna.properties["mode"].enum_items[object_mode]
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

    sub = row.row(align=True)
    sub.ui_units_x = 5.5
    sub.operator_menu_enum(
        "object.mode_set", "mode",
        text=bpy.app.translations.pgettext_iface(act_mode_item.name, act_mode_i18n_context),
        icon=act_mode_item.icon,
    )
    del act_mode_item

    layout.template_header_3D_mode()

    # Contains buttons like Mode, Pivot, Layer, Mesh Select Mode...
    if obj:
        # Particle edit
        if object_mode == 'PARTICLE_EDIT':
            row = layout.row()
            row.prop(tool_settings.particle_edit, "select_mode", text="", expand=True)

    # Grease Pencil
    if obj and obj.type == 'GPENCIL' and context.gpencil_data:
        gpd = context.gpencil_data

        if gpd.is_stroke_paint_mode:
            row = layout.row()
            sub = row.row(align=True)
            sub.prop(tool_settings, "use_gpencil_draw_onback", text="", icon='MOD_OPACITY')
            sub.separator(factor=0.4)
            sub.prop(tool_settings, "use_gpencil_weight_data_add", text="", icon='WPAINT_HLT')
            sub.separator(factor=0.4)
            sub.prop(tool_settings, "use_gpencil_draw_additive", text="", icon='FREEZE')

        # Select mode for Editing
        if gpd.use_stroke_edit_mode:
            row = layout.row(align=True)
            row.prop(tool_settings, "gpencil_selectmode_edit", text="", expand=True)

        # Select mode for Sculpt
        if gpd.is_stroke_sculpt_mode:
            row = layout.row(align=True)
            row.prop(tool_settings, "use_gpencil_select_mask_point", text="")
            row.prop(tool_settings, "use_gpencil_select_mask_stroke", text="")
            row.prop(tool_settings, "use_gpencil_select_mask_segment", text="")

        # Select mode for Vertex Paint
        if gpd.is_stroke_vertex_mode:
            row = layout.row(align=True)
            row.prop(tool_settings, "use_gpencil_vertex_select_mask_point", text="")
            row.prop(tool_settings, "use_gpencil_vertex_select_mask_stroke", text="")
            row.prop(tool_settings, "use_gpencil_vertex_select_mask_segment", text="")

        if gpd.use_stroke_edit_mode or gpd.is_stroke_sculpt_mode or gpd.is_stroke_weight_mode or gpd.is_stroke_vertex_mode:
            row = layout.row(align=True)
            row.prop(gpd, "use_multiedit", text="", icon='GP_MULTIFRAME_EDITING')

            sub = row.row(align=True)
            sub.active = gpd.use_multiedit
            sub.popover(
                panel="VIEW3D_PT_gpencil_multi_frame",
                text="Multiframe",
            )

        if gpd.use_stroke_edit_mode:
            row = layout.row(align=True)
            row.popover(
                panel="VIEW3D_PT_tools_grease_pencil_interpolate",
                text="Interpolate",
            )

    overlay = view.overlay

    space_view3d.VIEW3D_MT_editor_menus.draw_collapsible(context, layout)

    layout.separator_spacer()

    if object_mode in {'PAINT_GPENCIL', 'SCULPT_GPENCIL'}:
        # Grease pencil
        if object_mode == 'PAINT_GPENCIL':
            layout.prop_with_popover(
                tool_settings,
                "gpencil_stroke_placement_view3d",
                text="",
                panel="VIEW3D_PT_gpencil_origin",
            )

        if object_mode in {'PAINT_GPENCIL', 'SCULPT_GPENCIL'}:
            layout.prop_with_popover(
                tool_settings.gpencil_sculpt,
                "lock_axis",
                text="",
                panel="VIEW3D_PT_gpencil_lock",
            )

        if object_mode == 'PAINT_GPENCIL':
            # FIXME: this is bad practice!
            # Tool options are to be displayed in the topbar.
            if context.workspace.tools.from_space_view3d_mode(object_mode).idname == "builtin_brush.Draw":
                settings = tool_settings.gpencil_sculpt.guide
                row = layout.row(align=True)
                row.prop(settings, "use_guide", text="", icon='GRID')
                sub = row.row(align=True)
                sub.active = settings.use_guide
                sub.popover(
                    panel="VIEW3D_PT_gpencil_guide",
                    text="Guides",
                )

        layout.separator_spacer()
    elif tool.active().idname in {tool.name, 'Hops'} or not show_region_tool_header:
        # Transform settings depending on tool header visibility
        header.draw_xform_template(layout, context)

        layout.separator_spacer()

    # Viewport Settings
    layout.popover(
        panel="VIEW3D_PT_object_type_visibility",
        icon_value=view.icon_from_show_object_viewport,
        text="",
    )

    # Gizmo toggle & popover.
    row = layout.row(align=True)
    # FIXME: place-holder icon.
    row.prop(view, "show_gizmo", text="", toggle=True, icon='GIZMO')
    sub = row.row(align=True)
    sub.active = view.show_gizmo
    sub.popover(
        panel="VIEW3D_PT_gizmo_display",
        text="",
    )

    # Overlay toggle & popover.
    row = layout.row(align=True)
    row.prop(overlay, "show_overlays", icon='OVERLAY', text="")
    sub = row.row(align=True)
    sub.active = overlay.show_overlays
    sub.popover(panel="VIEW3D_PT_overlay", text="")

    row = layout.row()
    row.active = (object_mode == 'EDIT') or (shading.type in {'WIREFRAME', 'SOLID'})

    # While exposing 'shading.show_xray(_wireframe)' is correct.
    # this hides the key shortcut from users: T70433.
    row.operator(
        "view3d.toggle_xray",
        text="",
        icon='XRAY',
        depress=(
            overlay.show_xray_bone if has_pose_mode else
            getattr(
                shading,
                "show_xray_wireframe" if shading.type == 'WIREFRAME' else
                "show_xray"
            )
        ),
    )

    row = layout.row(align=True)
    row.prop(shading, "type", text="", expand=True)
    sub = row.row(align=True)
    # TODO, currently render shading type ignores mesh two-side, until it's supported
    # show the shading popover which shows double-sided option.

    # sub.enabled = shading.type != 'RENDERED'
    sub.popover(panel="VIEW3D_PT_shading", text="")

    draw_pause(hd, context)


def draw_pause(hd, context):
    layout = hd.layout
    scene = context.scene

    if context.engine == "CYCLES":
        view = context.space_data

        if view.shading.type == 'RENDERED':
            cscene = scene.cycles
            layout.prop(cscene, "preview_pause", icon='PLAY' if cscene.preview_pause else 'PAUSE', text="")
