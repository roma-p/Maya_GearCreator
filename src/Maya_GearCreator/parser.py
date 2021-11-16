import importlib
import logging
import pymel.core as pm

from Maya_GearCreator import gear_network
from Maya_GearCreator import gear_chain
from Maya_GearCreator import consts
from Maya_GearCreator.gears import gear_basic
from Maya_GearCreator.gears import gear_abstract
from Maya_GearCreator.misc import circle_descriptor
from Maya_GearCreator import rod

importlib.reload(gear_network)
importlib.reload(gear_chain)
importlib.reload(consts)
importlib.reload(gear_basic)
importlib.reload(gear_abstract)
importlib.reload(circle_descriptor)
importlib.reload(rod)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def parse():

    gns = [parseSingleGearNetwork(grp) for grp in getGearNetworksGroups()]

    # updating neigbour and constraint circles Manger internal dict.
    allGears = []
    allConstraintCircles = []

    for gn in gns:
        allGears += gn.listGears()
        allConstraintCircles += listAllConstraintCircles(gn)
    gear_abstract.GearAbstract.neighManager.parse(*allGears)

    gear_abstract.GearAbstract.cCirclesConnectManager.parse(
        *allGears + allConstraintCircles)
    return gns


def parseSingleGearNetwork(gearNetworkGroup):

    # 1  creating gearNetwork object
    parentGroup = pm.listRelatives(gearNetworkGroup, parent=True) or None
    gearNetwork = gear_network.GearNetwork(
        name=str(gearNetworkGroup),
        parentObj=parentGroup,
        networkExists=True,
        networkGroup=gearNetworkGroup)
    # 2 parsing and referencing gear chains
    gearChainList = []
    for gearChainGroup in getGearChainsGroups(gearNetwork):
        gearChainList.append(parseSingleGearChain(gearNetwork, gearChainGroup))
    gearNetwork.chainManager.parse(*gearChainList)
    # 3 parsing and referencing rods.
    rodList = []
    for rodTransform in getRodTransforms(gearNetwork):
        rodList.append(parseSingleRod(gearNetwork, rodTransform))
    gearNetwork.rodChildrenManager.parse(*rodList)
    gearNetwork.rodConnectManager.parse(*rodList + gearNetwork.listGears())
    #gearNetwork.rodConnectManager.parse(*rodList)
    return gearNetwork


def parseSingleGearChain(gearNetwork, gearChainGroup):

    gc = gear_chain.GearChain(
        gearNetwork,
        tWidth=gearChainGroup.getAttr("tWidth"),
        name=str(gearChainGroup),
        chainExists=True,
        chainGroup=gearChainGroup)
    gearNetwork.chainManager.add(gc)

    gc.height = gearChainGroup.getAttr("height")  # FIXME ? automatique?
    gearList = []
    for gearTransform in getGearTransforms(gc):
        gear = parseSingleGear(gc, gearTransform)
        gearList.append(gear)
    gc.gearList.parse(*gearList)
    return gc


def parseSingleGear(gearChain, gearTransform):
    gearInput = getInputs(gearTransform, inputType=pm.nodetypes.PolyGear)[0]
    gear = gear_basic.GearBasic(
        name=str(gearTransform),
        radius=gearInput.radius.get() + gearInput.gearOffset.get(),
        tWidth=gearChain.tWidth,
        gearOffset=gearInput.gearOffset.get(),
        gearChain=gearChain,
        gearExists=True,
        gearData=(gearTransform, gearInput))
    circleList = []
    for circleTransform in getCircleTransforms(gear):
        circleList.append(parseSingleCircle(gear, circleTransform))
    gear.cCirclesChildrenManager.parse(*circleList)
    return gear


def parseSingleCircle(gear, circleTransform):
    circleInput = getInputs(circleTransform,
                            inputType=pm.nodetypes.MakeNurbCircle)[0]
    return circle_descriptor.CircleDescriptor(
        circleExists=True,
        circleData=(circleTransform, circleInput))


def parseSingleRod(gearNetwork, rodTransform):
    rodInput = getInputs(rodTransform, pm.nodetypes.PolyCylinder)[0]
    radius = rodInput.radius.get()
    r = rod.Rod(
        gearNetwork=gearNetwork,
        rodExists=True,
        rodData=(rodTransform, rodInput))
    r.radius = radius
    return r

# LISTING GROUPS --------------------------------------------------------------


def getGearNetworksGroups():
    allGeatNetworks = [
        t for t in pm.ls(type="transform")
        if t.hasAttr(consts.TAG_GEARNETWORK)]
    return allGeatNetworks


def getGearChainsGroups(gearNetwork):
    gearChainGroups = []
    for child in pm.listRelatives(gearNetwork.group, c=True):
        if child.hasAttr(consts.TAG_GEARCHAIN):
            gearChainGroups.append(child)
    return gearChainGroups


def getGearTransforms(gearChain):
    gearTransform = []
    for child in pm.listRelatives(gearChain.group, c=True):
        if child.hasAttr(consts.TAG_GEAR):
            gearTransform.append(child)
    return gearTransform


def getCircleTransforms(gear):
    circleTransform = []
    for child in pm.listRelatives(gear.objTransform, c=True):
        if child.hasAttr(consts.TAG_CONSTRAINTS_C):
            circleTransform.append(child)
    return circleTransform


def getRodTransforms(gearNetwork):
    rodTransforms = []
    for child in pm.listRelatives(gearNetwork.rodsDescriptor.group, c=True):
        if child.hasAttr(consts.TAG_ROD):
            rodTransforms.append(child)
    return rodTransforms


def getInputs(transform, inputType=None):
    ret = []
    for _input in transform.getShape().inputs():
        if inputType:
            if isinstance(_input, inputType):
                ret.append(_input)
        else:
            ret.append(_input)
    return ret


def listAllConstraintCircles(gn):
    constraintCircles = []
    for gear in gn.listGears():
        constraintCircles += list(gear.cCirclesChildrenManager)
    return constraintCircles
