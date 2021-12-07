import importlib
import logging

from Maya_GearCreator.gears import gear_basic
from Maya_GearCreator.gears import gear
from Maya_GearCreator import consts
from Maya_GearCreator.misc import maya_helpers
from Maya_GearCreator.maya_wrapper import maya_obj_descriptor

importlib.reload(gear_basic)
importlib.reload(gear)
importlib.reload(consts)
importlib.reload(maya_helpers)
importlib.reload(maya_obj_descriptor)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class GearChain(maya_obj_descriptor.MayaObjDescriptor):

    DEFAULT_PREFIX = "gearChain"
    groupIdx = 0

    def __init__(
            self, gearNetwork,
            name=None, tWidth=0.3,
            chainExists=False,
            chainGroup=None):

        super(GearChain, self).__init__(
            name=name,
            parentTransform=gearNetwork.objTransform,
            objExists=chainExists,
            objTransform=chainGroup,
            group=True,
            _class=GearChain)

        self.gearList = self.createChildrenM(tag=consts.TAG_GEAR)
        # TODO : change name. -> gearManager.

#        self.height = 0

        maya_helpers.safeAddAttr(self.objTransform, "tWidth", "float", True)
        maya_helpers.safeAddAttr(self.objTransform, "height", "float", True)

        if tWidth:
            self.tWidth = tWidth

        self.gearNetwork = gearNetwork

    # Twidth ------------------------------------------------------------------

    @property
    def tWidth(self):
        return self.objTransform.tWidth.get()

    @tWidth.setter
    def tWidth(self, tWidth):
        self.objTransform.tWidth.set(tWidth)

    # TODO : CANCELLED WHEN CHANGING RADIUS OF A GEAR.... HEIN?
    def changeTWidth(self, tWidth):
        self.tWidth = tWidth
        for g in self.gearList:
            g.changeTWidth(tWidth)

    @tWidth.setter
    def tWidth(self, tWidth):
        self.objTransform.tWidth.set(tWidth)

    # Height ------------------------------------------------------------------

    @property
    def height(self):
        return self.objTransform.height.get()

    @height.setter
    def height(self, height):
        self.objTransform.height.set(height)

    def changeHeight(self, height):
        if not self.listRod():
            return
        _min, _max = self.calculateMinMaxHeight()
        if height < _min or height > _max:
            return
        for g in self.gearList:
            g.changeHeight(height)
        self.height = height

    # -------------------------------------------------------------------------

    def addGear(
            self, name=None,
            radius=consts.DEFAULT_RADIUS,
            gearOffset=consts.DEFAULT_GEAR_OFFSET,
            linkedGear=None,
            linkedRod=None):

       # if len(self.gearList) > 0 and not linkedGear:
           # log.error("gearChain not empty, so new gear has to be connected.")
           # return

        g = gear_basic.GearBasic(
            name=name,
            radius=radius,
            tWidth=self.tWidth,
            gearOffset=gearOffset,
            linkedGear=linkedGear,
            linkedRod=linkedRod,
            gearChain=self)
        self.gearList.add(g)
        return g

    # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def calculateMinTWidth(self):
        return 0.1

    def calculateMaxTWidth(self):
        return 0.8

    def calculateMinMaxHeight(self):
        _min = None
        _max = None

        for rod in self.listRod():

            gear = self.gearNetwork.getGearFromRodOnChain(rod, self)

            pos = rod.translate[1]  # TODO : Depends on orientation. !!!!!!!!!
            # _rodDelta = rod.height / 2
            _gearDelta = gear.gear.height / 2

            _tmp_min = rod.getLen(top=False) + _gearDelta
            _tmp_max = rod.getLen(top=True) - _gearDelta

            if not _min or _tmp_min > _min:
                _min = _tmp_min
            if not _max or _tmp_max < _max:
                _max = _tmp_max
        if _min is None and _max is None:
            return 0, 1
        return _min, _max

    def listRod(self):
        return self.gearNetwork.getRodsOnChains(self)
