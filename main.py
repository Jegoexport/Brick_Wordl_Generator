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
    brickHeightGrid = np.empty([size[0], size[1]], dtype=int)
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
    placeWallBricks(displacementGrid, brickHeightGrid, size, worldScale, worldOffset, zStepSize, materialGrid, 1)

def placeWallBricks(displacementGrid, brickHeightGrid, size, worldScale, worldOffset, zStepSize, materialGrid: [[material]], LOCALXAXIS: bool = 0):
    for x in range(size[LOCALXAXIS]-1):
        startTimer = time()
        displacementUpperLimitRow = brickHeightGrid[x] if LOCALXAXIS else np.array(
            [row[x] for row in brickHeightGrid])
        displacementBottomLimitRow = displacementGrid[x] if LOCALXAXIS else np.array(
            [row[x] for row in displacementGrid])
        neighbourDispUpperLimitRow = brickHeightGrid[x + 1] if LOCALXAXIS else np.array(
            [row[x + 1] for row in brickHeightGrid])
        neighbourDispBottomLimitRow = displacementGrid[x + 1] if LOCALXAXIS else np.array(
            [row[x + 1] for row in displacementGrid])
        materialRow = materialGrid[x] if LOCALXAXIS else np.array(
            [row[x] for row in materialGrid])
        y = 0
        while y < (size[not LOCALXAXIS]):
            materialGrid[x][y].testWallBricks(displacementUpperLimitRow, displacementBottomLimitRow,
                                              neighbourDispUpperLimitRow, neighbourDispBottomLimitRow,
                                              materialRow, y, (x if LOCALXAXIS else y, y if LOCALXAXIS else x), worldScale, worldOffset, zStepSize, LOCALXAXIS)
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
    #tex = [material(("materials/grassMaterial.json"))]
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
    #displacementGrid = np.array([[0, 1024],
    #                             [0, 1024]])
    #print(displacementGrid)

    # load textureMap
    print("loading material map")
    #grid = [[tex[0]]*4]*4
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
    place(displacementGrid, grid, tex, scale, worldOffset, stepSize), #[grass, road, lines]'''

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

