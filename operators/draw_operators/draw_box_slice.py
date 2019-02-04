import bpy
import bgl
import blf
import bpy_extras.view3d_utils
from mathutils import Vector
import bmesh
from bpy.props import *
from ... utils.objects import set_active
from ... utils.modifiers import apply_modifiers, create_solidify_modifier
from ... graphic.draw_px import draw_extending_box
from ... ui.main_panel import boxcutter_enable_hops
from . draw_utils import set_evet_region, append_vert_to_list, set_saved_region, check_if_moving, boxcutter_show_wire, generate_3d_mesh, saved_cords, set_grid_path

class BoxSlicerDrawPoly(bpy.types.Operator):
        """Draw a box from 2d shape """
        bl_idname = "boxcutter.draw_slicebox"
        bl_label = "Box Slicer Draw Poly"
        bl_options = {'REGISTER', 'UNDO'}

        cut_mode = BoolProperty(name = "Cut Mode",
                              description = "cut mode",
                              default = True)

        def execute(self, context):

            boxcutter_show_wire(self, context, False)
            generate_3d_mesh(self, context, 'BOX')

            if self.first_active in list(bpy.context.selected_objects):
                bpy.context.scene.objects.active = self.first_active
                bpy.ops.boxcutter.bool_split()  
                if boxcutter_enable_hops():
                    for obj in list(bpy.context.selected_objects):
                        set_active(obj, False)
                        object = bpy.context.active_object
                        if object.hops.status in ("CSHARP", "SUBSHARP"):
                            bpy.ops.hops.soft_sharpen()

                        if object.hops.status == "UNDEFINED":
                            if bpy.context.scene.BoxCutter_bool_method == 'CARVEMOD':
                                bpy.ops.hops.soft_sharpen()
                            else:
                                bpy.ops.hops.complex_sharpen()

                        if object.hops.status == "CSTEP":
                            if bpy.context.scene.BoxCutter_bool_method == 'BMESH':
                                bpy.ops.object.editmode_toggle()
                                bpy.ops.mesh.hide(unselected=True)
                                bpy.ops.mesh.select_all(action='DESELECT')
                                bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                                bpy.ops.transform.edge_bevelweight(value=1)
                                bpy.ops.mesh.mark_sharp()
                                bpy.ops.object.editmode_toggle()
                            else:
                                bpy.ops.step.sstep()

                if bpy.context.scene.BoxCutter_split_mesh == True:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.separate(type='LOOSE')
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                                
                set_active(bpy.context.active_object, True, True)

            bpy.context.scene.BoxCutter_shape_moving = False
            bpy.context.scene.BoxCutter_help_item = 'MAIN'
            return {'FINISHED'}

        def cancel(self, context):
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.list_location_3d[:] = []
            bpy.context.scene.BoxCutter_shape_moving = False
            bpy.context.scene.BoxCutter_help_item = 'MAIN'

        def modal(self, context, event):
            context.area.tag_redraw()
            if event.type == 'MOUSEMOVE':
                grid_path_x, grid_path_y = set_grid_path(self,context, event)
                self.mouse_path = Vector((grid_path_x, grid_path_y))

            elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE' and not event.alt :

                check_if_moving(self, context, event)

                set_evet_region(self, event, False)
                append_vert_to_list(self, context, self.mouse_path[0], self.mouse_path[1])
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                self.use_3d_cursor = False
                self.execute(context)

                return {'FINISHED'}

            elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE' and event.alt:

                check_if_moving(self, context, event)

                set_evet_region(self, event, False)
                append_vert_to_list(self, context,self.mouse_path[0], self.mouse_path[1])
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                self.execute(context)

                return {'FINISHED'}

            elif event.type == 'RIGHTMOUSE':
                self.cancel(context)
                return {'CANCELLED'}


            elif event.type in {'ESC'}:
                self.cancel(context)
                return {'CANCELLED'}


            if event.type == 'SPACE' and event.value == 'PRESS' and not event.shift and not event.ctrl:
                self.savedx = -(self.mouse_path[0] - self.first_mouse_x)
                self.savedy = -(self.mouse_path[1] - self.first_mouse_y)

            
                if bpy.context.scene.BoxCutter_shape_moving == False:
                    bpy.context.scene.BoxCutter_shape_moving = True
                elif bpy.context.scene.BoxCutter_shape_moving == True:
                    bpy.context.scene.BoxCutter_shape_moving = False

            elif event.type == 'SPACE' and event.value == 'PRESS' and not event.ctrl and event.shift:
                self.savedx = saved_cords[0]
                self.savedy = saved_cords[1]
                bpy.context.scene.BoxCutter_shape_moving = True


            elif event.type == 'SPACE' and event.value == 'PRESS' and event.ctrl and not event.shift:
                self.savedx = -(self.mouse_path[0] - self.first_mouse_x)
                self.savedy = -(self.mouse_path[1] - self.first_mouse_y)

                saved_cords[0] = self.savedx
                saved_cords[1] = self.savedy

                bpy.context.scene.BoxCutter_shape_moving = True

            elif event.shift and event.type == "Z" and event.value=='PRESS':
                if bpy.context.scene.BoxCutter_enable_grid == False:
                    bpy.context.scene.BoxCutter_enable_grid = True
                else:
                    bpy.context.scene.BoxCutter_enable_grid = False


            return {'RUNNING_MODAL'}

        def invoke(self, context, event):
            bpy.context.scene.BoxCutter_help_item = 'BOX'

            if bpy.context.scene.BoxCutter_shape_moving == True:
                self.savedx = saved_cords[0]
                self.savedy = saved_cords[1]

            self.yellow_color = True
            self.use_3d_cursor = True
            if context.area.type == 'VIEW_3D':
                self.first_active = bpy.context.scene.objects.active
                boxcutter_show_wire(self, context, True)
                args = (self, context)
                self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_extending_box, args, 'WINDOW', 'POST_PIXEL')

                grid_path_x, grid_path_y = set_grid_path(self,context, event)
                self.mouse_path = Vector((grid_path_x, grid_path_y))

                self.list_location_3d = []
                set_evet_region(self, event, True)
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                self.report({'WARNING'}, "View3D not found, cannot run operator")
                return {'CANCELLED'}


