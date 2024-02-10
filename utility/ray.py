import bpy

from math import radians
from mathutils import Matrix, Vector

from . import addon
from . view3d import location2d_to_origin3d, location2d_to_vector3d


class cast:
    origin: Vector = (0, 0)
    direction: Vector = (0, 0)


    def __new__(self, x, y, selected=False, obj=None, mesh_data=None, use_copy=False, transform_by=None, types={'MESH'}):
        context = bpy.context
        self.origin = location2d_to_origin3d(x, y)
        self.direction = location2d_to_vector3d(x, y)
        self.obj = obj
        self.mesh_data = mesh_data
        self.use_copy = use_copy
        self.transform_by = transform_by

        if obj:
            return self.object(self, context)

        elif mesh_data:
            return self.mesh(self, context)

        return self.scene(self, context, selected)


    def object(self, context):
        # returns hit, location, normal, index
        if self.transform_by:
            self.obj.data.transform(self.transform_by)
        return self.obj.ray_cast(self.origin, self.direction,
                depsgraph = bpy.context.evaluated_depsgraph_get())


    def mesh(self, context):
        obj = bpy.data.objects.new(name='snap_mesh', object_data=self.mesh_data)
        bpy.context.scene.collection.objects.link(obj)

        if self.use_copy:
            obj.data = obj.data.copy()
            obj.data.bc.removeable = True

        if self.transform_by:
            obj.data.transform(self.transform_by)

        hit, location, normal, index = obj.ray_cast(self.origin, self.direction, depsgraph=bpy.context.evaluated_depsgraph_get())

        bpy.data.objects.remove(obj)

        del obj

        return hit, location, normal, index


    def scene(self, context, selected, types={'MESH'}):
        original_visible = context.visible_objects[:]
        valid_obj = lambda obj: obj.type in types and (not selected or obj.select_get())
        display = [(obj, obj.display_type) for obj in context.selected_objects if valid_obj(obj)]
        hide = [obj for obj in original_visible if not valid_obj(obj)]

        for obj in hide:
            obj.hide_set(True)

        for obj in display:
            obj[0].display_type = 'SOLID'

        hit, location, normal, index, object, matrix = context.scene.ray_cast(context.view_layer, self.origin, self.direction)

        for obj in hide:
            obj.hide_set(False)

        for obj in display:
            obj[0].display_type = obj[1]

        del original_visible
        del display
        del hide

        return hit, location, normal, index, object, matrix
