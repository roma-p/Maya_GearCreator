import importlib
import logging
import pymel.core as pm

from Maya_GearCreator.gears import gear_basic
from Maya_GearCreator.gears import gear
from Maya_GearCreator import consts

importlib.reload(gear_basic)
importlib.reload(gear)
importlib.reload(consts)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class GearChain():

    DEFAULT_PREFIX = "gearChain"
    DEFAULT_TWIDTH = 0.3
    gearChainIdx = 0

    def __init__(self, gearNetwork, tWidth=0.3):
        name = self.genAutoName()
        self.gearList = []
        self.gearNetwork = gearNetwork
        self.group = pm.group(em=True, name=name)
        self.name = name

        self.group.addAttr(
            "tWidth", 
            keyable=True,
            attributeType="float")
        self.tWidth = tWidth


    def __del__(self): pass
        # if more than one neigbour: impossible I guess. 
        # delete transform / construct
        # delete circle
        # delete constraints. 

    # HANDLING NAME -----------------------------------------------------------

    def genAutoName(cls):
        name = "{}{}".format(cls.DEFAULT_PREFIX, cls.gearChainIdx)
        cls.gearChainIdx += 1
        return name

    @property
    def name(self):
        return str(self.group)

    @name.setter
    def name(self, name):
        pm.rename(self.group, name)

    # Redondant but used as signal callback for UI
    def setName(self, name):
        self.name = name

    # Twidth ------------------------------------------------------------------

    @property
    def tWidth(self):
        return self.group.tWidth.get()

    @tWidth.setter
    def tWidth(self, tWidth):
        self.group.tWidth.set(tWidth)

    # TODO : CANCELLED WHEN CHANGING RADIUS OF A GEAR.... HEIN? 
    def changeTWidth(self, tWidth):
        self.tWidth = tWidth
        for g in self.gearList:
            g.changeTWidth(tWidth)

    # -------------------------------------------------------------------------

    def addGear(
            self, name=None,
            radius=consts.DEFAULT_RADIUS, 
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None):

        if self.gearList and not linkedGear:
            log.error("gearChain not empty, so new gear has to be connected.")
            return
        g = gear_basic.GearBasic(
            name=name, 
            radius=radius,
            tWidth=self.tWidth,
            gearOffset=gearOffset,
            linkedGear=linkedGear,
            gearChain=self)#
        self.gearList.append(g)
        pm.parent(g.objTransform, self.name)
        return g

    # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def calculateMinTWidth(self):
        return 0.1

    def calculateMaxTWidth(self):
        return 0.8
