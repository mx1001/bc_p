import bpy

from . import addon


def system_dpi(ui_scale=True):
    preference = bpy.context.preferences
    system = preference.system

    dpi = system.dpi * system.pixel_size

    if ui_scale:
        dpi *= preference.view.ui_scale

    return dpi


def dpi_factor(rounded=False, integer=False, ui_scale=True, min=1.0):
    factor = system_dpi(ui_scale=ui_scale) / 72 if addon.preference().behavior.use_dpi_factor else 1

    if factor < min:
        factor = min

    if rounded:
        factor = round(factor)

    if integer:
        factor = int(factor)

    return factor
