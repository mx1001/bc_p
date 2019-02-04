import bpy
import bgl
import blf
import bpy_extras.view3d_utils
from mathutils import Vector
import bmesh
from bpy.props import *
from ... utils.objects import set_active, show_obj_wires
from ... utils.modifiers import apply_modifiers, create_solidify_modifier
from ... graphic.draw_px import draw_extending_box
from ... ui.main_panel import boxcutter_enable_hops
from ... utils.view_3d import set_3d_cursor_location, save_3d_cursor_location
from ... utils.blender_ui import get_region_dimensions
from ... utils.space_3d import get_center_point

saved_cords = [0, 0]
enable_grid = False

def get_view_directions(context):
    region = context.region
    rv3d = context.space_data.region_3d
    v0 = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, Vector((0,0)), Vector())
    vX = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, Vector((1,0)), Vector())
    vY = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, Vector((0,1)), Vector())
    dirX = (vX - v0).normalized()
    dirY = (vY - v0).normalized()
    dirZ = dirX.cross(dirY)
    return (dirX, dirY, dirZ)

def make_bmesh(self, context):
    cursor_x, cursor_y, cursor_z = save_3d_cursor_location()
    set_3d_cursor_location(0, 0, 0)

    bpy.ops.object.add(type='MESH')
    ob = bpy.context.object
    me = ob.data

    set_3d_cursor_location(cursor_x, cursor_y, cursor_z)

    bm = bmesh.new()
    list_verts = []
    for v in self.list_location_3d:
        list_verts.append(bm.verts.new(v))
    try:
        bm.faces.new(list_verts)
    except:
        pass
    bm.to_mesh(me)
    bm.free()

def generate_3d_mesh(self, context, bmesh_matrix):
    view_directions = get_view_directions(context)

    selection = bpy.context.scene.objects.active

    if bmesh_matrix == 'BOX':
        self.list_location_3d = []
        append_vert_to_list(self, context, self.first_mouse_x, self.first_mouse_y)
        append_vert_to_list(self, context, self.first_mouse_x, self.last_mouse_region_y)
        append_vert_to_list(self, context, self.last_mouse_region_x, self.last_mouse_region_y)
        append_vert_to_list(self, context, self.last_mouse_region_x, self.first_mouse_y)
    elif bmesh_matrix == 'CIRCLE':
        for m in range(0, self.n):
            append_vert_to_list(self, context, self.list_dx[m % self.n], self.list_dy[m % self.n])
        del self.list_location_3d[0]
        del self.list_location_3d[0]
    make_bmesh(self, context)

    if self.cut_mode:
        selection.select = True

    thickess = 0.6
    set_active(bpy.context.scene.objects.active, True)
    cutter = bpy.context.scene.objects.active
    bpy.context.scene.objects.active = self.first_active

    if self.first_active in list(bpy.context.selected_objects):
        if self.use_3d_cursor == False:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
        biggest_dimension = [abs(bpy.context.object.dimensions[0]), abs(bpy.context.object.dimensions[1]), abs(bpy.context.object.dimensions[2])]
        thickess = max(biggest_dimension)

        bpy.ops.object.select_all(action='DESELECT')
        set_active(self.first_active, True)
    else:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    
    set_active(cutter, True)
    object = bpy.context.active_object
    create_solidify_modifier(object, thickess*2, 0, True, False, True, True)
    if self.use_3d_cursor:
        object.location += view_directions[2] * thickess
    bpy.ops.object.modifier_apply(apply_as="DATA",modifier='Solidify')
    
def append_vert_to_list(self, context, x, y):
    region = context.region
    rv3d = context.space_data.region_3d
    depth_location = bpy.context.scene.cursor_location

    region_2d = Vector((x, y))
    location_3d = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, region_2d, depth_location)
    self.list_location_3d.append(location_3d)
    depth_location = self.list_location_3d[0]

def set_evet_region(self, event, first):
    if first:
        self.first_mouse_x = self.mouse_path[0]
        self.first_mouse_y = self.mouse_path[1]
    else:
        self.last_mouse_region_x = self.mouse_path[0]
        self.last_mouse_region_y = self.mouse_path[1]

def set_saved_region(self, event):
    self.first_mouse_x = self.mouse_path[0]+self.savedx
    self.first_mouse_y = self.mouse_path[1]+self.savedy

def check_if_moving(self, context, event):
    if bpy.context.scene.BoxCutter_shape_moving == True:
        set_saved_region(self, event)
        append_vert_to_list(self, context, self.first_mouse_x, self.first_mouse_y)
    else:
        append_vert_to_list(self, context, self.first_mouse_x, self.first_mouse_y)

def boxcutter_show_wire(self, context, enable):
    if bpy.context.scene.BoxCutter_show_wires == True:
        if self.first_active in list(bpy.context.selected_objects):
            show_obj_wires(context, enable)

def set_grid_path(self,context, event):

    region_height, region_width = get_region_dimensions()
    center_point = get_center_point(self, context)
    grid_path_spaceing = bpy.context.scene.BoxCutter_grid_spaceing

    if bpy.context.scene.BoxCutter_enable_grid:
        grid_path_x = int(int(center_point[0]) - (grid_path_spaceing *(int((center_point[0] - event.mouse_region_x)/grid_path_spaceing))))
        grid_path_y = int(int(center_point[1]) - (grid_path_spaceing *(int((center_point[1] - event.mouse_region_y)/grid_path_spaceing))))
    else:
        grid_path_x = event.mouse_region_x
        grid_path_y = event.mouse_region_y

    return grid_path_x, grid_path_y
