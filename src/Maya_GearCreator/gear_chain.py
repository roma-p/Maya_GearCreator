import importlib
import logging

from Maya_GearCreator.gears import gear
importlib.reload(gear)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class GearChain():

    DEFAULT_PREFIX = "gearChain"
    DEFAULT_TWIDTH = 0.3
    gearChainIdx = 0

    def __init__(self, gearNetwork, tWidth=0.3):
        self.name = self.genAutoName()
        self.tWidth = tWidth
        self.gearList = []
        self.gearNetwork = gearNetwork

    def __del__(self): pass
        # if more than one neigbour: impossible I guess. 
        # delete transform / construct
        # delete circle
        # delete constraints. 

    def genAutoName(cls):
        name = "{}{}".format(cls.DEFAULT_PREFIX, cls.gearChainIdx)
        cls.gearChainIdx += 1
        return name

    # Redondant but used as signal callback for UI
    def setName(self, name):
        self.name = name

    # TODO : CANCELLED WHEN CHANGING RADIUS OF A GEAR....
    def changeTWidth(self, tWidth):
        for g in self.gearList:
            g.changeTWidth(tWidth)

    def addGear(self, radius, tLen=None, linkedGear=None, name=None):
        if self.gearList and not linkedGear:
            log.error("gearChain not empty, so new gear has to be connected.")
            return
        g = gear.Gear(name=name, radius=radius,
                      tWidth=self.tWidth, tLen=tLen,
                      linkedGear=linkedGear,
                      gearChain=self)
        self.gearList.append(g)
        return g

    # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def calculateMinTWidth(self):
        return 0.1

    def calculateMaxTWidth(self):
        return 0.8
