from bpy.types import Panel

from .properties import PROPS1, PROPS2
from .consts import (
    ui_panel_id, 
    fur_gen_operator_id, 
    fur_copy_anim_operator_id, 
    fur_mask_fixed_operator_id, 
    recalc_anim_pivot_operator_id, 
    fur_gen_uv_by_colors_id,
    recalc_normals_as_ref_object_id,
    fur_copy_vertex_col_operator_id,
    select_twisted_quads_id)

class FurPanel(Panel):
    bl_idname = ui_panel_id
    bl_label = 'Fur tool Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type= 'UI'
    bl_category = 'Fur Tool'
    #bl_context = 'object'

    def draw(self, context):
        box = self.layout.box()
        col = box.column()
        col.label(text="Generate fur")
        for (prop_name, _) in PROPS1:
            row = col.row()
            row.prop(context.scene, prop_name)
        col.operator(fur_gen_operator_id, text="1. Generate")        

        box = self.layout.box()
        col = box.column()
        col.label(text="Hair cards UV tools")
        col.operator(fur_copy_vertex_col_operator_id, text="Copy vert colors Selected->Active")
        for (prop_name, _) in PROPS2:
            row = col.row()
            row.prop(context.scene, prop_name)
        col.operator(fur_gen_uv_by_colors_id, text="Map UV by Vertex color attr")

        box = self.layout.box()
        col = box.column()
        col.label(text="Other tools")
        col.operator(fur_copy_anim_operator_id, text="2. Copy skin Selected->Active")
        col.operator(fur_mask_fixed_operator_id, text="Mask fixed points for sculpting")
        col.operator(recalc_anim_pivot_operator_id, text="err Recalc anim pivot test")
        col.operator(recalc_normals_as_ref_object_id, text="Recalc normals as ref object Active->Selected")
        col.operator(select_twisted_quads_id, text="Select twisted quads")
        