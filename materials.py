from json import load
from bricks import normalBrick, wallBrick
import numpy as np


def nameFromPath(path: str) -> str:
    name = path.split('.')[0].split('/')
    return name[len(name) - 1]


class material:
    def __init__(self, materialConfigFilePath):
        file = open(materialConfigFilePath)
        data = load(file)
        self.name = data.get("name", nameFromPath(materialConfigFilePath))
        self.color = np.array(data["color"], np.uint8).tobytes()
        if len(data["bricks"]) <= 0:
            raise Exception("no bricks in material, you need at least a 1x1 brick")
        self.bricks = [normalBrick(e) for e in data["bricks"]]
        if len(data.get("wallBricks", [])) <= 0:
            print(Warning("no wall bricks in material, holes may appear"))
        self.wallBricks = [wallBrick(e) for e in data.get("wallBricks", [])]
        self.maxSize = self.calcMaxSize()
        self.materialType = data.get("type", "flat")

    def calcMaxSize(self) -> (int, int):
        maxSize = [0, 0]
        for b in self.bricks:
            if b.size[0] > maxSize[0]:
                maxSize[0] = b.size[0]
            if b.size[1] > maxSize[1]:
                maxSize[1] = b.size[1]
            if b.rotatable:
                if b.size[1] > maxSize[0]:
                    maxSize[0] = b.size[1]
                if b.size[0] > maxSize[1]:
                    maxSize[1] = b.size[0]
        return maxSize

    def statistics(self) -> dict:
        stats = {brick.name: {"total": brick.placedBricks, "edgeBricks": brick.placedEdgeBricks,
                              "flatBricks": brick.placedFlatBricks} for brick in self.bricks}
        numBricks = [0,0,0]
        for mat in stats.values():
            values = list(mat.values())
            for i in range(3):
                numBricks[i] += values[i]
        finalStats = {self.name: {"total": numBricks[0], "edgeBricks": numBricks[1], "flatBricks": numBricks[2]}}
        finalStats.update(stats)
        return finalStats

    def testBricks(self, materialGrid, coordinates: (int, int), size: [int, int], displacementGrid: np.ndarray,
                   brickHeightGrid: np.ndarray, finishedGrid: [[bool]], zStepSize: int,
                   worldScale: (float, float, float) = (1, 1, 1), worldOffset: (float, float, float) = (0, 0, 0)) -> int:
        """
        Defines which of all Bricks in this Material should be placed.

        :param materialGrid:
        :param coordinates:
        :param size: size of global world -> shape of material and displacementGrid
        :param displacementGrid:
        :param finishedGrid: Grid of boolean that present on which coordinates a bricks has already been placed
        :param worldScale:
        :param worldOffset:
        :return: length of placed Brick in y direction
        """
        foundBrick = False
        testedGrid = np.array([[False] * materialGrid[coordinates[0]][coordinates[1]].maxSize[1]] * materialGrid[coordinates[0]][coordinates[1]].maxSize[0])
        for brick in self.bricks:
            if brick.brickTest(coordinates, size, displacementGrid[coordinates[0]][coordinates[1]],
                               materialGrid[coordinates[0]][coordinates[1]], displacementGrid, materialGrid,
                               finishedGrid, testedGrid):
                finalBrick = brick
                foundBrick = True

        if foundBrick:
            finalBrick.redefineBrick(displacementGrid, (coordinates[0], coordinates[1], displacementGrid[coordinates[0]][coordinates[1]]),
                                     worldScale, worldOffset, size)
            for X in range(coordinates[0], coordinates[0] + finalBrick.size[0]):
                for Y in range(coordinates[1], coordinates[1] + finalBrick.size[1]):
                    finishedGrid[X, Y] = True
                    brickHeightGrid[X, Y] = displacementGrid[X, Y] + finalBrick.size[2] * zStepSize
            return finalBrick.size[1]
        else:
            print(f"Could not find matching Brick at {coordinates} for {self.name}")
            return 1

    def testWallBricks(self, displacementUpperLimitRow, displacementBottomLimitRow, neighbourDispUpperLimitRow,
                       neighbourDispBottomLimitRow, materialRow, COORDINATE, coordinates: (int, int),
                       worldscale: (float, float, float), worldOffset, zStepSize, LOCALXAXIS):
        finalBrick = False
        while True:
            if displacementBottomLimitRow[COORDINATE] > neighbourDispUpperLimitRow[COORDINATE]:
                for brick in self.wallBricks:
                    if brick.downBrickTest(COORDINATE, self, displacementBottomLimitRow, materialRow):
                        finalBrick = brick
                if finalBrick:
                    finalBrick.redefineBrick(
                        (coordinates[0] + worldOffset[0], coordinates[1] + worldOffset[1],
                         displacementBottomLimitRow[COORDINATE]), worldscale, LOCALXAXIS)
                    for x in range(COORDINATE, COORDINATE + finalBrick.size[0]):
                        displacementBottomLimitRow[x] -= finalBrick.size[2] * zStepSize
                    #return finalBrick.size[0]
                else:
                    print(f"No matching Brick found for {coordinates} at height {displacementBottomLimitRow[COORDINATE]}")
                    break
            else:
                break
        while True:
            if displacementUpperLimitRow[COORDINATE] < neighbourDispBottomLimitRow[COORDINATE]:
                for brick in self.wallBricks:
                    if brick.upBrickTest(COORDINATE, self, neighbourDispBottomLimitRow, materialRow):
                        finalBrick = brick
                if finalBrick:
                    finalBrick.redefineBrick(
                        (coordinates[0] + worldOffset[0] + 1, coordinates[1] + worldOffset[1] + 1,
                         neighbourDispBottomLimitRow[COORDINATE] + worldOffset[2]), worldscale, LOCALXAXIS)
                    for x in range(COORDINATE, COORDINATE + finalBrick.size[0]):
                        neighbourDispBottomLimitRow[x] -= finalBrick.size[2] * zStepSize
                    #return finalBrick.size[0]
                else:
                    print(f"No matching Brick found for {coordinates} at height {displacementBottomLimitRow[COORDINATE]}")
                    break
            else:
                break
        return 1


if __name__ == "__main__":
    exampleMat = material("exampleMaterial.json")
    exampleMat.testBricks()
