import bpy
from bgl import *
import blf
import bpy_extras.view3d_utils
import math
from .. preferences import BC_border_color, BC_indicator_color
from mathutils import Vector
from .. utils.blender_ui import get_dpi_factor, get_dpi


def draw_logo_boxcutter():

    bgR = BC_indicator_color()[0]
    bgG = BC_indicator_color()[1]
    bgB = BC_indicator_color()[2]
    bgA = BC_indicator_color()[3]

    rw = bpy.context.region.width
    rh = bpy.context.region.height
    d = get_dpi_factor()
    x = - 70 *d
    y = 16 *d

    glColor4f(bgR, bgG, bgB, bgA)

    '''glBegin(GL_TRIANGLE_FAN)
                glVertex2f(rw + 0 + x, rh - (13*d + y))
                glVertex2f(rw + 2.5*d + x, rh - (13*d + y))
                glVertex2f(rw + 2.5*d + x, rh - (4*d + y))
                glVertex2f(rw + 3*d + x, rh - (3*d + y))
                glVertex2f(rw + 1.7*d + x, rh - (1.7*d + y))
                glVertex2f(rw + 0 + x, rh - (3*d + y))
                glEnd()
            
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(rw + 13*d + x, rh - (0 + y))
                glVertex2f(rw + 13*d + x, rh - (2.5*d + y))
                glVertex2f(rw + 4*d + x, rh - (2.5*d + y))
                glVertex2f(rw + 3*d + x, rh - (3*d + y))
                glVertex2f(rw + 1.7*d + x, rh - (1.7*d + y))
                glVertex2f(rw + 3*d + x, rh - (0 + y))
                glEnd()'''



    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw+ 4*d + x, rh - (4*d + y))
    glVertex2f(rw+ 26*d + x, rh - (26*d + y))
    glVertex2f(rw+ 4*d + x, rh - (26*d + y))
    glEnd()
    
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw+ 9*d + x, rh - (8*d + y))
    glVertex2f(rw+ 22*d + x, rh - (8*d + y))
    glVertex2f(rw+ 20*d + x, rh - (10*d + y))
    glVertex2f(rw+ 9*d + x, rh - (10*d + y))
    glEnd()
    
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw+ 22*d + x, rh - (8*d + y))
    glVertex2f(rw+ 20*d + x, rh - (10*d + y))
    glVertex2f(rw+ 20*d + x, rh - (21*d + y))
    glVertex2f(rw+ 22*d + x, rh - (21*d + y))
    glEnd()
    

    '''x = x +30 *d 
            
            
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(rw- 0 + x, rh - (13*d + y))
                glVertex2f(rw- 2.5*d + x, rh - (13*d + y))
                glVertex2f(rw- 2.5*d + x, rh - (4*d + y))
                glVertex2f(rw- 3*d + x, rh - (3*d + y))
                glVertex2f(rw- 1.7*d + x, rh - (1.7*d + y))
                glVertex2f(rw- 0 + x, rh - (3*d + y))
                glEnd()
            
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(rw- 13*d + x, rh - (0 + y))
                glVertex2f(rw- 13*d + x, rh - (2.5*d + y))
                glVertex2f(rw- 4*d + x, rh - (2.5*d + y))
                glVertex2f(rw- 3*d + x, rh - (3*d + y))
                glVertex2f(rw- 1.7*d + x, rh - (1.7*d + y))
                glVertex2f(rw- 3*d + x, rh - (0 + y))
                glEnd()
            
            
            
            
                x = - 70 *d
                y = y + 30*d
            
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(rw + 0 + x, rh - (-13*d + y))
                glVertex2f(rw + 2.5*d + x, rh - (-13*d + y))
                glVertex2f(rw + 2.5*d + x, rh - (-4*d + y))
                glVertex2f(rw + 3*d + x, rh - (-3*d + y))
                glVertex2f(rw + 1.7*d + x, rh - (-1.7*d + y))
                glVertex2f(rw + 0 + x, rh - (-3*d + y))
                glEnd()
            
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(rw + 13*d + x, rh - (-0 + y))
                glVertex2f(rw + 13*d + x, rh - (-2.5*d + y))
                glVertex2f(rw + 4*d + x, rh - (-2.5*d + y))
                glVertex2f(rw + 3*d + x, rh - (-3*d + y))
                glVertex2f(rw + 1.7*d + x, rh - (-1.7*d + y))
                glVertex2f(rw + 3*d + x, rh - (-0 + y))
                glEnd()




    x = x +30 *d 

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw- 0 + x, rh - (-13*d + y))
    glVertex2f(rw- 2.5*d + x, rh - (-13*d + y))
    glVertex2f(rw- 2.5*d + x, rh - (-4*d + y))
    glVertex2f(rw- 3*d + x, rh - (-3*d + y))
    glVertex2f(rw- 1.7*d + x, rh - (-1.7*d + y))
    glVertex2f(rw- 0 + x, rh - (-3*d + y))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw- 13*d + x, rh - (0 + y))
    glVertex2f(rw- 13*d + x, rh - (-2.5*d + y))
    glVertex2f(rw- 4*d + x, rh - (-2.5*d + y))
    glVertex2f(rw- 3*d + x, rh - (-3*d + y))
    glVertex2f(rw- 1.7*d + x, rh - (-1.7*d + y))
    glVertex2f(rw- 3*d + x, rh - (0 + y))
    glEnd()'''