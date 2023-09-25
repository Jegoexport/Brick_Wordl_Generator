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

        self.noWallBrick = False
        if len(data.get("wallBricks", [])) <= 0:
            self.noWallBrick = True
            print(Warning(f"no wall bricks in material: {self.name}, holes may appear"))
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
        stats.update({brick.name: {"total": brick.placedBricks, "wallBricks": brick.placedBricks} for brick in self.wallBricks})

        numBricks = {"total": 0, "edgeBricks": 0, "flatBricks": 0, "wallBricks": 0}
        for brick in stats.values():
            values = list(brick.values())
            keys = list(brick.keys())
            for i in range(len(values)):
                numBricks[keys[i]] += values[i]

        finalStats = {self.name: numBricks}
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
                    brickHeightGrid[X, Y] += finalBrick.size[2] * zStepSize
            return finalBrick.size[1]
        else:
            print(f"Could not find matching Brick at {coordinates} for {self.name}")
            return 1

    def testWallBricks(self, displacementUpperLimitRow, displacementBottomLimitRow, neighbourDispUpperLimitRow,
                       neighbourDispBottomLimitRow, materialRow, COORDINATE, coordinates: (int, int),
                       worldscale: (float, float, float), worldOffset, zStepSize, LOCALXAXIS):

        """

        :param displacementUpperLimitRow: height of row with bricks placed
        :param displacementBottomLimitRow: height of row with no bricks placed
        :param neighbourDispUpperLimitRow: height of next row with bricks placed
        :param neighbourDispBottomLimitRow: height of next row with no bricks placed
        :param materialRow:
        :param COORDINATE:
        :param coordinates:
        :param worldscale:
        :param worldOffset:
        :param zStepSize:
        :param LOCALXAXIS:
        :return:
        """

        def generateCoordiantes(height: np.ndarray, BACKFACING: bool):
            # localaxis is changed
            return (coordinates[0] + worldOffset[0] + (1 if (not LOCALXAXIS) and BACKFACING else 0),
                    coordinates[1] + worldOffset[1] + (1 if LOCALXAXIS and BACKFACING else 0),
                    height[COORDINATE] + worldOffset[2])

        def test(bottomLimit: np.ndarray, upperLimit: np.ndarray, BACKFACING: bool):
            while True:
                finalBrick = False
                if bottomLimit[COORDINATE] > upperLimit[COORDINATE]:
                    for brick in self.wallBricks:
                        if brick.brickTest(COORDINATE, self, bottomLimit, materialRow):
                            finalBrick = brick
                    if finalBrick:
                        finalBrick.redefineBrick(generateCoordiantes(bottomLimit, BACKFACING), worldscale, LOCALXAXIS, BACKFACING)
                        for x in range(COORDINATE, COORDINATE + finalBrick.size[0]):
                            bottomLimit[x] -= finalBrick.size[2] * zStepSize
                    else:
                        print(f"NO MATCHING BRICK: \n"
                              f"    Material: {self.name} \n"
                              f"    Coordinates: {coordinates}, Height: {displacementBottomLimitRow[COORDINATE]} \n"
                              f"    World Coordinates: {bottomLimit, generateCoordiantes(BACKFACING)}")
                        break
                else:
                    break

        if self.noWallBrick:
            return 1

        test(displacementBottomLimitRow, neighbourDispUpperLimitRow, False)
        test(neighbourDispBottomLimitRow, displacementUpperLimitRow, True)

        return 1


if __name__ == "__main__":
    exampleMat = material("exampleMaterial.json")
    exampleMat.testBricks()
