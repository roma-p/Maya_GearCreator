import math
import logging
import pymel.core as pm
import importlib

from Maya_GearCreator import consts
from Maya_GearCreator import gear_chain
from Maya_GearCreator.misc import maya_helpers
from Maya_GearCreator.maya_wrapper import connections_manager
from Maya_GearCreator.maya_wrapper import maya_obj_descriptor as mob

importlib.reload(consts)
importlib.reload(gear_chain)
importlib.reload(maya_helpers)
importlib.reload(connections_manager)
importlib.reload(mob)

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
            gear_construct=None,
            name=None,
            radius=consts.DEFAULT_RADIUS,
            tWidth=consts.DEFAULT_TWIDTH,
            gearOffset=consts.DEFAULT_GEAR_OFFSET,
            linkedGear=None,
            gearChain=None,
            linkedRod=None,
            _class=None,
            objExists=False):

        _class = _class or GearAbstract

        super().__init__(
            objTransform=gear_shape,
            name=name,
            _class=_class,
            objExists=objExists)

        if not objExists:
            self.addInput(gear_construct, "gear")

        self.shader_bk = None

        # ADJUSTING SHAPE -----------------------------------------------------
        self.gear.radius = radius - gearOffset
        self.gear.gearOffset = gearOffset
        self.gear.sides = GearAbstract.calculateTNumber(tWidth,
                                                        self.gear.radius)

        # HANDLNING NEIGHBOURS ------------------------------------------------
        self.circleConstraints = []

        # HANDLING CONSTRAINT_CIRCLES
        self.cCirclesChildrenManager = self.createChildrenM(
            tag=consts.TAG_CONSTRAINTS_C)

        self.gearChain = gearChain
        self.tWidth = tWidth

        if linkedGear:
            self.addNeighbour(linkedGear)

            self.setParrallelAtInit(linkedGear)
            self.adjustGearToCircleConstraint(linkedGear)

        if linkedRod:
            self.translate = linkedRod.translate

        self.lockTransform(True)

    @transform
    def setParrallelAtInit(self, linkedGear):
        if linkedGear.isParrallelToGnd():
            return
        self.rotate = [linkedGear.rotate[0], 0, 90]
        self.translate = linkedGear.translate

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

    def calculateConstraintRadius(parentGear, childGear, orientation=0):
        if not orientation:
            return parentGear.gear.radius + (parentGear.gear.gearOffset / 2) \
                + childGear.gear.radius + (childGear.gear.gearOffset / 2)
        else:
            return parentGear.gear.radius + (parentGear.gear.gearOffset / 2) \
                + childGear.gear.height / 2

    def calculateAdjustedRadius(self, radius):
        radius = radius or self.gear.radius
        return radius - self.gear.gearOffset

    def calculateTNumber(tWidth, radius):
        tNumber = int(radius * math.pi / tWidth)
        return tNumber

    # TODO : depends on orientation.
    def calculateExtremum(self):
        delta = self.gear.height / 2
        center = self.translate[1]
        return center - delta, center + delta

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

    # Height / TWidth --

    def changeTWidth(self, tWidth):
        self.gear.sides = GearAbstract.calculateTNumber(tWidth,
                                                        self.gear.radius)

    @transform
    def changeHeight(self, height):
        x, y, z = self.translate
        self.translate = (x, height, z)
        # TODO : to change when multiple orientaion.

    # Radius an internal radius --

    def changeRadius(self, radius):
        raise NotImplementedError()

    def changeInternalRadius(self, radius):
        raise NotImplementedError()

    # if rod: change internal radius for all gears on current gear's rod.
    def smartChangeInternalRadius(self, newRadius):
        r = self.gearChain.gearNetwork.getRodFromGear(self)
        if not r:
            self.gear.internalRadius = newRadius
        else:
            r.changeRadius(newRadius)

    def getCurrentGearMaxInternalRadius(self):
        return self.gear.radius - consts.ROD_GEAR_OFFSET

    def getMaxInternalRadius(self):
        r = self.gearChain.gearNetwork.getRodFromGear(self)
        if r:
            return r.getMaxRadius()
        else:
            return self.getCurrentGearMaxInternalRadius()

    def getInternalRadius(self):
        raise NotImplementedError()

    # Move along other gears --

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
        self.lockTransform(False)
        self.rotate = self.moveMode.rotate
        self.lockTransform(True)
        self.moveMode = None
        self.lockChain(rootObj=self, lock=False)
        # self.lockChain(*[g for g in self.listNeigbours() if g != self], lock=False)
        self.lockTransform()

    def calculateMoveAlong(self, rootGear):
        constraintsCircle = self.getRelatedConstraintCircle(rootGear)
        return 2 * math.pi * constraintsCircle.circle.radius

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

    def _shiftCircleConstr(gear1, gear2, parrallel=True, positive=False):
        c = gear1.getRelatedConstraintCircle(gear2)
        if parrallel:
            orientation = 0
        else:
            orientation = 1
        c.circle.radius = GearAbstract.calculateConstraintRadius(gear2, gear1,
                                                                 orientation)
        if not positive:
            pm.move(
                c.objTransform,
                [
                    0,
                    - gear1.gear.radius - gear2.gear.height / 2,
                    0
                ],
                os=True, r=True, wd=True)
        else:
            pm.move(
                c.objTransform,
                [
                    0,
                    + gear1.gear.radius + gear2.gear.height / 2,
                    0
                ],
                os=True, r=True, wd=True)

    def getOrientation(self):
        return GearAbstract.convAngle2Orientation(self.rotate[2])

    @transform
    def changeOrientation(self, orientation, neighbourGear):
        if self.isParrallel(neighbourGear):
            self.orienGear(neighbourGear)
        self.lockChain(neighbourGear, lock=True)
        self._setParrallel(neighbourGear)
        # self.orienGear(neighbourGear)
        if orientation == 0:
            self.lockChain(neighbourGear, lock=False)
            return

        if neighbourGear.isParrallelToGnd():
            pm.rotate(
                self.objTransform,
                [0, 0, orientation * 90],
                os=True, r=True)
            pm.move(
                self.objTransform,
                [
                    - (self.gear.radius + neighbourGear.gear.height / 2),
                    -orientation * (self.gear.radius - neighbourGear.gear.gearOffset),
                    0
                ],
                os=True, r=True, wd=True)

        if orientation == - 1:
            positive = True
        else:
            positive = False

        self.lockChain(neighbourGear, lock=False)

        if orientation == -1:
            self.flipPartOfChain180(neighbourGear)

        GearAbstract._shiftCircleConstr(self, neighbourGear, parrallel=False, positive=positive)
        GearAbstract._shiftCircleConstr(neighbourGear, self, parrallel=False, positive=False)

    def _setParrallel(self, neighbourGear):

        GearAbstract._shiftCircleConstr(self, neighbourGear, parrallel=True)
        GearAbstract._shiftCircleConstr(neighbourGear, self, parrallel=True)

        if self.isParrallel(neighbourGear):
            return
        delta = neighbourGear.translate[1] - self.translate[1]
        if delta > 0:
            orientation = 1
        else:
            orientation = -1
        if orientation == 1:
            pm.rotate(self.objTransform, [0, 0, -90], os=True, r=True)
            pm.move(
                self.objTransform,
                [
                    - 1 * (self.gear.radius - neighbourGear.gear.gearOffset),
                    1 * (self.gear.radius + neighbourGear.gear.height / 2),
                    0
                ],
                os=True, r=True, wd=True)
        # TODO: !!! DOES SHIFT CHILDREN GEARS BY 90°
        elif orientation == -1:
            self.lockChain(neighbourGear, lock=False)
            self.flipPartOfChain180(neighbourGear, negative=True)
            self.lockChain(neighbourGear, lock=True)
            pm.rotate(self.objTransform, [0, 0, 90], os=True, r=True)
            pm.move(
                self.objTransform,
                [
                    - 1 * (self.gear.radius - neighbourGear.gear.gearOffset),
                    - 1 * (self.gear.radius + neighbourGear.gear.height / 2),
                    0
                ],
                os=True, r=True, wd=True)

    def isParrallel(self, neighbourGear):

        x1, _, z1 = neighbourGear.rotate
        x2, _, z2 = self.rotate

        if int(x1 - x2) // 180 == 0 and int(z1 - z2) // 180 == 0:
            return True
        else:
            return False

    # GEAR CHAIN RELATION MANAGER TAG -> "X" ou "Z" ET PIS VOILA.

    def isParrallelToGnd(self):

        #  THIS IS NO SENSE...

        if self.translate[2] // 180 == 0:
            return True
        else:
            return False

    @transform
    def setParrallel(self, neighbourGear):
        self._setParrallel(neighbourGear)

    # CONSTRAINTS -------------------------------------------------------------

    @transform
    def initCircleConstraint(self, neighbourGear):
        # axis is X-Y TODO: to update when multiple orientation implemented
        objTransform, objConstructor = pm.circle(
            radius=GearAbstract.calculateConstraintRadius(self, neighbourGear),
            nr=(0, 1, 0))
        c = mob.MayaObjDescriptor(objTransform)
        c.addInput(objConstructor, "circle")
        c.visibility = False
        self.addConstraintCircle(neighbourGear, c)
        pm.parentConstraint(neighbourGear.objTransform,
                            c.objTransform)

    @transform
    def activateCircleConstraint(self, neighbourGear):
        constraintsCircle = self.getRelatedConstraintCircle(neighbourGear)
        self.circleConstraints = [
            pm.geometryConstraint(
                constraintsCircle.objTransform,
                self.objTransform),
            pm.aimConstraint(
                neighbourGear.objTransform,
                self.objTransform,
                wut="objectrotation",
                wuo=neighbourGear.objTransform)
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

    def orienGear(self, neighbourGear):
        constraint = pm.aimConstraint(
            neighbourGear.objTransform,
            self.objTransform,
            wut="objectrotation",
            wuo=neighbourGear.objTransform)
        pm.delete(constraint)

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

    # MISC --------------------------------------------------------------------

    def flipPartOfChain180(self, rootObj, negative=False):
        if negative:
            factor = -1
        else:
            factor = 1
        pm.rotate(self.objTransform, [factor * 180, 0, 0], os=True, r=True)
        gears, r = self._find_children(rootObj)
        self._flipPartOfChain180_recc(factor, *gears, rod=r)

    def _flipPartOfChain180_recc(self, factor, *neighboursGear, rod=None):
        allObj = list(neighboursGear)
        if rod:
            allObj.append(rod)
        for obj in allObj:
            obj.lockTransform(False)
            pm.rotate(obj.objTransform, [factor * 180, 0, 0], os=True, r=True)
            obj.lockTransform(True)
        for g in neighboursGear:
            new_gears, new_rod = g._find_children(self)
            g._flipPartOfChain180_recc(factor, *new_gears, rod=new_rod)
        if rod:
            rod._flipPartOfChain180_recc(self, factor)
