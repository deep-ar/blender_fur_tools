import bpy
import mathutils

from .consts import select_twisted_quads_id

class SelectTwistedQuadsOperator(bpy.types.Operator):
    bl_idname = select_twisted_quads_id
    bl_label = 'select_twisted_quads'
    
    def selectTwistedPolygons(self, object:bpy.types.Object):
        om = object.data

        for face in om.polygons:
            v02 = mathutils.Vector(om.vertices[face.vertices[2]].co - om.vertices[face.vertices[0]].co) #сгиб
            v01 = mathutils.Vector(om.vertices[face.vertices[1]].co - om.vertices[face.vertices[0]].co)
            v03 = mathutils.Vector(om.vertices[face.vertices[3]].co - om.vertices[face.vertices[0]].co)

            cross12 = v01.cross(v02)
            cross23 = v02.cross(v03)

            dcross = cross12.dot(cross23)
            if dcross < 0:
                face.select = True
            else:
                face.select  = False

        return


    def execute(self, context):

        if len(bpy.context.selected_objects) > 0:
            for o in bpy.context.selected_objects:
                self.selectTwistedPolygons(o)
        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}