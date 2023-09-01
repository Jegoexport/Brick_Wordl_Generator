## config.json

The config.json file holds standard application data and needs to be configures to match your requirements.

#### Properties:

* ``materialPaths``: In this array are all Paths to the [config.json of your Materials](### Define a Material)
* ``stepSize``: If you want your normal bricks laced in a higher vertical interval than your Road Bricks you use this
  parameter to define how height one brick is in your heightMap Depth. 
> **Example**
> I used a stepSize of 32 to smooth my roads out. That means if your normal bricks in your texture Map were placed 
> between 0-31 now their height level is 0.
* ``worldscale``: This is scale of your global world and defines how wide, long and high your one brick dimension is and
  how it should be scaled in your global world.
> **Example**
> I use a World-scale of ``[0.25, 0.25, 0.1]`` because one 1x1 brick in my world is 0.25m by 0.25m and one plate is 0.1m
> high.
* ``worldOffset``: Offset in x, y and z that will be added to every coordinate in the end. By default, it will be set to
  half the worldsize in x and y direction and 0 for z.
* ``heightMapPath``: Path to your HeightMap.
> **Warning**
> Your Height should be and **black and white** only png and have the **same size** as your texturePathMap. I recommend
> a color depth of 16 bits.
* ``texturePathMap``: Path to your TextureMap. I recommend and png with an 8-bit color depth.

### Define a Material

#### Basic Properties:

* `` color ``: RGB Color Code that refers to this Material on the texture map.
* ``type``: Brick Type of the Material. Available options are ``flat`` (default), ``slope`` or ``road``. If a material 
  has different kinds of bricks eg: ``flat`` and ``slope`` you should use the least, so ``slope`` for this.
* `` bricks ``: This is an array of all Bricks in this Material:
> **Note**
> The Order of the brick in the array matters

#### Brick Properties:

  * ``name``: Name of the Brick. A Folder is created with this name in jsonsOutput to write all data for this brick in a
    specific items.level.json.
  * ``size``: Array with X-,Y- and Z-Dimensions of this Brick in brickscale.
  * ``minSlope``: minium slope. Optional. Default Value is 0.
  * ``rotatatable``: Boolean. If the rotation with 90° make a difference that set it to ``true``. If not to ``False``.
  * ``persistendID``: ID that the items.level.json (BeamNG) needs. Not important. Can be the same for now for all object"
  * ``linkedObject``: Filepath to DAE-file for the 3d-Object of this brick. 
  > **Note** 
  > Use a short Path to reduce the Size of items.level.json file.

#### Example Material

```json
{
  "color": [0, 146, 71],
  "bricks": [{"name": "b11g", "size":  [1,1], "rotatable":  false,
    "persistentID": "01a330ee-2bba-4cba-ab17-9eec6398f3df",
    "linkedObject": ["/levels/brickWorld/art/shapes/b11g.dae"]
  },
  {"name": "b44g", "size":  [4,4], "rotatable":  false,
    "persistentID": "01a330ee-2bba-4cba-ab17-9eec6398f3df",
    "linkedObject": ["/levels/brickWorld/art/shapes/b44g.dae"]
  }]
}
```