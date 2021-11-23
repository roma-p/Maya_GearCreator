import importlib
import logging

from Maya_GearCreator import gear_chain
from Maya_GearCreator import rod
from Maya_GearCreator import consts
from Maya_GearCreator.misc import maya_helpers
from Maya_GearCreator.maya_wrapper import children_manager as childrenM
from Maya_GearCreator.maya_wrapper import connections_manager as connectionM
from Maya_GearCreator.misc import maya_grp_descriptor
from Maya_GearCreator.maya_wrapper import maya_obj_descriptor


importlib.reload(gear_chain)
importlib.reload(rod)
importlib.reload(consts)
importlib.reload(connectionM)
importlib.reload(childrenM)
importlib.reload(maya_helpers)
importlib.reload(maya_grp_descriptor)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GearNetwork(maya_obj_descriptor.MayaObjDescriptor):

    DEFAULT_PREFIX = "gearNetwork"
    groupIdx = 0

    def __init__(
            self,
            name=None, parentTransform=None,
            networkExists=False,
            networkGroup=None):

        super(GearNetwork, self).__init__(
            name=name,
            parentTransform=parentTransform,
            objExists=networkExists,
            group=True,
            objTransform=networkGroup,
            _class=GearNetwork)

        # gear chain handler.
        self.chainManager = self.createObjChildrenM(consts.TAG_GEARCHAIN)

        # rods subgroup and rods handler.
        if networkExists:
            rodGroup = maya_helpers.getGroup(
                consts.ROD_SUBGROUP,
                self.objTransform)

            self.rodsDescriptor = maya_obj_descriptor.MayaObjDescriptor(
                name=consts.ROD_SUBGROUP,
                parentTransform=self.objTransform,
                group=True,
                objTransform=rodGroup,
                objExists=True)
        else:

            self.rodsDescriptor = maya_obj_descriptor.MayaObjDescriptor(
                name=consts.ROD_SUBGROUP,
                parentTransform=self.objTransform,
                group=True)

        self.rodChildrenManager = self.rodsDescriptor.createObjChildrenM(
            tag=consts.TAG_ROD)
        self.rodConnectManager = connectionM.ConnectionsManager(
            consts.TAG_CONNECT_ROD)

        # adding Tag tag
        maya_helpers.addTag(self.objTransform, consts.TAG_GEARNETWORK)

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

        if rod.cylinder.radius > radius + gearOffset + consts.ROD_GEAR_OFFSET:
            radius = rod.cylinder.radius + gearOffset + consts.ROD_GEAR_OFFSET

        gear = gearChain.addGear(
            name=name,
            radius=radius,
            gearOffset=gearOffset,
            linkedRod=rod)
        gear.internalRadius = rod.cylinder.radius
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
                radius=gear.gear.internalRadius,
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
