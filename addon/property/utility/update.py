from ... import toolbar

def change_start_operation(option, context):
    # for tool in context.workspace.tools:
        # if tool.idname == tool.name:
            # tool.operator_properties('bc.shape_draw').operation = option.start_operation
    toolbar.options().operation = option.start_operation

    context.workspace.tools.update()


def store_collection(option, context):
    bc = context.scene.bc

    if not bc.running:
        main = 'Cutters'
        if option.collection and option.stored_collection != option.collection and main != option.collection.name:
            option.stored_collection = option.collection

            if option.collection and option.shape and option.shape.name not in option.collection.objects:
                option.shape = option.stored_shape if option.stored_shape and option.stored_shape.name in option.collection.objects else None

            if option.collection and not option.shape and len(option.collection.objects):
                option.shape = option.collection.objects[0]


def store_shape(option, context):
    bc = context.scene.bc

    if not bc.running:
        if option.shape and option.stored_shape != option.shape:
            option.stored_shape = option.shape
