import math
import bpy
import bgl
import blf
import bpy_extras.view3d_utils
from mathutils import Vector, Quaternion
from mathutils.geometry import interpolate_bezier
import bmesh
from bpy.props import *
from ... utils.objects import set_active
from ... utils.modifiers import apply_modifiers, create_solidify_modifier
from ... graphic.draw_px import draw_extending_curve
from . draw_utils import set_evet_region, append_vert_to_list, set_saved_region, check_if_moving, boxcutter_show_wire, generate_3d_mesh, set_grid_path, saved_cords
from ... ui.main_panel import boxcutter_enable_hops


def sharpen_active_object():
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


def boxCutter_curve_vert_count():
    return bpy.context.scene.BoxCutter_curve_vert_count

class BoxCutterDrawCurve(bpy.types.Operator):
        """Draw an ngon/curve with the mouse"""
        bl_idname = "boxcutter.draw_curve"
        bl_label = "Box Cutter Draw Ngon/Curve"
        bl_options = {'REGISTER', 'UNDO'}
        
        cut_mode = BoolProperty(name = "Cut Mode",
                              description = "cut mode",
                              default = True)
        
        slice = BoolProperty(name = "Slice",
                             description = "Slice or draw",
                             default = False)
        
        round_corners = BoolProperty(name = "Round corners",
                                     description = "Round corners",
                                     default = False)
        
        resolution = IntProperty(name = "Resolution",
                                 description = "Curve segment resolution",
                                 default = 12, min = 1)
                
        point_radius = FloatProperty(name = "Point radius",
                                     description = "Point radius",
                                     default = 6.0, min = 2.0)
        
        merge_radius = FloatProperty(name = "Merge radius",
                                     description = "Coinciding vertices removal radius",
                                     default = 1.0, min = 0.0)
        
        snap_angle = BoolProperty(name = "Snap angle",
                                  description = "Snap angle",
                                  default = False)
        
        angle_subdivs = IntProperty(name = "Angle subdivs",
                                 description = "Angle subdivisions",
                                 default = 72, min = 2)

        drag_option = 'WEIGHT'
        
        def execute(self, context):
            boxcutter_show_wire(self, context, False)
            generate_3d_mesh(self, context, 'NGON')
            
            if self.first_active in list(bpy.context.selected_objects):
                bpy.context.scene.objects.active = self.first_active

                if self.slice:
                    bpy.ops.boxcutter.bool_split()  
                    if boxcutter_enable_hops():
                        for obj in list(bpy.context.selected_objects):
                            set_active(obj, False)
                            sharpen_active_object()

                    if bpy.context.scene.BoxCutter_split_mesh == True:
                        bpy.ops.object.mode_set(mode = 'EDIT')
                        bpy.ops.mesh.separate(type='LOOSE')
                        bpy.ops.object.mode_set(mode='OBJECT')
                                    
                    set_active(bpy.context.active_object, True, True)
                else:
                    bpy.ops.boxcutter.bool_difference()
                    set_active(self.first_active, True)
                    if boxcutter_enable_hops():
                        sharpen_active_object()

            bpy.context.scene.BoxCutter_shape_moving = False
            bpy.context.scene.BoxCutter_help_item = 'MAIN'

            return {'FINISHED'}

        def modal(self, context, event):
            context.area.tag_redraw()
            
            grid_path_x, grid_path_y = set_grid_path(self,context, event)
            mouse_pos = Vector((grid_path_x, grid_path_y))
            mouse_pos_exact = Vector((event.mouse_region_x, event.mouse_region_y))
            
            is_finished = (event.type in {'RET', 'NUMPAD_ENTER',})
            is_cancelled = (event.type in {'ESC', 'RIGHTMOUSE'})
            
            self.draw_points = (self.drag_mode is None) and (event.shift)
            self.draw_outline = not (event.ctrl or event.shift)
            
            if self.drag_mode is None:
                if event.ctrl:
                    self.add_cursor_point_to_list(context, False)
                    self.set_point_2d(context, mouse_pos, len(self.curve_points)-1)
                else:
                    self.curve_points = self.curve_points[:self.finalized_points]
                    self.update_point_list(context)
            
            if event.type == 'MOUSEMOVE':
                grid_path_x, grid_path_y = set_grid_path(self,context, event)
                self.mouse_path = Vector((grid_path_x, grid_path_y))
                if self.drag_mode == 'MOVE_SHAPE':
                    self.move_shape(context, mouse_pos - self.drag_start)
                    self.drag_start = mouse_pos
                elif self.drag_mode == 'MOVE':
                    self.move_point(context, mouse_pos - self.drag_start)
                    self.drag_start = mouse_pos
                elif self.drag_mode == 'WEIGHT':
                    if self.round_corners:
                        delta_weight = ((mouse_pos_exact - self.drag_start).x / 2.0)
                    else:
                        delta_weight = ((mouse_pos_exact - self.drag_start).x / 80.0)
                        if event.ctrl: delta_weight = round(delta_weight / 0.5) * 0.5
                    self.add_point_weight(context, delta_weight)
                    self.drag_start = mouse_pos_exact
            elif event.type == 'MIDDLEMOUSE': # Alt+Click on tablets
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                self.use_3d_cursor # this line does nothing!
                self.execute(context)
                return {'FINISHED'}
            if event.type == 'LEFTMOUSE':
                if event.value == 'PRESS':
                    if event.shift:
                        self.drag_point_id = self.find_point(mouse_pos_exact)
                        self.drag_mode = self.drag_option
                    elif event.ctrl:
                        if (self.mouse_path - self.curve_points[self.finalized_points-1]["2d"]).magnitude > self.merge_radius:
                            self.add_cursor_point_to_list(context)
                            self.drag_mode = 'MOVE'
                    else:
                        is_finished = True
                    if self.drag_mode == self.drag_option: mouse_pos = mouse_pos_exact
                    self.drag_start = mouse_pos
                    self.drag_start_weight = self.get_point_weight()
                    self.drag_offset = self.get_point_2d() - mouse_pos
                else: # RELEASE
                    if self.finalized_points == 2:
                        if (self.curve_points[0]["2d"] - self.curve_points[1]["2d"]).magnitude <= self.merge_radius:
                            self.finalized_points = 1
                            self.curve_points = self.curve_points[:-1]
                            self.update_point_list(context)
                    self.drag_mode = None

            elif event.type == 'BACK_SPACE':
                if event.value == 'PRESS':
                    if len(self.curve_points) > 1:
                        if len(self.curve_points) > self.finalized_points:
                            if self.finalized_points > 1:
                                self.curve_points.pop(-2)
                                self.finalized_points -= 1
                                self.drag_point_id -= 1
                        else:
                            self.curve_points.pop(-1)
                            self.finalized_points -= 1
                            self.drag_point_id -= 1
                        self.update_point_list(context)
            elif event.type == 'DEL':
                if event.value == 'PRESS':
                    if (self.drag_mode is None) and (len(self.curve_points) > 1):
                        if len(self.curve_points) == self.finalized_points:
                            point_id = self.find_point(mouse_pos_exact)
                            if point_id >= 0:
                                self.curve_points.pop(point_id)
                                self.finalized_points -= 1
                                self.drag_point_id -= 1
                                self.update_point_list(context)
            elif event.type == 'X':
                if event.value == 'PRESS':
                    self.slice = not self.slice
            elif event.type in {'MINUS', 'NUMPAD_MINUS'}:
                if event.value == 'PRESS':
                    dres = (2 if self.round_corners else 1)
                    bpy.context.scene.BoxCutter_curve_vert_count = max(bpy.context.scene.BoxCutter_curve_vert_count-dres, 1);
                    self.update_point_list(context)
            elif event.type in {'EQUAL', 'NUMPAD_PLUS'}:
                if event.value == 'PRESS':
                    dres = (2 if self.round_corners else 1)
                    bpy.context.scene.BoxCutter_curve_vert_count = min(bpy.context.scene.BoxCutter_curve_vert_count+dres, 24);
                    self.update_point_list(context)
            elif event.type == 'Z':
                if event.value == 'PRESS':
                    if event.alt:
                        self.snap_angle = not self.snap_angle
                    elif event.shift:
                        bpy.context.scene.BoxCutter_enable_grid = not bpy.context.scene.BoxCutter_enable_grid
            if event.type == 'SPACE':
                if event.value == 'PRESS':
                    if self.drag_option == 'WEIGHT':
                        self.drag_option = 'MOVE'
                    else:
                        self.drag_option = 'WEIGHT'

            if event.type == 'Q':
                if event.value == 'PRESS':
                    if self.round_corners == False:
                        self.round_corners = True
                    else:
                        self.round_corners = False

            if (event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS') and event.value=='PRESS':
                bpy.context.scene.BoxCutter_curve_vert_count += 1
            elif (event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS') and event.value=='PRESS':
                bpy.context.scene.BoxCutter_curve_vert_count -= 1

            if is_finished or is_cancelled:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                bpy.context.scene.BoxCutter_help_item = 'MAIN'
                if is_finished:
                    self.use_3d_cursor = event.alt
                    self.execute(context)
                    return {'FINISHED'}
                else:
                    return {'CANCELLED'}

            return {'RUNNING_MODAL'}

        def invoke(self, context, event):
            bpy.context.scene.BoxCutter_help_item = 'NGON'
            self.use_3d_cursor = True
            if context.area.type == 'VIEW_3D':
                self.first_active = bpy.context.scene.objects.active
                args = (self, context)
                boxcutter_show_wire(self, context, True)
                self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_extending_curve, args, 'WINDOW', 'POST_PIXEL')

                grid_path_x, grid_path_y = set_grid_path(self,context, event)
                self.mouse_path = Vector((grid_path_x, grid_path_y))

                self.list_location_3d = []
                set_evet_region(self, event, True)
                context.window_manager.modal_handler_add(self)

                self.curve_points = []
                self.finalized_points = 0
                self.add_cursor_point_to_list(context)
                self.add_cursor_point_to_list(context) # immediately draw a line
                
                mouse_pos = Vector((grid_path_x, grid_path_y))
                
                self.drag_mode = 'MOVE'
                self.drag_start = mouse_pos
                self.drag_start_weight = 0.0
                self.drag_offset = self.get_point_2d() - mouse_pos
                #self.drag_point_id = 0 # for starting with a point
                self.drag_point_id = 1 # for starting with a line
                
                self.draw_points = False
                self.draw_outline = False
                
                bpy.context.scene.BoxCutter_curve_vert_count = bpy.context.scene.BoxCutter_curve_vert_count
                self.angle_subdivs = 360.0/bpy.context.scene.BoxCutter_snapping_angle
                
                return {'RUNNING_MODAL'}
            else:
                return {'CANCELLED'}
        
        def find_point(self, pos_2d):
            r = self.point_radius
            for i in range(len(self.curve_points)):
                p = self.curve_points[i]
                d = p["2d"] - pos_2d
                if max(abs(d.x), abs(d.y)) < r:
                    return i
            return -1
        
        def get_point_2d(self, i=None):
            if i is None: i = self.drag_point_id
            if (i < 0) or (i >= len(self.curve_points)): return Vector((0, 0))
            return self.curve_points[self.drag_point_id]["2d"]
        
        def get_point_3d(self, i=None):
            if i is None: i = self.drag_point_id
            if (i < 0) or (i >= len(self.curve_points)): return Vector((0, 0, 0))
            return self.curve_points[self.drag_point_id]["3d"]
        
        def get_point_weight(self, i=None):
            if i is None: i = self.drag_point_id
            if (i < 0) or (i >= len(self.curve_points)): return 0.0
            return self.curve_points[self.drag_point_id]["weight"]
        
        def set_point_2d(self, context, pos2d, i=None):
            if i is None: i = self.drag_point_id
            if i < 0: return
            if self.snap_angle and (len(self.curve_points) > 1):
                pos2d_prev = self.curve_points[(self.drag_point_id-1) % len(self.curve_points)]["2d"]
                angle0 = 0.0
                if (len(self.curve_points) > 2):
                    pos2d_prev2 = self.curve_points[(self.drag_point_id-2) % len(self.curve_points)]["2d"]
                    angle0 = (pos2d_prev - pos2d_prev2).angle_signed(Vector((1,0)), 0.0)
                delta = pos2d - pos2d_prev
                angle = delta.angle_signed(Vector((1,0)), 0.0)
                angle_grid = (math.pi*2)/self.angle_subdivs
                angle = round((angle - angle0)/angle_grid)*angle_grid + angle0
                new_dir = Vector((math.cos(angle), math.sin(angle)))
                pos2d = pos2d_prev + delta.project(new_dir)
            p = self.curve_points[self.drag_point_id]
            p["2d"] = pos2d
            self.update_point_list(context)
        
        def move_point(self, context, delta, i=None):
            if i is None: i = self.drag_point_id
            if i < 0:
                for p in self.curve_points:
                    p["2d"] = p["2d"] + delta
            else:
                p = self.curve_points[self.drag_point_id]
                p["2d"] = p["2d"] + delta
            self.update_point_list(context)
        
        def move_shape(self, context, delta):
            for p in self.curve_points:
                p["2d"] += delta
            self.update_point_list(context)
        
        def clamp_weight(self, weight):
            if self.round_corners:
                return max(weight, 0.0)
            else:
                return min(max(weight, 0.0), 1.0)
        
        def set_point_weight(self, context, weight, i=None):
            if i is None: i = self.drag_point_id
            if i < 0: return
            p = self.curve_points[self.drag_point_id]
            p["weight"] = self.clamp_weight(weight)
            self.update_point_list(context)
        
        def add_point_weight(self, context, delta_weight, i=None):
            if i is None: i = self.drag_point_id
            if i < 0:
                for p in self.curve_points:
                    p["weight"] = self.clamp_weight(p["weight"]+delta_weight)
            else:
                p = self.curve_points[self.drag_point_id]
                p["weight"] = self.clamp_weight(p["weight"]+delta_weight)
            self.update_point_list(context)
        
        def interpolate_curve_segment(self, i, resolution):
            n_points = len(self.curve_points)
            p0h = self.curve_points[(i-1) % n_points]
            p0 = self.curve_points[i]
            p1 = self.curve_points[(i+1) % n_points]
            p1h = self.curve_points[(i+2) % n_points]
            
            weight1 = p0["weight"]
            weight2 = p1["weight"]
            knot1 = p0["2d"]
            knot2 = p1["2d"]
            
            if max(weight1, weight2) <= 1e-6:
                return [knot1, knot2]
            
            if self.round_corners:
                handle1 = p0h["2d"]
                handle2 = p1h["2d"]
                
                #r1 = min(weight1, self.max_radius(handle1, knot1, knot2))
                #r2 = min(weight2, self.max_radius(knot1, knot2, handle2))
                r1 = p0["r"]
                r2 = p1["r"]
                
                vertices = []
                
                n = resolution // 2
                
                if r1 <= 1e-6:
                    vertices.append(p0["2d"])
                else:
                    vertices.extend(self.interpolate_arc(handle1, knot1, knot2, r1, n))
                    if n == 0: vertices = vertices[1:]
                
                if r2 <= 1e-6:
                    vertices.append(p1["2d"])
                else:
                    vertices.extend(self.interpolate_arc(handle2, knot2, knot1, r2, n, reverse=True))
                
                return vertices
            else:
                handle1 = knot1 + (knot2 - p0h["2d"]) * (weight1 * 0.5)
                handle2 = knot2 + (knot1 - p1h["2d"]) * (weight2 * 0.5)
                return interpolate_bezier(knot1, handle1, handle2, knot2, max(resolution, 2))
        
        def max_radius(self, pL, pC, pR):
            dCL = (pL - pC)
            dCR = (pR - pC)
            max_len = min(dCL.magnitude, dCR.magnitude)
            a2 = dCL.angle(dCR, 0.0) * 0.5
            r = math.tan(a2) * max_len
            return r
        
        def max_radius_angle(self, pL, pC, pR):
            dCL = (pL - pC)
            dCR = (pR - pC)
            max_len = min(dCL.magnitude, dCR.magnitude)
            a2 = dCL.angle(dCR, 0.0) * 0.5
            r = math.tan(a2) * max_len
            return r, a2
        
        def interpolate_arc(self, pL, pC, pR, r, n, reverse=False):
            dCL = (pL - pC).normalized()
            dCR = (pR - pC).normalized()
            a2 = dCL.angle(dCR, 0.0) * 0.5
            dCM = (dCL + dCR).normalized()
            t = (0.0 if a2 < 1e-6 else (r / math.sin(a2)))
            dCM_ = dCM * t
            c = pC + dCM_ # center of the circle
            cp = dCM_.project(dCR) # projection on CR
            dR = cp - dCM_
            dM = -dCM * r
            aM = dM.angle_signed(Vector((1,0)), 0.0)
            aR = dR.angle_signed(Vector((1,0)), 0.0)
            da = aR - aM
            if (da > math.pi): da -= math.pi * 2
            if (da < -math.pi): da += math.pi * 2
            if n > 0:
                for i in range(n+1):
                    t = float(i) / float(n)
                    if reverse: t = 1.0 - t
                    a = aM + da * t
                    dr = Vector((r*math.cos(a), r*math.sin(a)))
                    res = c + dr
                    yield res
            else:
                cR = Vector((r*math.cos(aR), r*math.sin(aR)))
                cM = cR.project(dCM)
                if reverse:
                    yield c + cR
                    yield c + cM
                else:
                    yield c + cM
                    yield c + cR
        
        def clamp_radii(self):
            n_points = len(self.curve_points)
            for i in range(n_points):
                pL = self.curve_points[(i-1) % n_points]
                pC = self.curve_points[i]
                pR = self.curve_points[(i+1) % n_points]
                r, a2 = self.max_radius_angle(pL["2d"], pC["2d"], pR["2d"])
                r = min(pC["weight"], r)
                l = (0.0 if a2 < 1e-6 else (r / math.tan(a2)))
                pC["a"] = a2
                pC["r"] = r
                pC["l"] = l
                pC["dl"] = 0.0
            
            for i in range(n_points):
                pA = self.curve_points[i]
                pB = self.curve_points[(i+1) % n_points]
                AB = (pB["2d"] - pA["2d"]).magnitude
                lAB = pA["l"] + pB["l"]
                if lAB <= AB: continue
                dl = (lAB - AB) * 0.5
                pA["dl"] = max(pA["dl"], dl)
                pB["dl"] = max(pB["dl"], dl)
            
            for p in self.curve_points:
                p["l"] = p["l"] - p["dl"]
                p["r"] = math.tan(p["a"]) * p["l"]
        
        def update_point_list(self, context):
            n_points = len(self.curve_points)
            if n_points <= 2:
                interpolated_2d = [p["2d"] for p in self.curve_points]
            else:
                self.clamp_radii()
                interpolated_2d = []
                for i in range(n_points):
                    vertices = self.interpolate_curve_segment(i, bpy.context.scene.BoxCutter_curve_vert_count)
                    for j in range(len(vertices)-1):
                        interpolated_2d.append(vertices[j])
            
            region = context.region
            rv3d = context.space_data.region_3d
            
            self.list_location_3d = []
            v_prev = None
            for v in interpolated_2d:
                if not (v_prev is None):
                    if (v-v_prev).magnitude <= self.merge_radius: continue
                v_3d = bpy_extras.view3d_utils.region_2d_to_location_3d(region, rv3d, v, self.depth_location)
                self.list_location_3d.append(v_3d)
                v_prev = v
        
        def add_cursor_point_to_list(self, context, finalized=True):
            if len(self.curve_points) > self.finalized_points:
                if finalized:
                    self.finalized_points += 1
                return
            
            self.depth_location = bpy.context.scene.cursor_location
            
            self.curve_points.append({"2d":Vector(self.mouse_path), "3d":Vector(), "weight":0.0, "a":0.0, "r":0.0, "l":0.0, "dl":0.0})
            self.drag_point_id = len(self.curve_points)-1
            
            self.update_point_list(context)
            
            if finalized:
                self.finalized_points = len(self.curve_points)
