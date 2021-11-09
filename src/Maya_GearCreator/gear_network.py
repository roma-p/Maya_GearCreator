import importlib
import logging
import pymel.core as pm

from Maya_GearCreator import gear_chain
from Maya_GearCreator import rod
from Maya_GearCreator import consts
from Maya_GearCreator.misc import connections_manager

importlib.reload(gear_chain)
importlib.reload(rod)
importlib.reload(consts)
importlib.reload(connections_manager)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GearNetwork():
    DEFAULT_PREFIX = "gearNetwork"
    gearNetworkIdx = 0

    def __init__(self, name=None):
        name = name or self.genAutoName()
        self.gearDict = {}
        self.chainList = []
        self.multiChainGear = {}
        self.group = pm.group(em=True, name=name)
        self.name = name

        self.rodToChains = {}
        self.rodDict = {}
        self.rodsGroup = pm.group(em=True, name="rods")
        pm.parent(self.rodsGroup, self.name)

        self.rodManager = connections_manager.ConnectionsManager("rodLinked")


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
        self.chainList.append(chain)
        pm.parent(chain.group, self.name)
        if rod:
            self.rodToChains[rod].add(chain)
        return chain

    def addGear(
            self,
            gearChain,
            name=None,
            radius=consts.DEFAULT_RADIUS,
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None):

        gear = gearChain.addGear(name, radius, gearOffset, linkedGear)
        self.gearDict[gear.objTransform] = (gear, gearChain)
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
        self.gearDict[gear.objTransform] = (gear, gearChain)
        self.rodToChains[rod].add(gear.gearChain)
        self.connectRod(rod, gear)
        gearChain.rodList.append(rod)
        return rod

    def getGearFromTransform(self, transform):
        gearInfo = self.gearDict.get(transform)
        if gearInfo : return gearInfo[0]
        else : return None

    def delGear(self, gear):
        pass

    def addRod(self, gear):
        if not self.hasRod(gear):
            r = rod.Rod(
                linkedGear=gear,
                radius=gear.internalRadius,
                gearNetwork=self)
            self.rodToChains[r] = {gear.gearChain}
            self.rodDict[r.objTransform] = r
            gear.gearChain.rodList.append(r)
            self.connectRod(r, gear)
            pm.parent(r.name, self.rodsGroup)
            return r

    def getRodFromTransform(self, transform):
        rodInfo = self.rodDict.get(transform)
        if rodInfo : return rodInfo
        else : return None

    # HANDLNING RODS CONNECTIONS ----------------------------------------------

    def connectRod(self, rod, gear):
        self.rodManager.connect(gear, rod)

    def getRodFromGear(self, gear):
        rodList = self.rodManager.listConnections(gear)
        if rodList : return rodList[0]

    def getGearsFromRod(self, rod):
        return self.rodManager.listConnections(rod)

    def getGearFromRodOnChain(self, rod, gearChain):
        gearsOnRod = self.getGearsFromRod(rod)
        _tmp = [g for g in gearsOnRod if g in gearChain.gearList]
        if _tmp: return _tmp[0]
        else: return None


    def hasRod(self, gear):
        if self.getRodFromGear(gear): return True
        else: return False