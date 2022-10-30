from attr import NOTHING
import bpy
import math
import mathutils

from .consts import recalc_anim_pivot_operator_id

# just start of work. 


newPivotBoneName ="weasel_r_Toe-nub_bone"
rootBoneName = "weasel_Pelvis_bone"

class RecalcAnimPivotOperator(bpy.types.Operator):
    bl_idname = recalc_anim_pivot_operator_id
    bl_label = 'Recalc anim pivot'
    

    def pMatrix(self, bone):
        if bone.parent is not None and bone.parent.name != rootBoneName:
            return self.pMatrix(bone.parent) @ bone.matrix
        else:
            return bone.matrix

    def recalcAnim(self):
        sce = bpy.context.scene
        ob = bpy.context.object

        #refval
        sce.frame_set(sce.frame_start)
        pbone = ob.pose.bones[newPivotBoneName]
        refPos = self.pMatrix(pbone) @ pbone.location

        for f in range(sce.frame_start, sce.frame_end+1):
            sce.frame_set(f)

            pbone = ob.pose.bones[newPivotBoneName]
            rbone = ob.pose.bones[rootBoneName]
            
            pco = self.pMatrix(pbone) @ pbone.location
            delta = pco - refPos
            
            mdelta =  self.pMatrix(pbone) @ delta

            if f > 353:
                rbone.location -= mdelta
            else:    
                rbone.location -= mdelta

            rbone.location = mathutils.Vector((0,0,0))
            rbone.keyframe_insert(data_path="location", frame = f)


    def execute(self, context):

        if len(bpy.context.selected_objects) > 0:
            self.recalcAnim()
        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}