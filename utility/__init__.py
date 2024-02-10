import time
import traceback

import bpy

name = __name__.partition('.')[0]


def new_type(name='object', default=None, inherent=(), attribute={}, **keyed_argument):
    space = type(name, inherent, attribute)
    space.__new__ = default if default else lambda self: self

    for key, argument in keyed_argument.items():
        setattr(space, key, argument)

    return space


def context_copy(**kargs):
    return new_type(name='context', attribute=bpy.context.copy(), **kargs)


def method_handler(method, arguments=(), identifier='', exit_method=None, exit_arguments=(), return_result=True, return_value={'CANCELLED'}):
    if identifier:
        identifier += ' '

    try:
        if return_result:
            return method(*arguments)

        else:
            method(*arguments)

    except Exception:
        if bpy.context.preferences.addons[name].preferences.debug:
            print(F'\n{name + " "}{identifier}Method Failed:\n')
            traceback.print_exc()

        if exit_method:

            try:
                if return_result:
                    return exit_method(*exit_arguments)

                else:
                    exit_method(*exit_arguments)

            except Exception:
                if bpy.context.preferences.addons[name].preferences.debug:
                    print(F'\n{name + " "}{identifier}Exit Method Failed:\n')
                    traceback.print_exc()

        if return_result:

            try:
                return return_value

            except Exception:
                if bpy.context.preferences.addons[name].preferences.debug:
                    print(F'\n{name + " "}{identifier}Exit Return Value Failed:\n')
                    traceback.print_exc()


def timed_print(*args):
    if bpy.context.preferences.addons[name].preferences.debug:
        print(F'{time.perf_counter()}:', *args)
