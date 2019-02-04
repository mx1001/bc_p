import bpy
from bgl import *
import blf
from bpy.props import StringProperty, BoolProperty
from .. utils.blender_ui import get_dpi_factor, get_dpi, get_3d_view_tools_panel_overlay_width
from . draw_px import draw_box, draw_button_text, draw_border_region, draw_point
from . logo import draw_logo_boxcutter
from . help_info import draw_help
from .. utils.objects import get_current_selected_status, get_inactive_selected_objects
from .. utils.lists import append_to_list, remove_from_list
from .. preferences import BC_border_color, BC_indicator_color, enable_border_display

set_cutter_shape = "BOX"


def draw(self, context):
    global set_cutter_shape
    
    if not (DrawBooleanLayout.running_boxcutters.get(self._region) is self): return
    
    if self._region != context.region: return
    
    active_object, other_objects, other_object = get_current_selected_status()
    only_meshes_selected = all(object.type == "MESH" for object in bpy.context.selected_objects)
    object = bpy.context.active_object

    circle_verts = bpy.context.scene.BoxCutter_circle_vert_count 
    grid_spacing = bpy.context.scene.BoxCutter_grid_spaceing 
    
    draw_logo_boxcutter()

    if set_cutter_shape == "BOX":
        draw_button_text(True , get_3d_view_tools_panel_overlay_width(bpy.context.area) + 20*get_dpi_factor() , bpy.context.region.height - get_vertical_offset() - 60*get_dpi_factor(), '{} Cutter: BOX'.format(get_boolean_method_in_use()))
    elif set_cutter_shape == "NGON":
        draw_button_text(True , get_3d_view_tools_panel_overlay_width(bpy.context.area) + 20*get_dpi_factor() , bpy.context.region.height - get_vertical_offset() - 60*get_dpi_factor(), '{} Cutter: NGON'.format(get_boolean_method_in_use()))
    elif set_cutter_shape == "CIRCLE":
        draw_button_text(True , get_3d_view_tools_panel_overlay_width(bpy.context.area) + 20*get_dpi_factor() , bpy.context.region.height - get_vertical_offset() - 60*get_dpi_factor(), '{} Cutter: CIRCLE {:}' .format(get_boolean_method_in_use(), circle_verts))

    draw_button_text(True , get_3d_view_tools_panel_overlay_width(bpy.context.area) + 122*get_dpi_factor() , bpy.context.region.height - get_vertical_offset() - 60*get_dpi_factor(), 'Grid  {}' .format(grid_spacing))

    if active_object.mode == "OBJECT":
        if bpy.context.scene.BoxCutter_enable_help :
            draw_help(bpy.context.region.width-260*get_dpi_factor(), 320*get_dpi_factor() )

        if bpy.context.scene.BoxCutter_enable_grid:
            draw_point(self, context)    

    width = bpy.context.region.width
    factorx = get_dpi_factor()
    height = bpy.context.region.height
    factory = get_dpi_factor()
    #draw_box(width -100*factorx , height - 34*factory, 30*get_dpi_factor(), 30*get_dpi_factor())
    if enable_border_display():
        draw_border_region(self, context)

# ============ from dairin0d's library ============ #
def point_in_rect(p, r):
    return ((p[0] >= r.x) and (p[0] < r.x + r.width) and (p[1] >= r.y) and (p[1] < r.y + r.height))

def rv3d_from_region(area, region):
    if (area.type != 'VIEW_3D') or (region.type != 'WINDOW'): return None
    
    space_data = area.spaces.active
    try:
        quadviews = space_data.region_quadviews
    except AttributeError:
        quadviews = None # old API
    
    if not quadviews: return space_data.region_3d
    
    x_id = 0
    y_id = 0
    for r in area.regions:
        if (r.type == 'WINDOW') and (r != region):
            if r.x < region.x: x_id = 1
            if r.y < region.y: y_id = 1
    
    # 0: bottom left (Front Ortho)
    # 1: top left (Top Ortho)
    # 2: bottom right (Right Ortho)
    # 3: top right (User Persp)
    return quadviews[y_id | (x_id << 1)]

# areas can't overlap, but regions can
def ui_contexts_under_coord(x, y, window=None):
    point = int(x), int(y)
    if not window: window = bpy.context.window
    screen = window.screen
    scene = screen.scene
    tool_settings = scene.tool_settings
    for area in screen.areas:
        if point_in_rect(point, area):
            space_data = area.spaces.active
            for region in area.regions:
                if point_in_rect(point, region):
                    yield dict(window=window, screen=screen,
                        area=area, space_data=space_data, region=region,
                        region_data=rv3d_from_region(area, region),
                        scene=scene, tool_settings=tool_settings)
            break

def region_exists(r):
    wm = bpy.context.window_manager
    for window in wm.windows:
        for area in window.screen.areas:
            for region in area.regions:
                if region == r: return True
    return False
# ================================================= #

class DrawBooleanLayout(bpy.types.Operator):
    bl_idname = "boxcutter.draw_boolean_layout"
    bl_label = "Draw Screen Buttons"
    bl_description = "draw screen buttons"
    
    x = 0
    y = 0

    global show_hops
    
    running_boxcutters = {}
    
    def validate_region(self):
        if not (DrawBooleanLayout.running_boxcutters.get(self._region) is self): return False
        return region_exists(self._region)

    def modal(self, context, event):
        active_object, other_objects, other_object = get_current_selected_status()

        try:
            if not self.validate_region():
                self.cancel(context)
                return {'CANCELLED'}
            
            context.area.tag_redraw()
            
            self.LMB = False
            self.RMB = False

            if event.type == 'MOUSEMOVE':
                self.x = event.mouse_region_x
                self.y = event.mouse_region_y
                x_abs = self.x + context.region.x
                y_abs = self.y + context.region.y
                ui_contexts = list(ui_contexts_under_coord(x_abs, y_abs, context.window))
                if ui_contexts and ui_contexts[0]:
                    self._region_mouse = [uic["region"] for uic in ui_contexts]
            
            if not (self._region in self._region_mouse): return {'PASS_THROUGH'}
            
            if event.type == 'LEFTMOUSE'and event.value=='PRESS':
                if set_cutter_shape == "BOX":
                    if len(bpy.context.selected_objects) == 1:

                        if event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_poly('INVOKE_DEFAULT')
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_slicebox('INVOKE_DEFAULT')
                            return {'RUNNING_MODAL'}

                    if len(bpy.context.selected_objects) > 1:
                        if event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT'):
                            bpy.ops.boxcutter.bool_difference()
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT'):
                            bpy.ops.boxcutter.bool_union()
                            return {'RUNNING_MODAL'}


                    if len(bpy.context.selected_objects) == 0:

                        if event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.add_cube()
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_poly('INVOKE_DEFAULT', cut_mode =False )
                            return {'RUNNING_MODAL'}

                elif (set_cutter_shape == "NGON"):
                    
                    round_corners = (set_cutter_shape == "NGON")
                    
                    if len(bpy.context.selected_objects) == 1:

                        if event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_curve('INVOKE_DEFAULT', slice=False, round_corners=round_corners)
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_curve('INVOKE_DEFAULT', slice=True, round_corners=round_corners)
                            return {'RUNNING_MODAL'}

                    if len(bpy.context.selected_objects) > 1:
                        if event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT'):
                            bpy.ops.boxcutter.bool_difference()
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT'):
                            bpy.ops.boxcutter.bool_union()
                            return {'RUNNING_MODAL'}


                    if len(bpy.context.selected_objects) == 0:

                        if event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.add_cube()
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_curve('INVOKE_DEFAULT', slice=False, round_corners=round_corners, cut_mode=False)
                            return {'RUNNING_MODAL'}


                elif set_cutter_shape == "CIRCLE":

                    if len(bpy.context.selected_objects) == 1:

                        if event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_circle('INVOKE_DEFAULT')
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.slice_circle('INVOKE_DEFAULT')
                            return {'RUNNING_MODAL'}

                    if len(bpy.context.selected_objects) > 1:
                        if event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT'):
                            bpy.ops.boxcutter.bool_difference()
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT'):
                            bpy.ops.boxcutter.bool_union()
                            return {'RUNNING_MODAL'}


                    if len(bpy.context.selected_objects) == 0:

                        if event.ctrl and event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.add_cube()
                            return {'RUNNING_MODAL'}

                        elif event.ctrl and not event.shift and (active_object == None or context.active_object.mode == 'OBJECT') :
                            bpy.ops.boxcutter.draw_circle('INVOKE_DEFAULT', cut_mode =False )
                            return {'RUNNING_MODAL'}


            elif  event.value =='PRESS' and event.type == 'D' and event.ctrl  :
                bpy.ops.boxcutter.bisect()
                return {'RUNNING_MODAL'}

            elif  event.value =='RELEASE' and event.type == 'D' and not event.ctrl and not event.shift and not event.alt:
                boxcutter_set_shape()
                bpy.context.scene.BoxCutter_shape_moving = False
                return {'RUNNING_MODAL'}

            elif event.alt and not event.shift and event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.alt and event.value=='PRESS':
                boxcutter_set_cutter_method('forward')
                return {'RUNNING_MODAL'}

            elif event.alt and not event.shift and event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.alt and event.value=='PRESS':
                boxcutter_set_cutter_method('backward')
                return {'RUNNING_MODAL'}

            elif event.shift and event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.shift and event.value=='PRESS':
                bpy.context.scene.BoxCutter_grid_spaceing += 5
                return {'RUNNING_MODAL'}

            elif event.shift and event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.shift and event.value=='PRESS':
                bpy.context.scene.BoxCutter_grid_spaceing -= 5
                return {'RUNNING_MODAL'}

            elif event.shift and event.type == "Z" and event.value=='PRESS':
                if bpy.context.scene.BoxCutter_enable_grid == False:
                    bpy.context.scene.BoxCutter_enable_grid = True
                else:
                    bpy.context.scene.BoxCutter_enable_grid = False
                return {'RUNNING_MODAL'}

            if event.type == 'ESC' and event.value =='PRESS':
                self.cancel(context)
                return {'CANCELLED'}

            return {'PASS_THROUGH'}
        except Exception as exc:
            print(exc)
            self.cancel(context)
            return {'CANCELLED'}

    def cancel(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        if DrawBooleanLayout.running_boxcutters.get(self._region) is self:
            del DrawBooleanLayout.running_boxcutters[self._region]
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            DrawBooleanLayout.running_boxcutters = {}
            self._region_mouse = [context.region]
            self._region = context.region
            DrawBooleanLayout.running_boxcutters[self._region] = self
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
            
        else:
            return {'CANCELLED'}



def boxcutter_set_cutter_method(cycle='forward'):
    if cycle == 'backward':
        if bpy.context.scene.BoxCutter_bool_method == 'CARVE':
            bpy.context.scene.BoxCutter_bool_method = 'BMESH'
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
            bpy.context.scene.BoxCutter_bool_method = 'CARVE'
        elif bpy.context.scene.BoxCutter_bool_method == 'BMESH':
            bpy.context.scene.BoxCutter_bool_method = 'CARVEMOD'
    elif cycle == 'forward':
        if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
            bpy.context.scene.BoxCutter_bool_method = 'CARVE'
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVE':
            bpy.context.scene.BoxCutter_bool_method = 'CARVEMOD'
        elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
            bpy.context.scene.BoxCutter_bool_method = 'BMESH'

def boxcutter_set_shape():
    global set_cutter_shape

    if set_cutter_shape == "BOX":
        set_cutter_shape = "CIRCLE"
    elif set_cutter_shape == "CIRCLE":
        if bpy.context.scene.BoxCutter_enable_ngon:
            set_cutter_shape = "NGON"
        else:
            set_cutter_shape = "BOX"
    elif set_cutter_shape == "NGON":
        set_cutter_shape = "BOX"

def get_vertical_offset():
    if bpy.context.scene.unit_settings.system == "NONE":
        return 0
    else:
        return 20
def get_boolean_method_in_use():
    if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
        method = '(B)'
    elif bpy.context.scene.BoxCutter_bool_method == 'CARVE':
        method = '(C)'
    elif bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
        method = '(M)'

    return method

