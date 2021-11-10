import importlib
import logging
import pymel.core as pm

from Maya_GearCreator import gear_chain
from Maya_GearCreator import rod
from Maya_GearCreator import consts
from Maya_GearCreator.misc import helpers
from Maya_GearCreator.misc import children_manager as childrenM
from Maya_GearCreator.misc import connections_manager as connectionM

importlib.reload(gear_chain)
importlib.reload(rod)
importlib.reload(consts)
importlib.reload(connectionM)
importlib.reload(childrenM)
importlib.reload(helpers)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GearNetwork():
    DEFAULT_PREFIX = "gearNetwork"
    TAG = "GEARNETWORK"

    # better unique name....

    gearNetworkIdx = 0

    def __init__(self, name=None):
        name = name or self.genAutoName()

        # TODO : -> IF GROUP EXIST: NOT CREATE IT BUT REFERENCE IT.
        # SO FUNCTION IN HELPERS 'CREATE DIR' -> if already exists only return it. 

        # handling gear chains.
        self.group = pm.group(em=True, name=name)
        self.chainManager = childrenM.ChildrenManager_GrpDescriptor(self.group)

        # handling rods:
        self.rodsGroup = pm.group(em=True, name="rods")
        pm.parent(self.rodsGroup, self.name)
        # storing rods.
        self.rodChildrenManager = childrenM.ChildrenManager_ObjDescriptor(
            self.rodsGroup, "rod")
        # storing connection between rods and gears.
        self.rodConnectManager = connectionM.ConnectionsManager("rodLinked")

        # adding Tag tag
        helpers.addTag(self.group, GearNetwork.TAG)

        self.name = name

    # HANDLING NAME -----------------------------------------------------------

    def genAutoName(cls):
        name = "{}{}".format(cls.DEFAULT_PREFIX, cls.gearNetworkIdx)
        cls.gearNetworkIdx += 1
        return name

    # Redondant but used as signal callback for UI
    def setName(self, name):
        self.name = name

    @property
    def name(self):
        return str(self.group)

    @name.setter
    def name(self, name):
        pm.rename(self.group, name)

    def addChain(self, tWidth=0.3, rod=None):
        chain = gear_chain.GearChain(self, tWidth)
        self.chainManager.add(chain)
        return chain

    def addGear(
            self,
            gearChain,
            name=None,
            radius=consts.DEFAULT_RADIUS,
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None):
        gear = gearChain.addGear(name, radius, gearOffset, linkedGear)
        return gear

    def addGearOnRod(
            self, rod, gearChain, name=None,
            radius=consts.DEFAULT_RADIUS,
            gearOffset=consts.DEFAULT_GEAR_OFFESET):

        gear = gearChain.addGear(
            name=name,
            radius=radius,
            gearOffset=gearOffset,
            linkedRod=rod)
        gear.internalRadius = rod.radius
        self.connectRod(rod, gear)
        return gear

    def getGearFromTransform(self, transform):
        for gearChain in self.chainManager:
            gear = gearChain.gearList.getDescriptor(transform)
            if gear:
                return gear

    def delGear(self, gear):
        pass

    def addRod(self, gear):
        if not self.hasRod(gear):
            r = rod.Rod(
                linkedGear=gear,
                radius=gear.internalRadius,
                gearNetwork=self)
            self.connectRod(r, gear)
            self.rodChildrenManager.add(r)
            return r

    def getRodFromTransform(self, transform):
        return self.rodChildrenManager.getDescriptor(transform)

    # HANDLNING RODS CONNECTIONS ----------------------------------------------

    def connectRod(self, rod, gear):
        self.rodConnectManager.connect(gear, rod)

    def getRodFromGear(self, gear):
        rodList = self.rodConnectManager.listConnections(gear)
        if rodList:
            return rodList[0]

    def getGearsFromRod(self, rod):
        return self.rodConnectManager.listConnections(rod)

    def getGearFromRodOnChain(self, rod, gearChain):
        gearsOnRod = self.getGearsFromRod(rod)
        _tmp = [g for g in gearsOnRod if g in gearChain.gearList]
        if _tmp:
            return _tmp[0]
        else:
            return None

    def hasRod(self, gear):
        if self.getRodFromGear(gear):
            return True
        else:
            return False

    def listRodChains(self, rod):
        return set([g.gearChain for g in self.getGearsFromRod(rod)
            if g.gearChain])

    def getRodsOnChains(self, gearChain):
        ret = set()
        for gear in gearChain.gearList:
            rod = self.getRodFromGear(gear)
            if rod:
                ret.add(rod)
        return ret
