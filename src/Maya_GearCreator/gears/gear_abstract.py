import math
import logging
import pymel.core as pm
import importlib

from Maya_GearCreator import consts
from Maya_GearCreator import gear_chain
from Maya_GearCreator.misc import circle_descriptor
from Maya_GearCreator.misc import connections_manager
from Maya_GearCreator.misc import maya_obj_descriptor as mob
from Maya_GearCreator.misc import children_manager

importlib.reload(consts)
importlib.reload(gear_chain)
importlib.reload(circle_descriptor)
importlib.reload(connections_manager)
importlib.reload(mob)
importlib.reload(children_manager)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def transform(f):
    def wrapper(*args, **kargs):
        args[0].lockTransform(False)
        ret = f(*args, **kargs)
        args[0].lockTransform(True)
        return ret
    return wrapper

class GearAbstract(mob.MayaObjDescriptor):

    gearIdx = 0
    DEFAULT_PREFIX = "gear"

    neighManager = connections_manager.ConnectionsManager(
        consts.TAG_CONNECT_NEIGHBOUR)
    cCirclesConnectManager = connections_manager.ConnectionsManager(
        consts.TAG_CONNECT_CONSTRAINTS_C)

    def __init__(
            self,
            gear_shape,
            gear_construct,
            name=None,
            radius=consts.DEFAULT_RADIUS,
            tWidth=consts.DEFAULT_TWIDTH,
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None,
            gearChain=None,
            linkedRod=None,
            _class=None):

        _class = _class or GearAbstract

        super().__init__(
            gear_shape,
            gear_construct,
            _class,
            name)

        self.shader_bk = None

        # ADJUSTING SHAPE -----------------------------------------------------
        self.radius = radius - gearOffset
        self.gearOffset = gearOffset
        self.sides = GearAbstract.calculateTNumber(tWidth, self.radius)

        # HANDLNING NEIGHBOURS ------------------------------------------------
        self.circleConstraints = []

        # HANDLING CONSTRAINT_CIRCLES
        self.cCirclesChildrenManager = self.createObjChildrenM(
            tag=consts.TAG_CONSTRAINTS_C)

        if linkedGear:
            self.addNeighbour(linkedGear)
            self.adjustGearToCircleConstraint(linkedGear)

        if linkedRod:
            self.translate = linkedRod.translate

        self.gearChain = gearChain
        self.tWidth = tWidth

        self.lockTransform(True)

    def instantiateGear():
        # pm.polyPipe func buggy : accept no arg and return nothing
        # transform and constructor has to be fetched manually
        # and transform renamed after (unlike all other primitive.)
        pm.polyGear()
        gear_shape = pm.ls(selection=True)[0]
        for node in pm.listHistory(gear_shape):
            if isinstance(node, pm.nodetypes.PolyGear):
                gear_construct = node
                break
        return gear_shape, gear_construct

    # PROPERTIES --------------------------------------------------------------
    @property
    def tWidth(self):
        if self.gearChain:
            return self.gearChain.tWidth
        else:
            return self._tWidth

    @tWidth.setter
    def tWidth(self, tWidth):
        if not self.gearChain:
            self._tWidth = tWidth

    # CALCULATION -------------------------------------------------------------

    def calculateConstraintRadius(parentGear, childGear):
        return parentGear.radius + (parentGear.gearOffset / 2) \
            + childGear.radius + (childGear.gearOffset / 2)

    def calculateAdjustedRadius(self, radius):
        radius = radius or self.radius
        return radius - self.gearOffset

    def calculateTNumber(tWidth, radius):
        tNumber = int(radius * math.pi / tWidth)
        return tNumber

    # MANAGE NEIGHBOURS -------------------------------------------------------
    def listNeigbours(self):
        return GearAbstract.neighManager.listConnections(self)

    def isConnected(self, gear):
        return GearAbstract.neighManager.isConnected(self, gear)

    # TODO : del circles.
    def delNeighbour(self, gear):
        GearAbstract.neighManager.disconnect(self, gear)

    def addNeighbour(self, gear):
        GearAbstract.neighManager.connect(self, gear)
        self.initCircleConstraint(gear)
        gear.initCircleConstraint(self)

    # MANAGE CONSTRAINT CIRCLE ------------------------------------------------
    def addConstraintCircle(self, neighbourGear, circle):
        GearAbstract.cCirclesConnectManager.connect(circle, neighbourGear)
        self.cCirclesChildrenManager.add(circle)

    def getRelatedConstraintCircle(self, neighbourGear):
        return next(
            g for g in GearAbstract.cCirclesConnectManager.listConnections(neighbourGear)
            if g in self.cCirclesChildrenManager)

    # MODIFY ------------------------------------------------------------------

    def changeTWidth(self, tWidth):
        self.sides = GearAbstract.calculateTNumber(tWidth, self.radius)

    def changeRadius(self, radius):
        raise NotImplementedError()

    def activateMoveMode(self, rootGear):
        # 1 define constraint to move along root gear
        self.moveMode = rootGear
        self.activateCircleConstraint(rootGear)
        # 2 lock the rest of the chain.
        self.lockChain(rootObj=rootGear, lock=True)
        pm.setAttr(self.name + ".translate", lock=False)
        # 3 TODO: SHOW / HIDE CONSTRAINT CIRCLE.
        # TODO 4 !!!!!!!
        # MEMORIZE BASE POS.
        # self.basePos = .... get transform.
        # ds move along -> calculer la soustraction.
        self.basePos = self.translate[2]
        self.currentPos = self.basePos

    def desactivateMoveMode(self):
        if not self.moveMode: return
        self.desactivateCircleConstraint(self.moveMode)
        self.lockChain(rootObj=self, lock=False)
        # self.lockChain(*[g for g in self.listNeigbours() if g != self], lock=False)
        self.lockTransform()

    def calculateMoveAlong(self, rootGear):
        constraintsCircle = self.getRelatedConstraintCircle(rootGear)
        return 2 * math.pi * constraintsCircle.radius

        #TODO : radius du circle COnstraint espece de débile.
        #radius = self.radius + self.gearOffset / 2
        #perimeter = 2 * math.pi * radius
        #return perimeter
        # calculate radius + Tlen / 2 -> perimeter: max distance



    def moveAlong_Slider(self, distance):
        newZ = distance - self.currentPos
        if distance < self.currentPos:
            newZ = - newZ
        pm.move(self.objTransform, [0, 0, newZ],
                os=True, r=True, wd=True)
        # save current pos -> if new is lower -> move difference in negative.
        # EN FAIT NON. RETENIR LA VALEUR DU SLIDER + LA VALEUR DE LA POS.
        # LA VALEUR DU SLIDER SERT AU SIGNE, LA VALEUR DE LA POS A LA DISTANCE.

    def moveAlong(self, distance):
        pm.move(self.objTransform, [0, 0, distance],
                os=True, r=True, wd=True)

    @transform
    def changeHeight(self, height):
        x, y, z = self.translate
        self.translate = (x, height, z)
        # TODO : to change when multiple orientaion.

    def changeInternalRadius(self, newRadius):
        # TODO : checks.
        r = self.gearChain.gearNetwork.getRodFromGear(self)
        if not r:
            self.internalRadius = newRadius
        else:
            r.changeRadius(newRadius)

    # CONSTRAINTS -------------------------------------------------------------

    @transform
    def initCircleConstraint(self, neighbourGear):
        circle = circle_descriptor.CircleDescriptor(
            nr=(0, 1, 0),
            # axis is X-Y TODO: to update when multiple orientation implemented
            radius=GearAbstract.calculateConstraintRadius(self, neighbourGear))
        pm.move(circle.objTransform, neighbourGear.translate)
        circle.visibility = False

        self.addConstraintCircle(neighbourGear, circle)

        pm.parentConstraint(neighbourGear.objTransform,
                            circle.objTransform)

    @transform
    def activateCircleConstraint(self, neighbourGear):
        constraintsCircle = self.getRelatedConstraintCircle(neighbourGear)
        self.circleConstraints = [
            pm.geometryConstraint(
                constraintsCircle.objTransform,
                self.objTransform),
            pm.aimConstraint(neighbourGear.objTransform, self.objTransform)
        ]
        constraintsCircle.visibility = True

    def desactivateCircleConstraint(self, neighbourGear):
        self.getRelatedConstraintCircle(neighbourGear).visibility = False
        for constraint in self.circleConstraints:
            pm.delete(constraint)
        self.circleConstraints = []

    def adjustGearToCircleConstraint(self, neighbourGear):
        self.activateCircleConstraint(neighbourGear)
        self.desactivateCircleConstraint(neighbourGear)

    def activateParentConstraint(self, *gears):
        for gear in gears:
            self.parentConstraints.append(
                pm.parentConstraint(self.objTransform, gear.objTransform,
                                    maintainOffset=True))

    def desactivateParentConstraint(self, *gears):
        for constraint in self.parentConstraints:
            pm.delete(constraint)
        self.parentConstraints = []

    def lockChain(self, rootObj, lock=True):
        gears, r = self._find_children(rootObj)
        self._lockChain_recc(*gears, lock=lock, rod=r)

    def _lockChain_recc(self, *neighboursGear, lock=True, rod=None):
        func = {
            True: mob.MayaObjDescriptor.activateParentConstraint,
            False: mob.MayaObjDescriptor.desactivateParentConstraint
        }
        allObj = list(neighboursGear)
        if rod:
            allObj.append(rod)
        for obj in allObj:
            obj.lockTransform(not lock)
        func[lock](self, *allObj)
        for g in neighboursGear:
            new_gears, new_rod = g._find_children(self)
            g._lockChain_recc(*new_gears, lock=lock, rod=new_rod)
        if rod:
            rod._lockChain_recc(self, lock=lock)

    def _find_children(self, rootObj):
        ret_gears = [g for g in self.listNeigbours() if g != rootObj]
        r = self.gearChain.gearNetwork.getRodFromGear(self)
        if r and r != rootObj:
            ret_rod = r
        else:
            ret_rod = None
        return ret_gears, ret_rod

    # SHADER ------------------------------------------------------------------

    def setTmpShader(self, sg):
        self.shader_bk = self._getCurrentShader()
        self._setShader(sg)
        pass

    def restorShader(self):
        if self.shader_bk:
            for s in self.shader_bk:
                pm.sets(s, forceElement=self.objTransform)

    def _setShader(self, sg):
        pm.sets(sg, forceElement=self.objTransform)

    def _getCurrentShader(self):
        shadeEng = pm.listConnections(self.objTransform.getShape(),
                                      type="shadingEngine")
        return shadeEng
