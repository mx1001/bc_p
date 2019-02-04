# -*- coding: utf-8 -*-

'''
Copyright (C) 2015 YOUR NAME
YOUR@MAIL.com

Created by YOUR NAME

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "BoxCutter",
    "description": "Box Cutter 4: Plasmacutter",
    "author": "AR, MX, JL, EA, dairin0d, AgentX",
    "version": (0, 4, 0),
    "blender": (2, 77, 0),
    "location": "View3D",
    #"warning": "Experimental Box Cutter",
    "wiki_url": "https://masterxeon1001.com/2016/04/26/box-cutter-guide-v1/",
    "category": "Object" }
        
import bpy 
import os
from . import developer_utils
from . register import register_panel, unregister_panel

modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



addon_keymaps = []

def register_qkeymap():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")

    kmi = km.keymap_items.new('wm.call_menu', 'E', 'PRESS', ctrl = False, shift = False, alt=True)
    kmi.properties.name = "boxcutter_menu"

    kmi = km.keymap_items.new('wm.call_menu_pie', 'A', 'PRESS', ctrl = False, shift = False, alt=True)
    kmi.properties.name = "boxcutter_pie_menu"

    q_addon_keymaps.append(km)

def unregister_qkeymap():
    wm = bpy.context.window_manager
    for km in q_addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    q_addon_keymaps.clear()


def register():
    
    bpy.utils.register_module(__name__)         
    
    kc = bpy.context.window_manager.keyconfigs.addon
   
    # create the mode switch menu hotkey
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')                              
    
    kmi = km.keymap_items.new('boxcutter.draw_boolean_layout', 'W', 'PRESS', ctrl = False, shift = False, alt=True)
    kmi.active = True
    addon_keymaps.append((km, kmi))    

    register_panel()

def unregister():

    bpy.utils.unregister_module(__name__)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    unregister_panel()