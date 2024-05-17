bl_info = {
    "name": "Heightmap Generator",
    "author": "baral",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Heightmap Generator",
    "description": "Generate a heightmap of the selected object or of all .dae files present in choosen directory",
    "warning": "",
    "wiki_url": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
import os
from bpy.props import PointerProperty

from .material_map_generator import (
    Settings,
    MaterialMapGeneratorOperator,
    BatchMaterialMapGeneratorOperator,
    MaterialMapGeneratorPanel,
)


# This allows you to right click on a button and link to documentation
def heightmap_manual_map():
    url_manual_prefix = "https://github.com/BARALLL"
    url_manual_mapping = (("heightmap.generate", "scene_layout/object/types.html"),)
    return url_manual_prefix, url_manual_mapping


classes = [
    Settings,
    MaterialMapGeneratorOperator,
    BatchMaterialMapGeneratorOperator,
    MaterialMapGeneratorPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.settings = PointerProperty(type=Settings)


def unregister():
    del bpy.types.Scene.settings
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
