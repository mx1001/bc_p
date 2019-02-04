import bpy
from bgl import *
import blf
import bpy_extras.view3d_utils
import math
from .. preferences import BC_border_color, BC_indicator_color
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from .. utils.blender_ui import get_region_dimensions
from .. utils.space_3d import get_center_point
from .. utils.blender_ui import get_dpi_factor, get_dpi, get_3d_view_tools_panel_overlay_width

def draw_border_region(self, context):
    region = context.region
    rv3d = bpy.context.space_data.region_3d
   
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glColor4f(BC_border_color()[0], BC_border_color()[1], BC_border_color()[2], BC_border_color()[3])
    lw = 4 // 2
    glLineWidth(lw*4)

    glBegin(GL_LINE_STRIP)
    glVertex2i(lw, lw)
    glVertex2i(region.width - lw, lw)
    glVertex2i(region.width - lw, region.height - lw)
    glVertex2i(lw, region.height - lw)
    glVertex2i(lw, lw)
    glEnd()
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)  


def draw_extending_slicengon(self, context):
    region = context.region
    rv3d = context.space_data.region_3d

    self.last_x_position = self.mouse_path[0]
    self.last_y_position = self.mouse_path[1]

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    if self.first_active in list(bpy.context.selected_objects):
        glColor4f(0.62, 0.5, 0.2, 0.5)
    else :
        glColor4f(0.5, 0.5, 0.5, 0.5)

    glPointSize(5)
    glLineWidth(3)

    if 1 <= len(self.list_location_3d) < 2: 
        glBegin(GL_LINES)
    else:
        glBegin(GL_TRIANGLE_FAN)

    glBegin(GL_TRIANGLE_FAN)
    for x in self.list_location_3d:
        loc_1 = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, x)
        glVertex2f(loc_1[0], loc_1[1])
    glVertex2f(self.mouse_path[0], self.mouse_path[1])
    glEnd()
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)  

def draw_extending_ngon(self, context):
    region = context.region
    rv3d = context.space_data.region_3d

    self.last_x_position = self.mouse_path[0]
    self.last_y_position = self.mouse_path[1]

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)


    if self.first_active in list(bpy.context.selected_objects):
        glColor4f(0.6, 0.2, 0.2, 0.5)
    else :
        glColor4f(0.5, 0.5, 0.5, 0.5)

    glPointSize(5)
    glLineWidth(3)

    if 1 <= len(self.list_location_3d) < 2: 
        glBegin(GL_LINES)
    else:
        glBegin(GL_TRIANGLE_FAN)

    for x in self.list_location_3d:
        loc_1 = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, x)
        glVertex2f(loc_1[0], loc_1[1])
    glVertex2f(self.mouse_path[0], self.mouse_path[1])
    glEnd()
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)  

def draw_extending_curve(self, context):
    region = context.region
    rv3d = context.space_data.region_3d

    self.last_x_position = self.mouse_path[0]
    self.last_y_position = self.mouse_path[1]

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    if self.first_active in list(bpy.context.selected_objects):
        if self.slice:
            glColor4f(0.62, 0.5, 0.2, 0.5)
        else:
            glColor4f(0.6, 0.2, 0.2, 0.5)
    else :
        glColor4f(0.5, 0.5, 0.5, 0.5)

    glPointSize(self.point_radius*2)
    glLineWidth(3)
    
    if len(self.list_location_3d) <= 2:
        glBegin(GL_TRIANGLE_FAN)
        
        halfsize = 2.5 # point size: 5
        pA = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.list_location_3d[0])
        pB = pA
        
        if len(self.list_location_3d) > 1:
            halfsize = 1.5 # line width: 3
            pB = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.list_location_3d[1])
        
        dAB = (pB - pA).normalized()
        if dAB.magnitude < 0.5: dAB = Vector((1.0, 0.0))
        cAB = dAB.orthogonal()
        dAB *= halfsize
        cAB *= halfsize
        
        p00 = pA - dAB - cAB
        p01 = pA - dAB + cAB
        p10 = pB + dAB - cAB
        p11 = pB + dAB + cAB
        
        glVertex2f(p00[0], p00[1])
        glVertex2f(p01[0], p01[1])
        glVertex2f(p11[0], p11[1])
        glVertex2f(p10[0], p10[1])
        
        glEnd()
    else:
        locations_2d = [bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, loc_3d)
                        for loc_3d in self.list_location_3d]
        triangles = tessellate_polygon([locations_2d])
        
        glBegin(GL_TRIANGLES)
        for tri in triangles:
            for v_id in tri:
                v = locations_2d[v_id]
                glVertex2f(v[0], v[1])
        glEnd()
        
        if self.draw_outline:
            glColor4f(0.2, 0.2, 0.5, 0.75)
            glBegin(GL_LINE_LOOP)
            for loc_2d in locations_2d:
                glVertex2f(loc_2d[0], loc_2d[1])
            glEnd()
        
        if self.draw_points:
            if self.drag_option == 'MOVE':
                glColor4f(0.1, 0.45, 0.1, 0.75)
            else:
                glColor4f(0.2, 0.2, 0.5, 0.75)
            glBegin(GL_POINTS)
            for curve_point in self.curve_points:
                loc_2d = curve_point["2d"]
                glVertex2f(loc_2d[0], loc_2d[1])
            glEnd()

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)  

def draw_extending_circle(self, context):

    if bpy.context.scene.BoxCutter_shape_moving:
        center = self.mouse_path[0] + self.savedx, self.mouse_path[1] + self.savedy
    else:
        center = self.first_mouse_x, self.first_mouse_y

    if self.first_active in list(bpy.context.selected_objects):
        if self.yellow_color:
            glColor4f(0.62, 0.5, 0.2, 0.5)
        else:
            glColor4f(0.6, 0.2, 0.2, 0.5)
    else :
        glColor4f(0.5, 0.5, 0.5, 0.5)

    radius = abs(math.hypot(self.mouse_path[0] - center[0], self.mouse_path[1] - center[1]))
    amount = self.n

    self.list_dx, self.list_dy = calc_circle_pints(center, radius, amount)

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glBegin(GL_TRIANGLE_FAN)

    for x, y in zip(self.list_dx, self.list_dy):
        glVertex2f(x, y)

    glEnd()
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)  


def calc_circle_pints(center, radius, amount):
    list_dx = []
    list_dy = []

    x_offset, y_offset = center
    angle = math.radians(360 / amount)
    for i in range(amount):
        list_dx.append(math.cos(i*angle) * radius + x_offset)
        list_dy.append(math.sin(i*angle) * radius + y_offset)

    return list_dx, list_dy

def draw_extending_box(self, context):
    
    if bpy.context.scene.BoxCutter_shape_moving:
        dx0 = self.mouse_path[0] + self.savedx
        dy0 = self.mouse_path[1] + self.savedy
    else:
        dx0 = self.first_mouse_x
        dy0 = self.first_mouse_y
    dx1 = self.mouse_path[0]
    dy1 = self.mouse_path[1]

    self.last_x_position = dx1
    self.last_y_position = dy1

    position = [[dx0, dy0], [dx0, dy1], [dx1, dy1], [dx1, dy0]]

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    for mode in [GL_QUADS]:

        glBegin(mode)
        if self.first_active in list(bpy.context.selected_objects):
            if self.yellow_color:
                glColor4f(0.62, 0.5, 0.2, 0.5)
            else:
                glColor4f(0.6, 0.2, 0.2, 0.5)
        else :
            glColor4f(0.5, 0.5, 0.5, 0.5)
        for v1, v2 in position:
            glVertex2f(v1, v2)
        glEnd()

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)  



def draw_box(x0, y0, width, height):

    x1 = x0 + width
    y1 = y0 - height/2
    y0 += height/2

    bgR = BC_indicator_color()[0]
    bgG = BC_indicator_color()[1]
    bgB = BC_indicator_color()[2]
    bgA = BC_indicator_color()[3]

    position = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
        
    for mode in [GL_QUADS]:
        glBegin(mode)
        glColor4f(bgR, bgG, bgB, bgA)
        for v1, v2 in position:
            glVertex2f(v1, v2)
        glEnd()

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)     

def draw_button_text(hover, x, y, text):
    blf.position(0, x, y, 0)
    blf.size(0, 10, get_dpi())
    if hover:
        txtcol = bpy.context.user_preferences.themes[0].user_interface.wcol_pie_menu.text
    else:
        txtcol = bpy.context.user_preferences.themes[0].user_interface.wcol_pie_menu.text_sel
    txR = txtcol[0]
    txG = txtcol[1]
    txB = txtcol[2]
    txA = 1.0
    glColor4f(txR, txG, txB, txA)
    blf.draw(0, text)

def draw_point(self, context):

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glColor4f(0.7, 0, 0.87, 0.9)
    region_height, region_width = get_region_dimensions()
    center_point = get_center_point(self, context)
    grid_path_spaceing = bpy.context.scene.BoxCutter_grid_spaceing

    grid_path_x = int(int(center_point[0]) - (grid_path_spaceing *(int((center_point[0] - self.x)/grid_path_spaceing))))
    grid_path_y = int(int(center_point[1]) - (grid_path_spaceing *(int((center_point[1] - self.y)/grid_path_spaceing))))
    
    #glPointSize(4)
    #glBegin(GL_POINTS) 
    glLineWidth(2) 
    glBegin(GL_LINES)
    glVertex2f(grid_path_x - 4, grid_path_y+ 4)
    glVertex2f(grid_path_x + 4, grid_path_y+ 4)

    glVertex2f(grid_path_x + 4, grid_path_y+ 4)
    glVertex2f(grid_path_x + 4, grid_path_y- 4)

    glVertex2f(grid_path_x + 4, grid_path_y- 4)
    glVertex2f(grid_path_x - 4, grid_path_y- 4)

    glVertex2f(grid_path_x - 4, grid_path_y- 4)
    glVertex2f(grid_path_x - 4, grid_path_y+ 4)
    glEnd()
    glLineWidth(1) 

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)