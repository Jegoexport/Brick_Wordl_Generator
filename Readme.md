# Brick World Generator

![TestWorld, Screenshot from BeamNG](https://github.com/Jegoexport/Brick_Wordl_Generator/blob/master/assets/images/ExampleRenderBeamNG.jpg)

This program places bricks based on height and texture maps for [BeamND.drive](https://www.beamng.com)

## Content

### Finished:

* place basic quadratic bricks like 1x1, 2x2, 4x4 according to height map
* build streets with flat bricks angled in direction ot the street
* main Config-File
* placement of vertical 'wall' Bricks

### Work in Progress:

* procedural placement on nature elements like trees, bushes and plants based on texture map
* placement of non-flat rock bricks, like 2x1x6 bricks where on side is angled (working a bit)
* placement of non square bricks

-------------

## Setting up

### Output & integration into BeamNG

The Output will be saved in the jsonsOutput Folder. This Folder can simply be copied to the SceneObject folder in BeamNG.
Before this you should already have imported all DAE-Files into to your Map in BeamNG to define Materials, etc.

### config.json

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
> Your Height should be and **black and white** only png and have the **same size** as your ``texturePathMap``. I recommend
> a color depth of 16 bits for larger worlds.
* ``texturePathMap``: Path to your TextureMap. I recommend and png with an 8-bit color depth.

### Define a Material

#### Basic Properties:

##### Required:

* `` color ``: RGB Color Code that refers to this Material on the texture map.
* ``type``: Brick Type of the Material. Available options are ``flat`` (default), ``slope`` or ``road``. If a material 
  has different kinds of bricks eg: ``flat`` and ``slope`` you should use the least, so ``slope`` for this.
* `` bricks ``: This is an array of all Bricks in this Material. For more information see [Brick Properties](#brick-properties).
> **Note**
> The Order of the brick in the array matters

##### Optional:
* ``name``: Name of the material. If not given it is the json-file name. (Debug purpose only)
* ``type``: Brick Type of the Material. Available options are ``flat`` (default), ``slope`` or ``road``. If a material 
  has different kinds of bricks eg: ``flat`` and ``slope`` you should use the least, so ``slope`` for this.
* ``wallBricks``: List of Bricks placed under other Bricks if a hole occurs. For more information see [wallBricks Properties](#WallBrick-Properties).
> **Warning**
> If you don't specify any wallBricks only may appear. 


#### Brick Properties

##### Required:

  * ``name``: Name of the Brick. A Folder is created with this name in jsonsOutput to write all data for this brick in a
    specific items.level.json.
  * ``size``: Size in bricks for x, y and z.

  * ``rotatatable``: Boolean. If the rotation with 90° make a difference that set it to ``true``. If not to ``False``.
  * ``persistendID``: ID that the items.level.json (BeamNG) needs. Not important. Can be the same for now for all object
  * ``linkedObject``: Filepath to DAE-file for the 3d-Object of this brick. 
  > **Note** 
  > Use a short Path to reduce the Size of items.level.json file.

##### Optional:

* ``offset``: Offset in x, y and z Direction of the Brick. Rotation will be applied to it. *Default* ``(0, 0, 0)``
* ``scale``: Scale if the items.level.json file for BeamNG. *Default* ``(1, 1, 1)``
* ``randomZRotation``: If ``true`` random rotation will be applied around the Z-axis. *Default* ``false``
* ``rotatatable``: Boolean. If the rotation with 90° make a difference that set it to ``true``. *Default* ``False``. *Work in progress* 
* ``linkedFlatObject``: Filepath to DAE-file with only the top faces. It will only be placed if all surrounding bricks
are as high or higher
* ``minSlope``: Minium slope at which the brick can be placed *Default* ``0``.
* ``type``: Brick Type of the Brick. Available options are ``flat`` (default), ``slope`` or ``road``.
* 

#### WallBrick Properties

##### Required:

* ``name``: Name of the Brick. A Folder is created with this name in jsonsOutput to write all data for this brick in a
    specific items.level.json.
* ``size``: Size in bricks for x, y and z. Only x and z direction are used.
* ``linkedObject``: Array of filepath(s) to DAE-file(s) for the 3d-Object of this brick. If given more than one 
filepath will be randomly chosen. 
  > **Note** 
  > Use a short Path to reduce the Size of items.level.json file.

##### Optional:

* ``offset``: Offset in x, y and z Direction of the Brick. Rotation will be applied to it. *Default* ``(0, 0, 0)``
* ``scale``: Scale if the items.level.json file for BeamNG. *Default* ``(1, 1, 1)``
* ``randomZRotation``: If ``true`` random rotation will be applied around the Z-axis. *Default* ``false``


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

