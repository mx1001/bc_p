import bpy

def set_3d_cursor_location(x, y, z):

    bpy.context.space_data.cursor_location[0] = x
    bpy.context.space_data.cursor_location[1] = y
    bpy.context.space_data.cursor_location[2] = z

def save_3d_cursor_location():

    cursor_x = bpy.context.space_data.cursor_location[0]
    cursor_y = bpy.context.space_data.cursor_location[1]
    cursor_z = bpy.context.space_data.cursor_location[2]

    return cursor_x, cursor_y, cursor_z