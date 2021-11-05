import math
import logging
import collections
import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor
from Maya_GearCreator.misc import connections_manager
from Maya_GearCreator.misc import circle_descriptor
from Maya_GearCreator import gear_chain
from Maya_GearCreator import consts

importlib.reload(maya_obj_descriptor)
importlib.reload(connections_manager)
importlib.reload(circle_descriptor)
importlib.reload(gear_chain)
importlib.reload(consts)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def transform(f):
    def wrapper(*args, **kargs):
        args[0].lockTransform(False)
        ret = f(*args, **kargs)
        args[0].lockTransform(True)
        return ret
    return wrapper

class GearAbstract(maya_obj_descriptor.MayaObjDescriptor):

    gearIdx = 0
    DEFAULT_PREFIX = "gear"
    connectManager = connections_manager.ConnectionsManager("neighbour")

    def __init__(
            self, 
            gear_shape, 
            gear_construct,
            name=None,
            radius=consts.DEFAULT_RADIUS,
            tWidth=consts.DEFAULT_TWIDTH,
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None,
            gearChain=None):

        super(GearAbstract, self).__init__(
            gear_shape,
            gear_construct,
            GearAbstract,
            name)

        self.shader_bk = None
        
        # ADJUSTING SHAPE -----------------------------------------------------
        self.radius = radius - gearOffset
        self.gearOffset = gearOffset
        self.sides = GearAbstract.calculateTNumber(tWidth, self.radius)

        # HANDLNING NEIGHBOURS ------------------------------------------------
        self.constraintsCircles = {}
        self.circleConstraints = []
        self.parentConstraints = []

        if linkedGear:
            self.addNeighbour(linkedGear)
            self.adjustGearToCircleConstraint(linkedGear)

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
            +  childGear.radius + (childGear.gearOffset / 2)

    def calculateAdjustedRadius(self, radius):
        radius = radius or self.radius
        return radius - self.gearOffset

    def calculateTNumber(tWidth, radius):
        tNumber = int(radius * math.pi / tWidth)
        return tNumber

    # MANAGE NEIGHBOURS -------------------------------------------------------
    def listNeigbours(self): 
        return GearAbstract.connectManager.listConnections(self)

    def hasConnection(self):
        return GearAbstract.connectManager.hasConnection(self)

    # TODO : del circles. 
    def delNeighbour(self, gear):
        GearAbstract.connectManager.disconnect(self, gear)
    
    def addNeighbour(self, gear): 
        GearAbstract.connectManager.connect(self, gear)
        self.initCircleConstraint(gear)
        gear.initCircleConstraint(self)

    # MODIFY ------------------------------------------------------------------

    def lockTransform(self, lock=True):
        for transform in ("translate", "rotate", "scale"):
            pm.setAttr(self.name + "." + transform, lock=lock)

    def changeTWidth(self, tWidth):
        self.sides = GearAbstract.calculateTNumber(tWidth, self.radius)

    def changeRadius(self, radius):
        raise NotImplementedError()


    def activateMoveMode(self, rootGear):
        # 1 define constraint to move along root gear
        self.moveMode = rootGear
        self.activateCircleConstraint(rootGear)
        # 2 lock the rest of the chain.
        self.lockChain(*[g for g in self.listNeigbours() if g != rootGear])
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
        self.lockChain(*[g for g in self.listNeigbours() if g != self],
                       lock=False)
        self.lockTransform()

    def calculateMoveAlong(self):
        radius = self.radius + self.gearOffset / 2
        perimeter = 2 * math.pi * radius
        return perimeter
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

    # CONSTRAINTS -------------------------------------------------------------

    @transform
    def initCircleConstraint(self, neighbourGear):
        circle = circle_descriptor.CircleDescriptor(
            nr=(0,1,0), # axis is X-Y TODO: to update when multiple orientation implemented.
            radius=GearAbstract.calculateConstraintRadius(self, neighbourGear))
        pm.move(circle.objTransform, neighbourGear.translate)
        circle.visibility = False
        self.constraintsCircles[neighbourGear] = circle
        pm.parent(circle.objTransform, self.name)
        pm.parentConstraint(neighbourGear.objTransform, 
                            circle.objTransform)

    @transform
    def activateCircleConstraint(self, neighbourGear):
        self.circleConstraints = [
            pm.geometryConstraint(
                self.constraintsCircles[neighbourGear].objTransform,
                self.objTransform),
            pm.aimConstraint(neighbourGear.objTransform, self.objTransform)
        ]
        self.constraintsCircles[neighbourGear].visibility = True

    def desactivateCircleConstraint(self, neighbourGear):
        self.constraintsCircles[neighbourGear].visibility = False
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

    def lockChain(self, *neighboursGear, lock=True):
        func = {
            True: GearAbstract.activateParentConstraint,
            False: GearAbstract.desactivateParentConstraint
        }
        for g in neighboursGear: g.lockTransform(not lock)
        func[lock](self, *neighboursGear)
        for gear in neighboursGear:
            newNeighboursGear= [g for g in gear.listNeigbours() if g != self]
            if newNeighboursGear:
                gear.lockChain(*newNeighboursGear, lock=lock)
#            else:
#                gear.lockChain(*newNeighboursGear, lock=lock)

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