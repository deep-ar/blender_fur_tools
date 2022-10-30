from attr import NOTHING
import bpy
import math
import mathutils

from .consts import recalc_normals_as_ref_object_id

class RecalcNormalsAsRefObjectOperator(bpy.types.Operator):
    bl_idname = recalc_normals_as_ref_object_id
    bl_label = 'RecalcNormalsAsRefObjectOperator'
    
        

    def execute(self, context):

        if len(bpy.context.selected_objects) == 2 and bpy.context.active_object is not NOTHING:
            destObject = [value for value in context.selected_objects if value != context.active_object][0]
            sourceObject = context.active_object
            #self.recalcNormals2(sourceObject, destObject)
            for face in destObject.data.polygons:
                p = sourceObject.matrix_world.inverted() @ destObject.matrix_world @ face.center
                result, location, normal, index = sourceObject.closest_point_on_mesh(p)
                normal = sourceObject.matrix_world @ normal
                nv = destObject.matrix_world @ face.normal
                if result and nv.dot(normal) < 0: 
                    face.flip()
                    face.select = True

        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}