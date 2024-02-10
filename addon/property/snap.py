import bpy

from bpy.types import PropertyGroup, Object, Mesh
from bpy.props import *


class option(PropertyGroup):
    mesh: PointerProperty(type=Mesh)
    display: BoolProperty(default=True)
    location: FloatVectorProperty()
    normal: FloatVectorProperty()
    hit: BoolProperty()
