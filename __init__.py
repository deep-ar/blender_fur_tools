# see https://medium.com/geekculture/creating-a-custom-panel-with-blenders-python-api-b9602d890663

bl_info = {
        "name": "Fur tools",
        "description": "Fur tools.",
        "author": "PVS",
        "version": (1, 0),
        "blender": (3, 2, 0),
        "location": "Properties > Object > My Awesome Panel",
        "warning": "", # used for warning icon and text in add-ons panel
        "wiki_url": "",
        "category": "Object"
        }

import bpy

from .select_twisted_quads_operator import SelectTwistedQuadsOperator

from .copy_vertex_colors import CopyVertexColorsOperator

from .recalc_normals_as_ref_object import RecalcNormalsAsRefObjectOperator

from .gen_uv_by_colors_operator import GenUVByVertexColorsOperator

from .recalc_anim_pivot_operator import RecalcAnimPivotOperator

from .mask_fixed_operator import MaskFixedOperator

from .copy_anim_operator import CopyAnimOperator
from .ui import FurPanel
from . import properties
from .gen_fur2_operator import GenFurOperator

CLASSES = [
    GenFurOperator,
    CopyAnimOperator,
    FurPanel,
    MaskFixedOperator,
    RecalcAnimPivotOperator,
    GenUVByVertexColorsOperator,
    RecalcNormalsAsRefObjectOperator,
    CopyVertexColorsOperator,
    SelectTwistedQuadsOperator
]

def register():
    properties.register()
    for cls in CLASSES:
        bpy.utils.register_class(cls)

def unregister():
    properties.unregister()
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()