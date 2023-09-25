from materials import material
from trees import treeType
import numpy as np
from PIL import Image
from random import randrange, seed
from json import load
from time import time_ns, time


def place(displacementGrid, materialGrid: [[material]], materials: [material], worldScale: [float, float, float],
          worldOffset: [float, float, float], zStepSize: int):
    size = (len(displacementGrid), len(displacementGrid[0]))
    finishedGrid = np.array([[False] * size[1]] * size[0])
    brickHeightGrid = np.copy(displacementGrid) #np.empty([size[0], size[1]], dtype=int)
    for x in range(size[0]):
        startTimer = time()
        y = 0
        while y < size[1]:
            if not finishedGrid[x,y]:
                y += materialGrid[x][y].testBricks(materialGrid, (x, y), size, displacementGrid, brickHeightGrid,
                                                   finishedGrid, zStepSize, worldScale, worldOffset)
            else:
                y += 1
        print(f'for Row {x}: {round(time()-startTimer, 4)} sec.')
    placeWallBricks(displacementGrid, brickHeightGrid, size, worldScale, worldOffset, zStepSize, materialGrid)
    placeWallBricks(displacementGrid, brickHeightGrid, size, worldScale, worldOffset, zStepSize, materialGrid, True)

def placeWallBricks(displacementGrid, brickHeightGrid, size, worldScale, worldOffset, zStepSize,
                    materialGrid: [[material]], LOCALXAXIS: bool = False):
    for x in range(size[LOCALXAXIS]-1):
        startTimer = time()
        displacementUpperLimitRow = np.array([row[x] for row in brickHeightGrid]) if LOCALXAXIS else brickHeightGrid[x]
        displacementBottomLimitRow = np.array([row[x] for row in displacementGrid]) if LOCALXAXIS \
            else np.copy(displacementGrid[x])
        neighbourDispUpperLimitRow = np.array([row[x + 1] for row in brickHeightGrid]) if LOCALXAXIS \
            else brickHeightGrid[x + 1]
        neighbourDispBottomLimitRow = np.array([row[x + 1] for row in displacementGrid]) if LOCALXAXIS \
            else np.copy(displacementGrid[x + 1])
        materialRow = np.array([row[x] for row in materialGrid]) if LOCALXAXIS else materialGrid[x]
        y = 0
        while y < (size[not LOCALXAXIS]):
            materialGrid[x][y].testWallBricks(displacementUpperLimitRow, displacementBottomLimitRow,
                                              neighbourDispUpperLimitRow, neighbourDispBottomLimitRow,
                                              materialRow, y, (y if LOCALXAXIS else x, x if LOCALXAXIS else y), worldScale, worldOffset, zStepSize, LOCALXAXIS)
            y += 1
        print(f'for Row {x}: {round(time() - startTimer, 4)} sec.')
        
def saveJsons(materials:[material], treeList:[treeType]):
    for mat in materials:
        for br in mat.bricks:
            br.closeJson()
    for trees in treeList:
        for tree in trees.trees:
            tree.closeJson()

def convertToMaterial(imagePath: str, materials: [], default: int = -1) -> list:
    image = np.asarray(Image.open(imagePath))
    # image = np.array([[[0, 146, 71]]*16]*16, np.uint8)
    # print(image)
    dict = {}
    for i in range(len(materials)):
        dict.update({materials[i].color: i})
    print(dict)
    print("0,0:", image[0,0].tobytes())
    materialGrid = [[materials[dict.get(image[x][y].tobytes(), default)] for y in range(len(image[0]))] for x in range(len(image))]
    return materialGrid

def placeTrees(displacementGrid, treeTypeGrid, trees: [treeType], worldScale: [float, float, float]):
    seed(0)
    worldSize = (len(displacementGrid), len(displacementGrid[0]))
    numTrees = 0
    #mainloop
    i = 0
    for tree in trees:
        for x in range(0, worldSize[0], tree.density[0]):
            for y in range(0, worldSize[1], tree.density[1]):
                localX = x + randrange(0, tree.density[0])
                localY = y + randrange(0, tree.density[1])
                if localX >= worldSize[0] or localY >= worldSize[1]:
                    break
                checkedTrees = [False]*tree.numTrees
                checkedTreesNum = 0
                if treeTypeGrid[localX][localY] == i:
                    while checkedTreesNum < tree.numTrees:
                        r = randrange(0, tree.numTrees)
                        rotation = randrange(0, 360, 90)
                        if not checkedTrees[r]:
                            checkedTrees[r] = True
                            checkedTreesNum += 1
                            result = tree.trees[r].treeTest((localX, localY), worldSize, displacementGrid)
                            if result:
                                tree.trees[r].redefineBrick((localX, localY, displacementGrid[localX][localY]), worldScale,
                                                     rotation)
                                numTrees += 1
                                break
        i += 1
    print(numTrees)


if __name__ == '__main__':

    config = load(open("config.json"))

    # load materials
    print("loading materials...", end=' ')
    start = time_ns()
    tex = [material((f'materials/' + path)) for path in config["materialPaths"]]
    #tex = [material(("materials/exampleMaterial.json"))]
    print(time_ns()-start, "nanosec for", len(tex), "materials")

    # define Worldscale
    stepSize = int(config["stepSize"])
    scale = config["worldscale"]
    scale[2] = scale[2]/stepSize
    print(stepSize)

    # load heightMap
    print("loading displacement map")
    displacementGrid = np.asarray(Image.open(config["heightMapPath"]))
    #displacementGrid = np.array([[32 * y for y in range(4)] for x in range(4)])
    #displacementGrid = np.array([[0, 0, 0],
    #                             [0, 128, 0],
    #                             [0, 0, 0]])
    #                             [0, 128, 0, 0, 128, 0],
    #                             [0, 128, 128, 128, 128, 0],
    #                             [0, 0, 0, 0, 0, 0]])
    #print(displacementGrid)

    # load textureMap
    print("loading material map")
    #grid = [[tex[0]]*3]*3
    grid = convertToMaterial(config["textureMapPath"], tex)

    # redefine displacement map
    print("redefining displacement map")
    for x in range(len(displacementGrid)):
        for y in range(len(displacementGrid[0])):
            if not grid[x][y].materialType == "road":
                displacementGrid[x][y] = int(displacementGrid[x][y] / stepSize) * stepSize

    # define global offset
    worldOffset = config.get("worldOffset", [-len(displacementGrid)/2, -len(displacementGrid[0])/2, 0])

    # place Bricks
    print("placing bricks")
    startTimePlacing = time()
    place(displacementGrid, grid, tex, scale, worldOffset, stepSize)

    totalNumBricks = 0
    for material in tex:
        stats = material.statistics()
        print(stats)
        totalNumBricks += list(stats.values())[0]["total"]
    print(f"in total {totalNumBricks} bricks placed in {time()-startTimePlacing} sec.")
    exit()

    # load trees
    print("loading trees")
    file = open('treesConfig.json')
    data = load(file)
    trees = [treeType(e) for e in data]
    print("loading tree map")
    treeGrid = convertToMaterial("exampleTextureMap_2.png", trees)

    #place Trees
    print("placing trees")
    placeTrees(displacementGrid, treeGrid, trees, scale)

    print("writing to disc")
    saveJsons([], trees)

