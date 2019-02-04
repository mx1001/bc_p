import bpy
from bgl import *
import blf

from .. utils.blender_ui import get_dpi_factor, get_dpi, get_3d_view_tools_panel_overlay_width

def draw_help(x, y):
    blf.size(0, 12, get_dpi())

    txtcol = bpy.context.user_preferences.themes[0].user_interface.wcol_pie_menu.text

    txR = txtcol[0]
    txG = txtcol[1]
    txB = txtcol[2]
    txA = 1.0
    glColor4f(txR, txG, txB, txA)

    space = 20

    if bpy.context.scene.BoxCutter_help_item == 'MAIN':

        if len(bpy.context.selected_objects) == 1: 
            #draw_box(x+ 147*get_dpi_factor(), y+ 4*get_dpi_factor(), 30*get_dpi_factor(), 16*get_dpi_factor())
            #draw_box(x+ 115*get_dpi_factor(), y+ 4*get_dpi_factor(), 22*get_dpi_factor(), 16*get_dpi_factor())
            blf.position(0, x, y, 0)
            blf.draw(0, 'Draw red shape - hold ctrl + LMB')

            #draw_box(x+ 205*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 30*get_dpi_factor(), 16*get_dpi_factor())
            #draw_box(x+ 173*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 22*get_dpi_factor(), 16*get_dpi_factor())
            #draw_box(x+ 133*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 30*get_dpi_factor(), 16*get_dpi_factor())
            blf.position(0, x, y- space*get_dpi_factor(), 0)
            blf.draw(0, 'Draw yellow shape - hold shift + ctrl + LMB')
        elif len(bpy.context.selected_objects) == 0:
            #draw_box(x+ 151*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 30*get_dpi_factor(), 16*get_dpi_factor())
            #draw_box(x+ 119*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 22*get_dpi_factor(), 16*get_dpi_factor())
            blf.position(0, x, y- space*get_dpi_factor(), 0)
            blf.draw(0, 'Draw gray shape - hold ctrl + LMB')

        else:
            #draw_box(x+ 187*get_dpi_factor(), y+ 4*get_dpi_factor(), 30*get_dpi_factor(), 16*get_dpi_factor())
            #draw_box(x+ 156*get_dpi_factor(), y+ 4*get_dpi_factor(), 22*get_dpi_factor(), 16*get_dpi_factor())
            blf.position(0, x, y, 0)
            blf.draw(0, 'Boolean (difference) ctrl + LMB')

            #draw_box(x+ 206*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 30*get_dpi_factor(), 16*get_dpi_factor())
            #draw_box(x+ 174*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 22*get_dpi_factor(), 16*get_dpi_factor())
            #draw_box(x+ 134*get_dpi_factor(), y+ (4-space)*get_dpi_factor(), 30*get_dpi_factor(), 16*get_dpi_factor())
            blf.position(0, x, y- space*get_dpi_factor(), 0)
            blf.draw(0, 'Boolean (union) - shift + ctrl + LMB')

        #draw_box(x+ 79*get_dpi_factor(), y+ (4-(space*3))*get_dpi_factor(), 14*get_dpi_factor(), 16*get_dpi_factor())
        blf.position(0, x, y- (space*3)*get_dpi_factor(), 0)
        blf.draw(0, 'Change Shape - D')

        #draw_box(x+ 59*get_dpi_factor(), y+ (4-(space*4))*get_dpi_factor(), 20*get_dpi_factor(), 16*get_dpi_factor())
        #draw_box(x+ 90*get_dpi_factor(), y+ (4-(space*4))*get_dpi_factor(), 14*get_dpi_factor(), 16*get_dpi_factor())
        blf.position(0, x, y- (space*4)*get_dpi_factor(), 0)
        blf.draw(0, 'Fast Bisect - ctrl + D')

        #draw_box(x+ 64*get_dpi_factor(), y+ (4-(space*5))*get_dpi_factor(), 28*get_dpi_factor(), 16*get_dpi_factor())
        #draw_box(x+ 101*get_dpi_factor(), y+ (4-(space*5))*get_dpi_factor(), 14*get_dpi_factor(), 16*get_dpi_factor())
        blf.position(0, x, y- (space*5)*get_dpi_factor(), 0)
        blf.draw(0, 'Enable Grid - shift + Z')

        #draw_box(x+ 134*get_dpi_factor(), y+ (4-(space*7))*get_dpi_factor(), 34*get_dpi_factor(), 16*get_dpi_factor())
        #draw_box(x+ 94*get_dpi_factor(), y+ (4-(space*7))*get_dpi_factor(), 24*get_dpi_factor(), 16*get_dpi_factor())
        blf.position(0, x, y- (space*7)*get_dpi_factor(), 0)
        blf.draw(0, 'Snap (grid distance) - shift + wheel (or +/-)')

        #draw_box(x+ 136*get_dpi_factor(), y+ (4-(space*9))*get_dpi_factor(), 34*get_dpi_factor(), 16*get_dpi_factor())
        #draw_box(x+ 102*get_dpi_factor(), y+ (4-(space*9))*get_dpi_factor(), 18*get_dpi_factor(), 16*get_dpi_factor())
        blf.position(0, x, y- (space*9)*get_dpi_factor(), 0)
        blf.draw(0, 'Set boolean mode - alt + wheel (alt + (+/-)')

        blf.size(0, 10, get_dpi())
        blf.position(0, x + 8*get_dpi_factor(), y- (space*10)*get_dpi_factor(), 0)
        blf.draw(0, '(M) = use modifier - (modifier mode)')

        blf.position(0, x + 8*get_dpi_factor(), y- (214)*get_dpi_factor(), 0)
        blf.draw(0, '(C) = use carve - (most stable)')

        blf.position(0, x + 8*get_dpi_factor(), y- (230)*get_dpi_factor(), 0)
        blf.draw(0, '(B) = use bmesh - (least stable)')


    elif bpy.context.scene.BoxCutter_help_item == 'BOX':
        blf.position(0, x, y, 0)
        blf.draw(0, 'Cut Release - LMB')

        blf.position(0, x, y- space*get_dpi_factor(), 0)
        blf.draw(0, 'Cut Depth to cursor - hold alt + release LMB')

        blf.position(0, x, y- (space*3)*get_dpi_factor(), 0)
        blf.draw(0, 'Cancel / END -  RMB or Esc')

        blf.position(0, x, y- (space*5)*get_dpi_factor(), 0)
        blf.draw(0, 'Grid Snapping - shift + Z')

        blf.position(0, x, y- (space*7)*get_dpi_factor(), 0)
        blf.draw(0, 'Move Shape - space')

        blf.position(0, x, y- (space*8)*get_dpi_factor(), 0)
        blf.draw(0, 'Save Shape - ctrl + space')

        blf.position(0, x, y- (space*9)*get_dpi_factor(), 0)
        blf.draw(0, 'Restore Shape - shift + space')

    elif bpy.context.scene.BoxCutter_help_item == 'CIRCLE':
        blf.position(0, x, y, 0)
        blf.draw(0, 'Cut Release - LMB')

        blf.position(0, x, y- space*get_dpi_factor(), 0)
        blf.draw(0, 'Cut Depth to 3d cursor - hold alt + release LMB')

        blf.position(0, x, y- (space*3)*get_dpi_factor(), 0)
        blf.draw(0, 'Cancel / End -  RMB or Esc')

        blf.position(0, x, y- (space*5)*get_dpi_factor(), 0)
        blf.draw(0, 'Grid Snapping - shift + Z')

        blf.position(0, x, y- (space*7)*get_dpi_factor(), 0)
        blf.draw(0, 'Move Shape - space')

        blf.position(0, x, y- (space*8)*get_dpi_factor(), 0)
        blf.draw(0, 'Save Shape - ctrl + space')

        blf.position(0, x, y- (space*9)*get_dpi_factor(), 0)
        blf.draw(0, 'Restore Shape - shift + space')

        blf.position(0, x, y- (space*11)*get_dpi_factor(), 0)
        blf.draw(0, 'Change Vert Count - wheel (or +/-)')


    elif bpy.context.scene.BoxCutter_help_item == 'NGON':

        blf.position(0, x, y+ (space*2)*get_dpi_factor(), 0)
        blf.draw(0, 'start by drawing a line')

        blf.position(0, x, y, 0)
        blf.draw(0, 'Create Point - hold ctrl + LMB')

        blf.position(0, x, y- space*get_dpi_factor(), 0)
        blf.draw(0, 'Finish Cut - press LMB')

        blf.position(0, x, y- (space*2)*get_dpi_factor(), 0)
        blf.draw(0, 'Cut Depth to 3d Cursor - hold alt + LMB')
        
        blf.position(0, x, y- (space*3)*get_dpi_factor(), 0)
        blf.draw(0, 'Toggle Rebool / Cutter - X')

        blf.position(0, x, y- (space*4)*get_dpi_factor(), 0)
        blf.draw(0, 'Cancel / END -  RMB or Esc')
        
        blf.position(0, x, y- (space*5)*get_dpi_factor(), 0)
        blf.draw(0, 'Undo Point - Backspace')
        
        blf.position(0, x, y- (space*6)*get_dpi_factor(), 0)
        blf.draw(0, 'Hold Shift')

        blf.position(0, x + (space)*get_dpi_factor() , y- (space*7)*get_dpi_factor(), 0)
        blf.draw(0, 'Bevel all corners - LMB ')

        blf.position(0, x + (space)*get_dpi_factor() , y- (space*8)*get_dpi_factor(), 0)
        blf.draw(0, 'Bevel single corner - LMB (on blue corner)')

        blf.position(0, x, y- (space*10)*get_dpi_factor(), 0)
        blf.draw(0, 'Toggle Bevel / Move -  space')

        blf.position(0, x, y- (space*12)*get_dpi_factor(), 0)
        blf.draw(0, 'Grid Snapping - shift + Z')
        
        blf.position(0, x, y- (space*13)*get_dpi_factor(), 0)
        blf.draw(0, 'Angle Snapping - alt + Z')
        
        blf.position(0, x, y- (space*15)*get_dpi_factor(), 0)
        blf.draw(0, 'Toggle Bevel / Curve - Q')


def draw_box(x0, y0, width, height):

    x1 = x0 + width
    y1 = y0 - height/2
    y0 += height/2


    position = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
        
    for mode in [GL_QUADS]:
        glBegin(mode)
        glColor4f(0.1, 0.1, 0.1, 0.65)
        for v1, v2 in position:
            glVertex2f(v1, v2)
        glEnd()

    txtcol = bpy.context.user_preferences.themes[0].user_interface.wcol_pie_menu.text

    txR = txtcol[0]
    txG = txtcol[1]
    txB = txtcol[2]
    txA = 1.0
    glColor4f(txR, txG, txB, txA)
    glColor4f(txR, txG, txB, txA)
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)   