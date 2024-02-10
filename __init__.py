'''
Copyright (C) 2015-2020 Team C All Rights Reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    'name': 'BoxCutter',
    'description': 'BoxCutter 7.16.12: Catlin',
    'author': 'AR, MX, proxe',
    'version': (7, 16, 12),
    'blender': (2, 83, 0),
    'location': 'View3D',
    'wiki_url': 'https://boxcutter-manual.readthedocs.io/',
    'category': '3D View'}

from . import addon


def register():
    addon.register()


def unregister():
    addon.unregister()
