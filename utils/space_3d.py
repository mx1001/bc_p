import bpy
import bpy_extras.view3d_utils
from mathutils import Vector

def get_center_point(self, context):
	region = context.region
	rv3d = context.space_data.region_3d
	coord = Vector((0, 0, 0, 0))

	point = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, coord)

	return point