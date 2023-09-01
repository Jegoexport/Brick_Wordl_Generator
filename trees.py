from bricks import normalBrick
import numpy as np

class treeType:
    def __init__(self, data):
        self.name = data["name"]
        self.numTrees = len(data["objects"])
        self.trees = [normalBrick(e) for e in data["objects"]]
        self.density = data["density"]
        self.color = np.array(data["color"], np.uint8).tobytes()
        #self.maxRandom = data.get("maxRandom", (int(self.density[0]/2), int(self.density[1]/2)))
