from attr import NOTHING
import bpy
import math

from .consts import fur_copy_vertex_col_operator_id

class CopyVertexColorsOperator(bpy.types.Operator):
    bl_idname = fur_copy_vertex_col_operator_id
    bl_label = 'Copy anim Selected->Active'
    
    def getNearestSourceVertices(self, vCoord):
        minDist = 100000000
        minIdx = -1
        srcV = self.sourceObject.data.vertices
        
        for idx in range(len(srcV)):
            vc = self.sourceObject.matrix_world @ srcV[idx].co
            dist = math.dist(vCoord, vc)
            if dist < minDist:
                minDist = dist
                minIdx =idx
                
        return srcV[minIdx]

    def copyVertColors(self):
        srcColors = self.sourceObject.data.color_attributes.active.data
        dstColors = self.destObject.data.color_attributes.active.data
        
        for v in self.destObject.data.vertices:
            srcV = self.getNearestSourceVertices(self.destObject.matrix_world @ v.co)
            dstColors[v.index].color = srcColors[srcV.index].color



    def execute(self, context):

        if len(bpy.context.selected_objects) == 2 and bpy.context.active_object is not NOTHING:
            self.sourceObject = [value for value in bpy.context.selected_objects if value != bpy.context.active_object][0]
            self.destObject = bpy.context.active_object
            self.copyVertColors()
        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}