from array import array
import bpy
import math
import mathutils
import bmesh

from .consts import fur_gen_uv_by_colors_id

class TColor:
    val:mathutils.Color
    paletteColor:any
    threshold:float

    def __init__(self, col:mathutils.Color, threshold):
        self.val = col
        self.threshold = threshold
    
    def nonZero(self, val):
        if val ==0:
            return 0.001 #self.threshold
        else:
            return val

    def __eq__(self, other) -> bool:
        return (abs(self.val.r - other.val.r) / self.nonZero(self.val.r) < self.threshold and
        abs(self.val.g - other.val.g) / self.nonZero(self.val.g) < self.threshold and
        abs(self.val.b - other.val.b) / self.nonZero(self.val.b) < self.threshold)

    def getDist(self, col):
        return math.sqrt(col.r * col.r + col.b * col.b + col.g * col.g)

    def __lt__(self, other):
        if self.__eq__(other):
            return False
        else:
            return self.getDist(self.val) < self.getDist(other.val)

    def __le__(self, other):
        if self.__eq__(other):
            return True
        else:
            return self.getDist(self.val) < self.getDist(other.val)

    def __gt__(self, other):
        if self.__eq__(other):
            return False
        else:
            return self.getDist(self.val) > self.getDist(other.val)

    def __ge__(self, other):
        if self.__eq__(other):
            return True
        else:
            return self.getDist(self.val) > self.getDist(other.val)



class VertUV:
    vertIdx:int
    uv:any
    color:mathutils.Color
    tColor:TColor

    def __init__(self, vIdx, vUv, tcol):
        self.vertIdx = vIdx
        self.uv = vUv
        self.color = tcol.val
        self.tColor = tcol

class CardsGroup:
    cards:array
    def __init__(self):
        self.cards = []

class FLoop:
    center:mathutils.Vector
    p_ld:VertUV
    p_rd:VertUV
    p_lu:VertUV
    p_ru:VertUV
    allvUvs:array

    def __init__(self, vuvs):
        #getleft up point
        self.allvUvs = vuvs
        p = sorted(vuvs, key=lambda vuv: vuv.uv.x)
        left = sorted(p[0:2], key=lambda vuv: vuv.uv.y)
        right = sorted(p[2:4], key=lambda vuv: vuv.uv.y)
        self.p_ld = left[0]
        self.p_lu = left[1]
        self.p_rd = right[0]
        self.p_ru = right[1]

        self.center = mathutils.Vector([0,0])
        for vuv in vuvs:
            self.center += vuv.uv
        self.center /= len(vuvs)
        
class HairCard:
    vertices: array
    faces: array
    idx:int
    faceColors:array
    bottomColor:TColor
    upColor:TColor
    uvHeight:float
    uvWidth:float
    fLoops:array
    topX:float
    topY:float
    pointsCount:int

    def __init__(self, newIdx:int) -> None:
        self.idx = newIdx
        self.vertices = []
        self.faces = []

    def updateUVs(self, deltaX, deltaY):
        for f in self.fLoops:
            for vuv in f.allvUvs:
                vuv.uv.x += deltaX
                vuv.uv.y += deltaY
                
        return

    def updateUVs2(self, deltaX, deltaY, scale, obj:bpy.types.Object):
        #in object mode
        for f in self.faces:
            for loop in obj.data.polygons[f].loop_indices:
                x = obj.data.uv_layers["GradientsUV"].data[loop].uv.x
                x = (x - self.topX + deltaX) * scale
                obj.data.uv_layers["GradientsUV"].data[loop].uv.x = x

                y = obj.data.uv_layers["GradientsUV"].data[loop].uv.y
                y = (y - self.topY + self.uvHeight + deltaY) * scale
                obj.data.uv_layers["GradientsUV"].data[loop].uv.y = y
                #print("face", f, "new coords", x, y)
        return

    
    def getPointByIndex(self, index:int):

        cnt = 0
        for loop in self.fLoops:
            cnt += 4
            if index < cnt:
                points = [loop.p_ld, loop.p_lu, loop.p_ru, loop.p_rd]
                return points[ index - (cnt - 4)]

        return

    def calcFaceColors(self, obj:bmesh.types.BMesh, allTColors:array):

        #calc faces order and lef min max and right min max vertices
        self.fLoops = []
        self.pointsCount = 0
        uv_layer = obj.loops.layers.uv["GradientsUV"]
        for f in self.faces:
            vuvs = []
            for v in obj.faces[f].loops:
                uv = v[uv_layer].uv
                vuv = VertUV(v.vert.index, uv, allTColors[v.vert.index])
                vuvs.append(vuv)

            if len(vuvs)>0:
                self.fLoops.append(FLoop(vuvs))
            
            self.pointsCount += len(vuvs)

        self.fLoops = sorted(self.fLoops, key=lambda fl: fl.center.y)
        #min max gradient
        self.bottomColor = self.fLoops[0].p_lu.tColor.paletteColor # bottomColor # self.avgLoopColor(self.fLoops[2], self.fLoops[2].p_ld.tColor.threshold)
        self.upColor = self.fLoops[-1].p_ld.tColor.paletteColor # upColor #self.avgLoopColor(self.fLoops[-1], self.fLoops[-1].p_lu.tColor.threshold)
        self.uvHeight = abs(self.fLoops[-1].p_lu.uv.y - self.fLoops[0].p_ld.uv.y)
        self.uvWidth = abs(self.fLoops[0].p_ru.uv.x - self.fLoops[0].p_lu.uv.x)
        self.topX = self.fLoops[0].p_lu.uv.x
        self.topY = self.fLoops[-1].p_lu.uv.y
        return

class GenUVByVertexColorsOperator(bpy.types.Operator):
    bl_idname = fur_gen_uv_by_colors_id
    bl_label = 'Gen UV by Vertex color attr'
    selectedObject:bpy.types.Object
    bMesh:bmesh.types.BMesh
    allTColors:array

    def createColorAttrsByPalette(self, allColors):

        if "AdjustedVColors" in self.selectedObject.data.color_attributes:
            self.selectedObject.data.color_attributes.remove(self.selectedObject.data.color_attributes["AdjustedVColors"])
        self.selectedObject.data.color_attributes.new("AdjustedVColors", "FLOAT_COLOR", "POINT")
        
        allVerts = self.selectedObject.data.color_attributes["AdjustedVColors"].data

        for idx in range(len(allColors)):
            r = allColors[idx].paletteColor.val[0]
            g = allColors[idx].paletteColor.val[0]
            b = allColors[idx].paletteColor.val[0]
            a = 1
            allVerts[idx].color = [r,g,b,a]

        return

    def getColorPalette(self, threshold):
        allVerts = self.selectedObject.data.color_attributes.active.data
        allTColors = []
        for v in allVerts:
            r = math.floor(v.color[0] * 255) / 255
            g = math.floor(v.color[1] * 255) / 255
            b = math.floor(v.color[2] * 255) / 255
            allTColors.append(TColor(mathutils.Color([r,g,b]), threshold))

        sortedColors = sorted(allTColors)
        palette = []
        palette.append(sortedColors[0])
        for idx in range(len(sortedColors)):
            if sortedColors[idx] != palette[-1]:
                palette.append(sortedColors[idx])
            sortedColors[idx].paletteColor = palette[-1]

        return allTColors, palette


    def selectHairCardByFace(self, face:bpy.types.MeshPolygon):
        sv:bpy.types.MeshVertex
        for v in face.vertices:
            sv = self.selectedObject.data.vertices[v]
            
        return

    def getLinkedFaces(self, face, vertices, faces):

        for v in face.verts:
            lFaces = v.link_faces
            if len(lFaces) > 0 and v not in vertices:
                vertices.append(v)
                for f in lFaces:
                    if f.index not in faces:
                        faces.append(f.index)
                        self.getLinkedFaces(f, vertices, faces)

        return

    def getHairCards(self):
        cards = []
        cardIdx = 0
        hc:HairCard
        for face in self.bMesh.faces:
            #get linked faces
            existing = [hc for hc in cards if face.index in hc.faces]
            if len(existing) == 0:
                hc = HairCard(cardIdx)
                hc.faces.append(face.index)
                self.getLinkedFaces(face, hc.vertices, hc.faces)
                cards.append(hc)
                hc.calcFaceColors(self.bMesh, self.allTColors)
                cardIdx += 1

        return cards

    def groupHairCardsByColors(self, hairCards:array):

        upColorSorted = sorted(hairCards, key=lambda c:c.upColor)
        upColorGroups = []
        upColorGroups.append(CardsGroup())
        upColorGroups[0].cards.append(upColorSorted[0])

        for card in upColorSorted:
            if card.upColor != upColorGroups[-1].cards[0].upColor:
                upColorGroups.append(CardsGroup())
            if card not in upColorGroups[-1].cards:
                upColorGroups[-1].cards.append(card)

        totalGroups = []

        for upGroup in upColorGroups:
            upGroup.cards = sorted(upGroup.cards, key=lambda c: c.bottomColor)
            totalGroups.append(CardsGroup())
            totalGroups[-1].cards.append(upGroup.cards[0])
            for card in upGroup.cards:
                if card.bottomColor != totalGroups[-1].cards[0].bottomColor:
                    totalGroups.append(CardsGroup())
                if card not in totalGroups[-1].cards:
                    totalGroups[-1].cards.append(card)


        return totalGroups

    def makeAvgColorsByCardGroups(self, groups):

        allVerts = self.selectedObject.data.color_attributes["AdjustedVColors"].data
        for g in groups:
            for pNum in range(g.cards[0].pointsCount):
                color = mathutils.Color([0,0,0])
                for card in g.cards:
                    color += card.getPointByIndex(pNum).tColor.val
                color /= len(g.cards)
                for card in g.cards:
                    allVerts[card.getPointByIndex(pNum).vertIdx].color = [color.r, color.g, color.b, 1]


        return

    def selectWithSimilarColors(self):
        threshold = 20
        obj = bpy.context.object
        colors = obj.data.color_attributes.active.data
        selected_polygons = list(filter(lambda p: p.select, obj.data.polygons))
        if len(selected_polygons):
            p = selected_polygons[0]
            r = g = b = 0
            for i in p.vertices:
                c = colors[i].color
                r += c[0]
                g += c[1]
                b += c[2]
            r /= p.loop_total
            g /= p.loop_total
            b /= p.loop_total
            target = mathutils.Color((r, g, b))
            for p in obj.data.polygons:
                r = g = b = 0
                for i in p.vertices:
                    c = colors[i].color
                    r += c[0]
                    g += c[1]
                    b += c[2]
                r /= p.loop_total
                g /= p.loop_total
                b /= p.loop_total
                source = mathutils.Color((r, g, b))
                if (abs(source.r - target.r) * 100 / source.r < threshold and
                    abs(source.g - target.g) * 100 / source.g <  threshold and
                    abs(source.b - target.b) * 100 / source.b < threshold):
                    p.select = True
                    #print(target, source)
                else:   
                    p.select = False
        

    def execute(self, context):

        if len(bpy.context.selected_objects) > 0 :

            threshold = context.scene.fur_vert_color_threshold
            self.selectedObject = bpy.context.selected_objects[0]
            bpy.ops.object.mode_set(mode="OBJECT")
            #copy vert colors and calc palette
            self.allTColors, palette = self.getColorPalette(threshold)

            if "GradientsUV" in self.selectedObject.data.uv_layers:
                self.selectedObject.data.uv_layers.remove(self.selectedObject.data.uv_layers["GradientsUV"])
            self.selectedObject.data.uv_layers.new(name="GradientsUV", do_init=True)
            
            bpy.ops.object.mode_set(mode="EDIT")
            self.bMesh = bmesh.from_edit_mesh(self.selectedObject.data)
            self.bMesh.faces.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')

            cards = self.getHairCards()

            bpy.ops.object.mode_set(mode="OBJECT")

            #adjust vertex colors
            #to paletteColors of allColors
            self.createColorAttrsByPalette(self.allTColors)

            groups = self.groupHairCardsByColors(cards)

            #calc avg colors by cards
            self.makeAvgColorsByCardGroups(groups)

            #check
            testFaces = []
            for c in cards:
                for f in c.faces:
                    if f not in testFaces:
                        testFaces.append(f)
                    else:
                        print("Face twice in cards")

            testFaces = []
            for g in groups:
                for c in g.cards:
                    for f in c.faces:
                        if f not in testFaces:
                            testFaces.append(f)
                        else:
                            print("Face twice in groups")

            rows = math.floor(math.sqrt(len(groups)))
            cols = math.floor(len(groups) / rows)
            rest = len(groups) - rows * cols
            if rest > 0: cols += 1
            w = groups[0].cards[0].uvWidth
            h = groups[0].cards[0].uvHeight
            dist = max([w, h]) / 20

            scale = 1 / max([rows, cols])
            idx = 0
            for c in range(cols):
                for r in range(rows):
                    if idx < len(groups):
                        x = c * (w + dist)
                        y = r * (h + dist)
                        #print (x, y)
                        for card in groups[idx].cards:
                            #card.updateUVs(x,y)
                            card.updateUVs2(x ,y, scale , self.selectedObject)
                        idx +=1

            bpy.ops.object.mode_set(mode="EDIT")

            self.report({'INFO'}, "Groups " + str(len(groups)))

        else:
            self.report({'INFO'}, "Select object")

        return {'FINISHED'}