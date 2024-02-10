
import os

import bpy
import aud

from ...... utility import addon, screen, view3d


def play(name):
    if not load(name):
        return

    sound = aud.Sound(load(name))
    device = aud.Device()

    device.play(sound)

    preference = addon.preference()
    vol = preference.display.sound_volume
    device.volume = float(vol) / 100


def load(name):
    sound = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'sound', name))
    type = F'.{sound.split(".")[-1]}'

    if type not in bpy.path.extensions_audio:
        print(F'Unable to play audio with this blender build: {type}')
        return None

    return sound
