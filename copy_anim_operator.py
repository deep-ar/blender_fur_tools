from attr import NOTHING
import bpy
import math

from .consts import fur_copy_anim_operator_id

class CopyAnimOperator(bpy.types.Operator):
    bl_idname = fur_copy_anim_operator_id
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

    def getVertexGroup(self, item, name):
        if name in item.vertex_groups:
            return item.vertex_groups[name]
        
        item.vertex_groups.new(name=name)
        return item.vertex_groups[name]
        
        
    def copyAnim(self):
        self.destObject.vertex_groups.clear()    
        n = 0
        
        for v in self.destObject.data.vertices:
            srcV = self.getNearestSourceVertices(self.destObject.matrix_world @ v.co)

            for srcG in srcV.groups:
                sgName = self.sourceObject.vertex_groups[srcG.group].name
                dg = self.getVertexGroup(self.destObject, sgName)
                dg.add([v.index], srcG.weight, "ADD")



    def execute(self, context):

        if len(bpy.context.selected_objects) == 2 and bpy.context.active_object is not NOTHING:
            self.sourceObject = [value for value in bpy.context.selected_objects if value != bpy.context.active_object][0]
            self.destObject = bpy.context.active_object
            self.copyAnim()
        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}