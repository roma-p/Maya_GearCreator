from itertools import cycle
import pymel.core as pm
import logging

log = logging.getLogger("color auto shader")
log.setLevel(logging.DEBUG)

class ColorAutoShader():

    COLOR_SET = {
        "dark_red": (139, 0, 0),
        "orange_red": (255, 69, 0),
        "orange": (255, 165, 0),
        "lime_green": (50, 205, 50),
        "light_sea_green": (32, 178, 170),
        "dark_slate_blue": (72, 61, 139),
        "dark_orchid": (153, 50, 204)
    }

    SHADER_PREFIX = "GearCreator"

    def __init__(self):
        self._shaderDict = {}
        for colorName, colorRGB in self.COLOR_SET.items():
            self._shaderDict[colorName] = self._createShader(colorName,
                                                             colorRGB)
        self.cycleIterator = cycle(self.COLOR_SET.keys())

    def __iter__(self): return self

    def __next__(self):
        colorName = next(self.cycleIterator)
        colorRGB = self.COLOR_SET[colorName]
        sg = self._shaderDict[colorName]
        return colorName, colorRGB, sg

    def _createShader(self, name, color):

        materialName = "{}_{}".format(self.SHADER_PREFIX, name)
        sgName = "{}_SG_{}".format(self.SHADER_PREFIX, name)

        sg = ColorAutoShader._getShader(sgName)
        if sg: return sg

        material = pm.shadingNode("lambert",
            name=materialName,
            asShader=True)
        material.color.set(ColorAutoShader._convRGB(*color))
        sg = pm.sets(name=sgName,
                     empty=True,
                     renderable=True,
                     noSurfaceShader=True)
        pm.connectAttr("%s.outColor" % material, "%s.surfaceShader" % sg,
                       force=True)
        return sg

    def _getShader(name):
        for node in pm.ls(type=pm.nt.ShadingEngine):  # filter by name.
            if node.name() == name:
                return node

    def _convRGB(*rgb):
        return [value / 255 for value in rgb]
