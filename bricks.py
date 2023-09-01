import math
import numpy as np
import os
from random import randrange


class brick:
    def __init__(self, data: dict):
        """
        Init function on the parent brick class. This function initialize basic parameters that both subclasses
        normalBrick and wallBrick need

        :param data: Dictionary of the json file that gives all needed information. for more information about this
         dictionary look up the docs.
        """
        self.size = data["size"]
        # offset of object when placed
        self.offset = data.get("offset", (0, 0, 0))
        self.scale = data.get("scale", [1, 1, 1])
        # some stuff for BeamNG
        self.persistentID = data["persistentID"]
        # name of the object in BeamNG
        self.name = data["name"]
        # File to linked DAE-file containing the mesh of this brick
        # main mesh of object
        self.linkedObject = data["linkedObject"]
        if type(self.linkedObject) != list:
            raise ReferenceError(f'linkedObject of brick {self.name} is not a list but a'
                                 f' {type(self.linkedObject)}. \n Change the {type(self.linkedObject)} to a'
                                 f' list in the corresponding material.json.')
        # output json-file
        path = r'jsonsOutput/' + self.name
        if not os.path.exists(path):
            os.makedirs(path)
        self.outFile = open(("jsonsOutput/" + self.name + "/items.level.json"), "w")
        self.rotation = 0
        self.placedBricks = 0

    def placeInstance(self, coordinates: [int, int, int], worldscale: [float, float, float],
                      rotation: [float, float, float],
                      linkedFile: str, scale: [float, float, float] = [1, 1, 1]):
        """
        Functions places an instance of the linked mesh in the Json-File for BeamNG.

        :param coordinates: coordinates at which the brick instance should be placed
        :param worldscale: scale of the world: one brick unit equals world scale in meters
        :param rotation: rotation in around all axis (x,y,z) in radians
        :param linkedFile: string of the filepath to the DAE-File
        :param scale: scale of the object
        :return: none
        """

        def rotationMatrix() -> np.matrix:
            # X-rotation
            matrix = np.matrix([[1, 0, 0],
                                [0, math.cos(rotation[0]), -math.sin(rotation[0])],
                                [0, math.sin(rotation[0]), math.cos(rotation[0])]])
            # Y-rotation
            matrix *= np.matrix([[math.cos(rotation[1]), 0, math.sin(rotation[1])],
                                 [0, 1, 0],
                                 [-math.sin(rotation[1]), 0, math.cos(rotation[1])]])
            # Z-rotation
            matrix *= np.matrix([[math.cos(rotation[2]), -math.sin(rotation[2]), 0],
                                 [math.sin(rotation[2]), math.cos(rotation[2]), 0],
                                 [0, 0, 1]])
            matrix[abs(matrix) < 1e-8] = 0
            matrix[matrix > 1 - 1e-8] = 1
            matrix[matrix < -1 + 1e-8] = -1
            return matrix

        position = [round((coordinates[0] + self.offset[0]) * worldscale[0], 3),
                    round((coordinates[1] + self.offset[1]) * worldscale[1], 3),
                    round((coordinates[2] + self.offset[2]) * worldscale[2], 4)]
        text = '{' + f'"class":"TSStatic","__parent":"{self.name}",' \
                     f'"position":{position},"isRenderEnabled":false,'
        # deleted: "persistentId":"{self.persistentID}",
        if any(i != 1 for i in scale) or any(i != 1 for i in self.scale):
            text += f'"scale":[{self.scale[0] * scale[0]},' \
                    f'{self.scale[1] * scale[1]},' \
                    f'{self.scale[2] * scale[2]}],'
        if any(i != 0 for i in rotation):
            matrix = rotationMatrix()
            text += f'"rotationMatrix":[{matrix[0, 0]},{matrix[0, 1]},{matrix[0, 2]},' \
                    f'{matrix[1, 0]},{matrix[1, 1]},{matrix[1, 2]},' \
                    f'{matrix[2, 0]},{matrix[2, 1]},{matrix[2, 2]}],'
        text += f'"shapeName":"{linkedFile}","useInstanceRenderData":true' + '}\n'
        self.outFile.write(text)
        self.placedBricks += 1

    def closeJson(self):
        self.outFile.close()


class normalBrick(brick):
    def __init__(self, data: dict):
        # call to init fucntion of parent class
        brick.__init__(self, data)
        self.rotatable = data.get("rotatable", False)
        # File to linked DAE-file containing the mesh of this brick
        self.linkedFlatObject = data.get("linkedFlatObject", [False])
        if type(self.linkedFlatObject) != list:
            raise ReferenceError(f'linkedFlatObject of brick {self.name} is not a list but a'
                                 f' {type(self.linkedFlatObject)}. \n Change the {type(self.linkedFlatObject)} to a'
                                 f' list in the corresponding material.json.')
        brickType = data.get("type", "flat")
        types = {"flat": self.brickFlatTest, "road": self.brickRoadTest, "slope": self.brickSlopeTest, "tree": self.treeTest}
        self.objectType = types[brickType]
        self.minSlope = data.get("minSlope", 0)
        self.slopeX, self.slopeY = 0, 0
        self.placedFlatBricks = 0
        self.placedEdgeBricks = 0

    def brickTest(self, coordinates: (int, int), worldSize: (int, int), height: int, materialIndex: int,
                  displacementGrid: [[int]], materialGrid: [[int]], finishedGrid: [[bool]], testedGrid: [[bool]]) \
            -> bool:
        """
            This Functions tests if the brick can be placed on the given Coordinates.

            :param coordinates: Coordinates at which the brick should be placed and tested
            :param worldSize: size of the World(length of displacementGrid, materialGrid...)
            :param height: z-level of the first Coordinates
            :param materialIndex: index of the material in the materialList of the first Coordinates
            :param displacementGrid: Grid that stores the height of the terrain
            :param materialGrid: Grid that stores the material indexes of the terrain
            :param finishedGrid: Grid that stores if a brick is already placed on these Coordinates
            :param testedGrid: Grid that stores if the position is already tested
            :return: True if brick can be placed, False if not
            """
        return self.objectType(coordinates, worldSize, height, materialIndex, displacementGrid, materialGrid,
                               finishedGrid, testedGrid)

    def brickSlopeTest(self, coordinates: (int, int), worldSize: (int, int), height: int, materialIndex: int,
                      displacementGrid: [[int]], materialGrid: [[int]], finishedGrid: [[bool]], testedGrid: [[bool]])\
            -> bool:
        # todo

        self.slope(height, coordinates, worldSize, displacementGrid, materialGrid, "slope")

        if abs(self.slopeX) > abs(self.slopeY):
            if self.minSlope <= self.slopeX:
                self.rotation = 0
                return True
            elif self.minSlope <= -self.slopeX:
                self.rotation = 180
                return True
        else:
            if self.minSlope <= self.slopeY:
                self.rotation = 90
                return True
            elif self.minSlope <= -self.slopeY:
                self.rotation = 270
                return True
        return False

    def brickRoadTest(self, coordinates: (int, int), worldSize: (int, int), height: int, materialIndex: int,
                      displacementGrid: [[int]], materialGrid: [[int]], finishedGrid: [[bool]], testedGrid: [[bool]])\
            -> bool:
        def test(first: int, second: int):
            for deltaX in range(self.size[first]):
                for deltaY in range(self.size[second]):
                    if not testedGrid[deltaX, deltaY]:
                        X = coordinates[0] + deltaX
                        if X >= worldSize[0]:
                            return False
                        Y = coordinates[1] + deltaY
                        if Y >= worldSize[1]:
                            return False
                        if height + self.slopeX * deltaX + self.slopeY * deltaY != displacementGrid[X][Y] or finishedGrid[X,Y] or materialIndex != materialGrid[X][Y]:
                            return False
                        else:
                            testedGrid[deltaX,deltaY] = True
            return True
        
        self.slope(height, coordinates, worldSize, displacementGrid, materialGrid)
        
        if test(0, 1):
            return True
        return False

    def slope(self, height: int, coordinates: [int, int], worldSize: [int, int], displacementGrid: [[int]],
              materialGrid, materialType="road"):

        self.slopeX, self.slopeY = 0, 0

        # Checking X-Slope
        def secondX():
            # If not, is new X in world bounds?
            X = coordinates[0] - 1
            if X >= 0:
                # Is new positions same material?
                if materialGrid[X][coordinates[1]].materialType == materialType:
                    self.slopeX = displacementGrid[X][coordinates[1]] - height

        X = coordinates[0] + 1
        # is X in world bounds?
        if X < worldSize[0]:
            # If not, is new positions the same material?
            if materialGrid[X][coordinates[1]].materialType == materialType:
                self.slopeX = displacementGrid[X][coordinates[1]] - height
            else:
                secondX()
        else:
            secondX()

        # Checking Y-Slope
        Y = coordinates[1] + 1
        # is X in world bounds?
        if Y >= worldSize[0]:
            self.slopeY = 0
        else:
            # If not, is new positions a road block as well?
            if materialGrid[coordinates[0]][Y].materialType == materialType:
                self.slopeY = displacementGrid[coordinates[0]][Y] - height
            else:
                # If not, is new Y in world bounds?
                Y = coordinates[0] - 1
                if Y < 0:
                    self.slopeY = 0
                elif materialGrid[coordinates[0]][Y].materialType == materialType:
                    # If not, is new positions a road block as well?
                    self.slopeY = -(displacementGrid[coordinates[0]][Y] - height)
                else:
                    self.slopeY = 0

    def brickFlatTest(self, coordinates: (int, int), worldSize: (int, int), height: int, materialIndex: int,
                      displacementGrid: np.ndarray, materialGrid: [[int]], finishedGrid: [[bool]], testedGrid: [[bool]])\
            -> bool:
        def test(first: int, second: int):
            for deltaX in range(self.size[first]):
                for deltaY in range(self.size[second]):
                    if not testedGrid[deltaX,deltaY]:
                        X = coordinates[0] + deltaX
                        if X >= worldSize[0]:
                            return False
                        Y = coordinates[1] + deltaY
                        if Y >= worldSize[1]:
                            return False
                        if height != displacementGrid[X, Y] or finishedGrid[X, Y] or materialIndex != materialGrid[X][Y]:
                            return False
                        else:
                            testedGrid[deltaX, deltaY] = True
            return True
        if test(0,1):
            return True
        return False

    def treeTest(self, coordinates: (int, int), worldSize: (int, int), displacementGrid: [[int]]) -> bool:
        for deltaX in range(self.size[0]):
            for deltaY in range(self.size[1]):
                X = coordinates[0] + deltaX
                if X >= worldSize[0]:
                    return False
                Y = coordinates[1] + deltaY
                if Y >= worldSize[1]:
                    return False
                if displacementGrid[coordinates[0]][coordinates[1]] != displacementGrid[X][Y]:
                    return False
        return True

    def redefineBrick(self, displacementGrid: np.array, coordinates: [int, int, int], worldscale: [float, float, float],
                      worldOffset: [float, float, float], worldSize: [int, int]):

        def testHeight(local: [int, int], axis: int):
            if 0 <= local[not axis] < worldSize[not axis]:
                for local[axis] in range(coordinates[axis], coordinates[axis] + self.size[axis]):
                    if 0 <= local[axis] < worldSize[axis]:
                        if displacementGrid[local[0], local[1]] < coordinates[2]:
                            return True
            return False

        def defineModel():
            if self.linkedFlatObject[0]:
                if testHeight([coordinates[0], coordinates[1] - 1], 0):
                    self.placedEdgeBricks += 1
                    return self.linkedObject
                if testHeight([coordinates[0], coordinates[1] + self.size[1]], 0):
                    self.placedEdgeBricks += 1
                    return self.linkedObject
                if testHeight([coordinates[0] - 1, coordinates[1]], 1):
                    self.placedEdgeBricks += 1
                    return self.linkedObject
                if testHeight([coordinates[0] + self.size[0], coordinates[1]], 1):
                    self.placedEdgeBricks += 1
                    return self.linkedObject
                self.placedFlatBricks += 1
                return self.linkedFlatObject
            self.placedEdgeBricks += 1
            return self.linkedObject

        linkedModels = defineModel()
        linkedModel = linkedModels[randrange(len(linkedModels))]

        rotation = [0, 0, math.radians(self.rotation)]
        scale = [1,1,1]

        # "apply" Rotation and Scaling for road bricks
        if self.objectType == self.brickRoadTest:
            if self.slopeX:
                scale[0] = math.sqrt((self.size[0] * worldscale[0]) ** 2 + (self.slopeX * worldscale[2] * self.size[0]) ** 2) / (self.size[0] * worldscale[0])
                rotation[1] = math.atan(self.slopeX * worldscale[2] / worldscale[0])
            if self.slopeY:
                scale[1] = math.sqrt((self.size[1] * worldscale[1]) ** 2 + (self.slopeY * worldscale[2] * self.size[1]) ** 2) / (self.size[1] * worldscale[1])
                rotation[0] = -math.atan(self.slopeY * worldscale[2] / worldscale[1])

        # add WorldOffset
        coordinates = [coordinates[0]+worldOffset[0], coordinates[1]+worldOffset[1], coordinates[2]+worldOffset[2]]

        self.placeInstance(coordinates, worldscale, rotation, linkedModel, scale)


class wallBrick(brick):
    def __init__(self, data: dict):
        brick.__init__(self, data)

    def upBrickTest(self, coordinate: int, material, neighbourDispRow, materialRow: [[]]) -> bool:
        # 0 32
        MAX_SIZE: int = len(neighbourDispRow)
        HEIGHT: int = neighbourDispRow[coordinate]  # + (32 * self.size[2])
        for localX in range(coordinate, coordinate + self.size[0]):
            if localX >= MAX_SIZE:
                return False
            if neighbourDispRow[localX] != HEIGHT or materialRow[localX] != material:
                return False
        self.rotation = 0
        return True

    def downBrickTest(self, coordinate: int, material, displacementRow: np.ndarray, materialRow: [[]]) -> bool:
        MAX_SIZE: int = len(displacementRow)
        HEIGHT: int = displacementRow[coordinate]  # + (32 * self.size[2])
        for localX in range(coordinate, coordinate + self.size[0]):
            if localX >= MAX_SIZE:
                return False
            if displacementRow[localX] != HEIGHT or materialRow[localX] != material:
                return False
        self.rotation = 180
        return True

    def redefineBrick(self, coordinates, worldscale, LOCALXAXIS):
        rotation = [0, 0, math.radians(self.rotation if LOCALXAXIS else self.rotation + 90)]
        self.placeInstance(coordinates, worldscale, rotation, self.linkedObject[randrange(len(self.linkedObject))])
