import bpy

def append_to_list(menuname, y, name, x, listname):
    menu = menuname
    if not menu in listname:
        newmenu = {}
        newmenu['name'] = name
        newmenu['x'] = x
        newmenu['y'] = y
        listname[menu] = newmenu

def remove_from_list(menuname, listname):
    del(listname[menuname])
