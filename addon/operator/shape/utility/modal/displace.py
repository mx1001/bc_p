import bpy

from math import radians

# from .... utility import modifier
from .. import modifier
from ...... utility import addon, screen


def shape(op, context, event):
    bc = context.scene.bc

    displace = None

    for mod in bc.shape.modifiers:
        if mod.type == 'DISPLACE':
            displace = mod

            break

    if not displace:
        displace = bc.shape.modifiers.new('Displace', 'DISPLACE')
        displace.direction = 'X'

    location = op.view3d['location'].x + op.start['displace']

    displace.strength = location
    op.last['modifier']['displace'] = displace.strength
