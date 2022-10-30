import bpy
import math
import mathutils
import random

from .consts import fur_gen_operator_id
from .properties import PROPS1

class GenFurOperator(bpy.types.Operator):
    bl_idname = fur_gen_operator_id
    bl_label = 'Generate'
    selectedObject:bpy.types.Object = None
    PUFF: float = 0.1
    LEN:float = 2.8
    TRAPECIA: float = 0.3
    DIST = 0
    PUFF_RND = 0.3
    LEN_RND = 0.3
    DIST_RND = 0.3
    TRAPECIA_RND = 0.3

    def getVertexGroup(self, item, name):
        if name in item.vertex_groups:
            return item.vertex_groups[name]
        
        item.vertex_groups.new(name=name)
        return item.vertex_groups[name]

    def getVertexGroupWeights(self, vIdx):
        res = []
        vg:bpy.types.VertexGroupElement
        for vg in self.selectedObject.data.vertices[vIdx].groups:
            res.append((vg.group, vg.weight))

        return res

    def globalVertexCo(self, vIdx)->mathutils.Vector:
        return mathutils.Vector(self.selectedObject.matrix_world @ self.selectedObject.data.vertices[vIdx].co)

    def findBaseEdge(self, face:bpy.types.MeshPolygon, force:mathutils.Vector):
        # выбираем грани со стороны силы
        # для этого берем центр поверхности проецируем -force на поверхность и смотрим с какой гранью пересекаемся
        center = mathutils.Vector()
        for idx in face.vertices:
            center += self.globalVertexCo(idx)
        center /= len(face.vertices)
        
        # потом определяем с какой гранью пересекаемся
        # пересчитываем все точки из центра. и теперь смотри на cross prod 
        # проекцию -force и векторов из центра в точки ребра
        # если cross prod разно направлены, то -forсe между векторов и надо только 
        # определить в направлении -force или обратно. для этого берем dot prod
        forceProjInv:mathutils.Vector = force.project(self.selectedObject.matrix_world @ face.normal) - force
        
        intersectedEdgeIdx = -1
        leadVertexIdx = -1
        for idx in range(len(face.edge_keys)):
            edge = face.edge_keys[idx]
            v0c = self.globalVertexCo(edge[0]) - center
            v1c = self.globalVertexCo(edge[1]) - center
            s = forceProjInv.cross(v0c).dot(forceProjInv.cross(v1c))
            d1 = forceProjInv.dot(v0c)
            d2 = forceProjInv.dot(v1c)
            alpha = abs(forceProjInv.angle(v0c)) + abs(forceProjInv.angle(v1c))
            if s <= 0 and alpha < math.pi:# (d1 > 0 or d2 > 0):
                intersectedEdgeIdx = idx
                if d1 >= d2:
                    leadVertexIdx = edge[0]
                else:
                    leadVertexIdx = edge[1]

        if intersectedEdgeIdx == -1:
            intersectedEdgeIdx = 0
            leadVertexIdx = face.edge_keys[intersectedEdgeIdx][0]

        return intersectedEdgeIdx, leadVertexIdx

    def calcQuadd(self, v0, v1, face:bpy.types.MeshPolygon, force:mathutils.Vector):
        return []
    
    def calcEdgeLen(self, edge):
        v0 = self.globalVertexCo(edge[0])
        v1 = self.globalVertexCo(edge[1])
        d:mathutils.Vector = v1 - v0
        return d.length

    def calcEdgeVector(self, edge, startVertexIdx):
        v0 = self.globalVertexCo(startVertexIdx)
        v1 = self.globalVertexCo([v for v in edge if v != startVertexIdx][0])
        return v1 - v0

    def getFaceBasePoints(self, face:bpy.types.MeshPolygon, distFromEdge:float, force:mathutils.Vector):
        matrixWorld = self.selectedObject.matrix_world
        normal = matrixWorld @ face.normal
        leadEdge, leadVertexIdx = self.findBaseEdge(face, force)
        v0Idx = leadVertexIdx
        v1Idx = [v for v in face.edge_keys[leadEdge] if v != leadVertexIdx][0]

        nextEdge = [edge for edge in face.edge_keys if v0Idx in edge and v1Idx not in edge][0]


        return 0

    def addFaceCard2(self, face:bpy.types.MeshPolygon, distFromEdge:float, furLength:float, furPuff:float, furTrapecia:float, force:mathutils.Vector):
        matrixWorld = self.selectedObject.matrix_world
        normal = matrixWorld @ face.normal

    def addFaceCard(self, face:bpy.types.MeshPolygon, distFromEdge:float, furLength:float, furPuff:float, furTrapecia:float, force:mathutils.Vector):
        matrixWorld = self.selectedObject.matrix_world
        normal = matrixWorld @ face.normal

        leadEdge, leadVertexIdx = self.findBaseEdge(face, force)
        #if leadEdge >=0:!!!!!!!!!
        #face.edge_keys[leadEdge]
        # сгиб 4угольника по линии между 0 и 2 вертексами
        idxInFace = list(face.vertices).index(leadVertexIdx)
        newFacePoints = []
        fixed = []
        newOrder = []
        skinGroups = []
        sourceVertices = []

        #self.calcEdgeVector(face.edge_keys[leadEdge], leadVertexIdx)

        # чтобы не пересекать поверхность нужно расти прямо от грани
        # копируем грань, оставляя лидирующее ребро и поднимая остальные точки
        if len(face.vertices) == 3:
            # v - третья и последняя точка, добавляем 2 точки
            v2Idx = [v for v in face.vertices if v not in face.edge_keys[leadEdge]][0]
            ev = self.calcEdgeVector(face.edge_keys[leadEdge], leadVertexIdx)
            v0 = self.globalVertexCo(leadVertexIdx)
            v1 = v0 + ev
            v02 = self.globalVertexCo(v2Idx) - v0
            v13 = self.globalVertexCo(v2Idx) - v1

            v2p:mathutils.Vector = self.globalVertexCo(v2Idx) - v0
            v2 = self.globalVertexCo(v2Idx) - v2p.project(ev)
            v3 = v2 + ev

            v0 += v02 * distFromEdge
            v2 += v02 * distFromEdge
            v3 += v13 * distFromEdge
            v1 += v13 * distFromEdge

            v02:mathutils.Vector = v2 - v0
            v13 = v3 - v1

            v2 = v0 + v02 * furLength + normal * v02.length * furPuff
            v3 = v1 + v13 * furLength + normal * v13.length * furPuff

            newFacePoints.extend([v0, v2, v3, v1])
            v1Idx = [ i for i in face.edge_keys[leadEdge] if i != leadVertexIdx ][0]
            v0g = self.getVertexGroupWeights(leadVertexIdx)
            v1g = self.getVertexGroupWeights(v1Idx)
            v2g = self.getVertexGroupWeights(v2Idx)
            skinGroups.extend([v0g, v1g, v2g, v2g])
            sourceVertices.append(leadVertexIdx)
            sourceVertices.append(v2Idx)
            sourceVertices.append(v2Idx)
            sourceVertices.append(v1Idx)

            normDir = ev.cross(v02).dot(normal)
            
            if normDir > 0:
                print("flip normals")
                verticesOrder = [0,3,2,1]
                fixed.extend([0,3])
            else:
                verticesOrder = [0,1,2,3]
                fixed.extend([0,3])

            newOrder.extend(verticesOrder)
        else:

            for vIdx in range(len(face.vertices)):
                v = face.vertices[vIdx]
                if v in face.edge_keys[leadEdge]:
                    #ищем смежное
                    for ei in range(len(face.edge_keys)):
                        if ei!=leadEdge and v in face.edge_keys[ei]:
                            vs = [val for val in face.edge_keys[ei] if val != v][0]

                    dv = (self.globalVertexCo(vs) - self.globalVertexCo(v)) * distFromEdge
                    newFacePoints.append(self.globalVertexCo(v) + dv)
                    skinGroups.append(self.getVertexGroupWeights(v))
                    sourceVertices.append(v)
                    fixed.append(vIdx)
                else:
                    e02 = list(filter(lambda edge: v in edge and face.edge_keys[leadEdge][0] in edge, face.edge_keys))
                    e13 = list(filter(lambda edge: v in edge and face.edge_keys[leadEdge][1] in edge, face.edge_keys))
                    if e02 is not None and len(e02) > 0:
                        l02 = self.calcEdgeLen(e02[0])
                        v02 = self.calcEdgeVector(e02[0], face.edge_keys[leadEdge][0])
                        newPointDir = self.globalVertexCo(v) + normal * l02 * furPuff - self.globalVertexCo(face.edge_keys[leadEdge][0])
                        newPointDir = newPointDir - newPointDir.project(self.calcEdgeVector(face.edge_keys[leadEdge], face.edge_keys[leadEdge][0]))
                        newPoint = self.globalVertexCo(face.edge_keys[leadEdge][0]) + newPointDir * furLength + v02 * distFromEdge
                        newFacePoints.append(newPoint)
                        skinGroups.append(self.getVertexGroupWeights(face.edge_keys[leadEdge][0]))
                        sourceVertices.append(face.edge_keys[leadEdge][0])
                    if e13 is not None and len(e13) > 0:
                        l13 = self.calcEdgeLen(e13[0])
                        v13 = self.calcEdgeVector(e13[0], face.edge_keys[leadEdge][1])
                        newPointDir = self.globalVertexCo(v) + normal * l13 * furPuff - self.globalVertexCo(face.edge_keys[leadEdge][1])
                        newPointDir = newPointDir - newPointDir.project(self.calcEdgeVector(face.edge_keys[leadEdge], face.edge_keys[leadEdge][1]))
                        newPoint = self.globalVertexCo(face.edge_keys[leadEdge][1]) + newPointDir * furLength + v13 * distFromEdge
                        newFacePoints.append(newPoint)
                        skinGroups.append(self.getVertexGroupWeights(face.edge_keys[leadEdge][1]))
                        sourceVertices.append(face.edge_keys[leadEdge][1])
                newOrder.append(vIdx)

        #trapecia
        v0idx = fixed[0]
        v1idx = fixed[1]
        #order
        if newOrder[(newOrder.index(v0idx) + 1) % 4] == v1idx:
            #0 1 3 2  or 1 3 2 0 etc...
            v2idx = newOrder[(newOrder.index(v0idx) + 3) % 4]
            v3idx = newOrder[(newOrder.index(v1idx) + 1) % 4]
        else:
            #0 2 3 1  or 2 3 1 0 etc...
            v2idx = newOrder[(newOrder.index(v0idx) + 1) % 4]
            v3idx = newOrder[(newOrder.index(v1idx) + 3) % 4]

        v23:mathutils.Vector = newFacePoints[v3idx] - newFacePoints[v2idx]
        delta = furTrapecia #v23.length * (furTrapecia)
        newFacePoints[v3idx] += v23 * delta / 2
        newFacePoints[v2idx] -= v23 * delta / 2

        return newFacePoints, newOrder, fixed, skinGroups, sourceVertices 


    def randomizeProp(self, propertyName:str, baseValue:float, rndFactor:float):
        prop = [p for p in PROPS1 if p[0] == propertyName][0]
        val = baseValue + (random.random() - 0.5)*rndFactor
        if "min" in prop[1].keywords and val < prop[1].keywords["min"]:val = prop[1].keywords["min"]
        if "max" in prop[1].keywords and val > prop[1].keywords["max"]:val = prop[1].keywords["max"]
        return val

    def emitFurCards(self, object:bpy.types.Object):
        self.selectedObject = object
        force = self.FORCE #mathutils.Vector((0,1,0))
        allVertices = []
        allOrder = []
        allFixed = []
        allSkinGroups = []
        allSourceVertices = []
        allSourceFaces = []

        for face in object.data.polygons:
            furDist = self.randomizeProp("fur_distance", self.DIST,  self.DIST_RND)
            furLength = self.randomizeProp("fur_length", self.LEN,  self.LEN_RND)
            furPuff = self.randomizeProp("fur_puff", self.PUFF,  self.PUFF_RND)
            furTrapecia = self.randomizeProp("fur_trapecia", self.TRAPECIA,  self.TRAPECIA_RND)

            vertices, order, fixed, skinGroups, sourceVertices = self.addFaceCard(face, furDist, furLength, furPuff, furTrapecia, force)
            for idx in range(len(order)):
                order[idx] += len(allVertices)
            for idx in range(len(fixed)):
                fixed[idx] += len(allVertices)
                
            allVertices.extend(vertices)
            allSkinGroups.extend(skinGroups)
            allSourceVertices.append(tuple(sourceVertices))
            allSourceFaces.append(face)
            allOrder.append(tuple(order))
            allFixed.extend(fixed)

        mymesh = bpy.data.meshes.new("furObj")
        furObject:bpy.types.Object = bpy.data.objects.new("furObj", mymesh)
        bpy.context.scene.collection.objects.link(furObject)
        
        # Generate mesh data
        mymesh.from_pydata(allVertices, [], allOrder)
        # Calculate the edges
        mymesh.update(calc_edges=True)
        
        if self.COPY_SKIN:
            vg:bpy.types.VertexGroup
            for vg in object.vertex_groups:
                furObject.vertex_groups.new(name=vg.name)

            for vertIdx in range(len(allSkinGroups)):
                vertGroups = allSkinGroups[vertIdx]
                for vg in vertGroups:
                    groupIdx = vg[0]
                    vertWeight = vg[1]
                    furObject.vertex_groups[groupIdx].add([vertIdx], vertWeight, "ADD")

        vg = self.getVertexGroup(furObject, "FixedPoints")
        vg.add(allFixed, 1, "ADD")

        return furObject, allFixed, allSourceVertices, allSourceFaces

    def genHairCardsUV(self, destObject:bpy.types.Object, fixedPoints):
        if "HairUV" not in destObject.data.uv_layers:
            destObject.data.uv_layers.new(name="HairUV", do_init=True)
        
        for face in destObject.data.polygons:
            zone = ([0,0], [0, 0.5], [0.5, 0], [0.5, 0.5])[random.randint(0,3)]
            flip = (True, False)[random.randint(0,1)]
            
            #face_uvs = zip(face.vertices, face.loop_indices)
            #find top
            for i0 in range(len(face.vertices)):
                i1 = i0+1
                if i1 >= len(face.vertices):
                    i1 = 0
                i2 = i1+1
                if i2 >= len(face.vertices):
                    i2 = 0
                i3 = i2+1
                if i3 >= len(face.vertices):
                    i3 = 0
                
                v0 = face.vertices[i0]
                loop0_idx = face.loop_indices[i0]
                v1 = face.vertices[i1]
                loop1_idx = face.loop_indices[i1]
                v2 = face.vertices[i2]
                loop2_idx = face.loop_indices[i2]
                v3 = face.vertices[i3]
                loop3_idx = face.loop_indices[i3]
                
                if v0 in fixedPoints and v1 in fixedPoints: #check FixedGroup
                    if flip:
                        destObject.data.uv_layers["HairUV"].data[loop0_idx].uv = mathutils.Vector([zone[0] + 0, zone[1] + 0.5])
                        destObject.data.uv_layers["HairUV"].data[loop1_idx].uv = mathutils.Vector([zone[0] + 0.5, zone[1] + 0.5])
                        destObject.data.uv_layers["HairUV"].data[loop2_idx].uv = mathutils.Vector([zone[0] + 0.5, zone[1] + 0])
                        destObject.data.uv_layers["HairUV"].data[loop3_idx].uv = mathutils.Vector([zone[0] + 0, zone[1] + 0])
                    else:                    
                        destObject.data.uv_layers["HairUV"].data[loop0_idx].uv = mathutils.Vector([zone[0] + 0.5, zone[1] + 0.5])
                        destObject.data.uv_layers["HairUV"].data[loop1_idx].uv = mathutils.Vector([zone[0] + 0, zone[1] + 0.5])
                        destObject.data.uv_layers["HairUV"].data[loop2_idx].uv = mathutils.Vector([zone[0] + 0, zone[1] + 0])
                        destObject.data.uv_layers["HairUV"].data[loop3_idx].uv = mathutils.Vector([zone[0] + 0.5, zone[1] + 0])


    def copySourceUV(self, srcObject:bpy.types.Object, destObject:bpy.types.Object, sourceVertices, sourceFaces):
        
        if len(destObject.data.polygons) == len(sourceFaces) and len(destObject.data.polygons) == len(sourceVertices):
            if "srcUV" not in destObject.data.uv_layers:
                destObject.data.uv_layers.new(name="srcUV", do_init=True)

            for idx in range(len(sourceFaces)):
                destFace = destObject.data.polygons[idx]
                sourceFace = sourceFaces[idx]

                for lIdx in range(3):
                    dIdx = destFace.loop_indices[lIdx]
                    sIdx = sourceFace.loop_indices[lIdx]
                    destObject.data.uv_layers["srcUV"].data[dIdx].uv = srcObject.data.uv_layers.active.data[sIdx].uv

                dIdx = destFace.loop_indices[3]
                if len(sourceFace.loop_indices) > 3:
                    sIdx = sourceFace.loop_indices[3]
                else:
                    sIdx = sourceFace.loop_indices[2]

                destObject.data.uv_layers["srcUV"].data[dIdx].uv = srcObject.data.uv_layers.active.data[sIdx].uv


    def execute(self, context):
        self.PUFF = context.scene.fur_puff
        self.LEN = context.scene.fur_length
        self.TRAPECIA = context.scene.fur_trapecia
        self.DIST = context.scene.fur_distance
        self.PUFF_RND = context.scene.fur_puff_random
        self.LEN_RND = context.scene.fur_length_random
        self.TRAPECIA_RND = context.scene.fur_trapecia_random
        self.DIST_RND = context.scene.fur_distance_random
        self.COPY_SKIN = context.scene.fur_copy_skin
        
        if context.scene.fur_force_ref is not None:
            self.FORCE = -context.scene.fur_force_ref.location
        else:
            self.FORCE = mathutils.Vector((0, 1, 0))

        if len(bpy.context.selected_objects) > 0:
            for o in bpy.context.selected_objects:
                fur, fixedPoints, allSourceVertices, sourceFaces = self.emitFurCards(o)
                self.genHairCardsUV(fur, fixedPoints)
                self.copySourceUV(o, fur, allSourceVertices, sourceFaces)
        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}