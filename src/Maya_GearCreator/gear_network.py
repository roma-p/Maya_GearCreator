import importlib
import logging

from Maya_GearCreator import gear_chain
from Maya_GearCreator import rod
from Maya_GearCreator import consts
from Maya_GearCreator.misc import maya_helpers
from Maya_GearCreator.misc import children_manager as childrenM
from Maya_GearCreator.misc import connections_manager as connectionM
from Maya_GearCreator.misc import maya_grp_descriptor

importlib.reload(gear_chain)
importlib.reload(rod)
importlib.reload(consts)
importlib.reload(connectionM)
importlib.reload(childrenM)
importlib.reload(maya_helpers)
importlib.reload(maya_grp_descriptor)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GearNetwork(maya_grp_descriptor.MayaGrpDescriptor):

    DEFAULT_PREFIX = "gearNetwork"
    groupIdx = 0

    def __init__(
            self,
            name=None, parentObj=None,
            networkExists=False,
            networkGroup=None):

        super(GearNetwork, self).__init__(
            name=name, parentObj=parentObj,
            groupExists=networkExists, group=networkGroup)

        # gear chain handler.
        self.chainManager = self.createGrpChildrenM(consts.TAG_GEARCHAIN)

        # rods subgroup and rods handler.

        if networkExists:
            rodGroup = maya_helpers.getGroup(
                consts.ROD_SUBGROUP,
                self.group)
            self.rodsDescriptor = maya_grp_descriptor.MayaGrpDescriptor(
                name=consts.ROD_SUBGROUP,
                parentObj=self.group,
                groupExists=True,
                group=rodGroup)
        else:
            self.rodsDescriptor = maya_grp_descriptor.MayaGrpDescriptor(
                name=consts.ROD_SUBGROUP,
                parentObj=self.group)
        self.rodChildrenManager = self.rodsDescriptor.createObjChildrenM(
            tag=consts.TAG_ROD)
        self.rodConnectManager = connectionM.ConnectionsManager(
            consts.TAG_CONNECT_ROD)

        # adding Tag tag
        maya_helpers.addTag(self.group, consts.TAG_GEARNETWORK)

    def addChain(self, tWidth=0.3, name=None):
        chain = gear_chain.GearChain(self, tWidth=tWidth, name=name)
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

        if rod.radius > radius + gearOffset + consts.ROD_GEAR_OFFSET:
            radius = rod.radius + gearOffset + consts.ROD_GEAR_OFFSET

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

    def listGears(self):
        ret = []
        for gearChain in self.chainManager:
            ret += list(gearChain.gearList)
        return ret
