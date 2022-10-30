import bpy
import bmesh

from .consts import fur_mask_fixed_operator_id

class MaskFixedOperator(bpy.types.Operator):
    bl_idname = fur_mask_fixed_operator_id
    bl_label = 'Mask fixed points for sculpting'
    
    def maskVertices(self, object:bpy.types.Object):
        Om = object.data
        if "FixedPoints" not in object.vertex_groups: return

        fidx = object.vertex_groups["FixedPoints"].index

        vgroups = [v.groups for v in object.data.vertices]
        vertm = [fidx in [g.group for g in vg] for vg in vgroups]
        
        bm = bmesh.new()
        bm.from_mesh(Om)
        if not bm.verts.layers.paint_mask:
            m = bm.verts.layers.paint_mask.new()
        else:
            m = bm.verts.layers.paint_mask[0]
        
        for i, i2 in zip(bm.verts, vertm):
            i[m] = i2
        bm.to_mesh(Om)
        bm.clear()
        Om.update()


    def execute(self, context):

        if len(bpy.context.selected_objects) > 0:
            for o in bpy.context.selected_objects:
                self.maskVertices(o)
        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}