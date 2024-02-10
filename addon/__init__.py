from . import icon, operator, panel, property, header, keymap, pie, toolbar


def register():
    property.preference.register()
    property.register()

    operator.register()
    panel.register()
    pie.register()
    toolbar.register()

    keymap.register()

    header.add()
    toolbar.add()


def unregister():
    property.preference.unregister()
    property.unregister()

    operator.unregister()
    panel.unregister()
    pie.unregister()
    toolbar.unregister()

    keymap.unregister()

    header.remove()
    toolbar.remove()
