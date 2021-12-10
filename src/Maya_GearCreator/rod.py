import pymel.core as pm
import importlib

from Maya_GearCreator.maya_wrapper import maya_obj_descriptor as mob
# from Maya_GearCreator.misc import maya_obj_descriptor as mob
from Maya_GearCreator.misc import maya_helpers
from Maya_GearCreator import consts
from Maya_GearCreator.misc import py_helpers

importlib.reload(mob)
importlib.reload(maya_helpers)
importlib.reload(consts)
importlib.reload(py_helpers)


# TODO : CHANGING INTERNAL RADIUS of a gear ->
# if not rod -> just change raidus
# otherwise changing the radius of the rod
# rod -> change radius of all linked gears.

'''
cylinder faces:

"sub" -> SubdivisionsAxis

around  -> [0, sub -1 ]
bot     -> [sub, sub * 2 - 1]
top     -> [sub *2, sub *3 -1 ]

'''

class Rod(mob.MayaObjDescriptor):

    rodIdx = 0
    DEFAULT_PREFIX = "rod"

    def __init__(
            self, name=None,
            radius=consts.DEFAULT_ROD_RADIUS,
            height=consts.DEFAULT_ROD_LEN,
            linkedGear=None,
            gearNetwork=None,
            objExists=False,
            objTransform=None):

        if not objExists:
            objTransform, rodConstruct = pm.polyCylinder()

        super(Rod, self).__init__(
            objTransform,
            name,
            objExists,
            _class=Rod)

        if not objExists:
            self.addInput(rodConstruct, "cylinder")
            self.cylinder.radius = radius
            self.cylinder.height = height

        if linkedGear:
            self.translate = linkedGear.translate
        if gearNetwork:
            self.gearNetwork = gearNetwork

        self.setSubdivisionAxis(self.cylinder.subdivisionsAxis)

        self.lockTransform()

    def setSubdivisionAxis(self, subdivisionsAxis):
        self.cylinder.subdivisionsAxis = subdivisionsAxis

        self.topVertex = maya_helpers.formatMeshStr(self.name, "vertex",
                                               *self.getVtxIdx(top=True))
        self.botVertex = maya_helpers.formatMeshStr(self.name, "vertex",
                                               *self.getVtxIdx(top=False))

    def changeLen(self, newHeight, top=True):

        currentHeight = self.getLen(top=top)
        delta = newHeight - currentHeight
        pm.move(
            0, delta, 0,
            self.getVertexStr(top),
            r=True, os=True,
            wd=True)  # moveY=True)  # TODO: TO CHANGE IF MUTLIPLE ORIENTATION.

    def getVtxIdx(self, top=True):
        return {
            True: ((self.cylinder.subdivisionsAxis,
                    self.cylinder.subdivisionsAxis * 2 - 1),),
            False: ((0, self.cylinder.subdivisionsAxis - 1),)
        }[top]

    def getVertexStr(self, top=True):
        return {
            True: self.topVertex,
            False: self.botVertex
        }[top]

    # TODO : store at init. DO NOT CHANGE UNLESS BEVEL.
    def getLen(self, top=True):

        vtxs = maya_helpers.ls(self.name, "vertex", *self.getVtxIdx(top))
        # TODO: to change if multiple orientation.
        height = vtxs[0].getPosition(space="world")[1]
        return height

    LEN_MARGIN = 3

    def getMinMaxTop(self):
        gearList = self.getGears()
        topHeight = self.getLen(top=True)
        _max = topHeight + Rod.LEN_MARGIN
        if not gearList:
            _min = self.cylinder.height / 2
            return _min, _max
        else:
            _min = None
            for g in self.getGears():
                pos = g.translate[1]
                # TODO : Depends on orientation. !!!!!!!!!
                height = pos + g.gear.height / 2
                if not _min or height > _min:
                    _min = height
        return _min, _max

    # INVERTED! so factor in slider shall be negative! probably in setter/getter !!!
    def getMinMaxBot(self):
        gearList = self.getGears()
        botHeight = self.getLen(top=False)
        _max = botHeight - Rod.LEN_MARGIN
        if not gearList:
            _min = self.cylinder.height / 2
            return _min, _max
        else:
            _min = None
            for g in self.getGears():
                pos = g.translate[1]
                # TODO : Depends on orientation. !!!!!!!!!
                height = pos - g.gear.height / 2
                if not _min or height < _min:
                    _min = height
        return _min, _max

    def changeRadius(self, newRadius):
        # CHECKERS....
        self.cylinder.radius = newRadius
        for g in self.getGears():
            g.changeInternalRadius(newRadius)

    def getMaxRadius(self):
        max = min([g.getCurrentGearMaxInternalRadius() 
            for g in self.getGears()])
        if max is None:
            max = 1
        return max

    def _lockChain_recc(self, rootGear, lock=True):
        func = {
            True: mob.MayaObjDescriptor.activateParentConstraint,
            False: mob.MayaObjDescriptor.desactivateParentConstraint
        }
        gears = [g for g in self.getGears()
                    if g != rootGear]
        for g in gears:
            g.lockTransform(not lock)
            func[lock](self, *gears)
        for g in gears:
            new_gears, new_rod = g._find_children(self)
            g._lockChain_recc(*new_gears, lock=lock, rod=new_rod)

    def getGears(self):
        return self.gearNetwork.getGearsFromRod(self)

    def findFreeInterval(self):

        occupied_intervals = []
        _top = self.getLen(top=True)
        _bot = self.getLen(top=False)

        for gear in self.getGears():
            occupied_intervals.append(gear.calculateExtremum())
        occupied_intervals = sorted(occupied_intervals)

        freeInterverals = []
        _min = _bot
        for interval in occupied_intervals:
            local_min, local_max = interval
            if local_min > _min:
                freeInterverals.append((_min, local_min))
            if local_max < _top:
                _min = local_max
        if _min < _top:
            freeInterverals.append((_min, _top))

        sortedFreeIntervals = py_helpers.sortIntervalBySize(*freeInterverals)

        return sortedFreeIntervals

    def chooseHeight(self, gear):
        freeInterverals = self.findFreeInterval()
        canContainIntervals = py_helpers.canContainInterval(
            gear.calculateExtremum(),
            *freeInterverals)
        # if we can, trying to put new gear at the maximum top position.
        chosen_interval = max(canContainIntervals)
        return chosen_interval[0] + gear.gear.height / 2

    def _flipPartOfChain180_recc(self, rootGear, factor):
        gears = [g for g in self.getGears() if g != rootGear]
        for g in gears:
            g.lockTransform(False)
            pm.rotate(g.objTransform, [factor * 180, 0, 0], os=True, r=True)
            g.lockTransform(True)
        for g in gears:
            new_gears, new_rod = g._find_children(self)
            g._flipPartOfChain180_recc(factor, *new_gears, rod=new_rod)

