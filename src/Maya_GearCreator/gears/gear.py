import math
import pymel.core as pm
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def transform(f):
    def wrapper(*args, **kargs):
        args[0].lockTransform(False)
        ret = f(*args, **kargs)
        args[0].lockTransform(True)
        return ret
    return wrapper


class Gear():

    DEFAULT_PREFIX = "gear"
    DEFAULT_RADIUS = 1
    DEFAULT_TLEN = 0.3

    gearIdx = 0

    def __init__(
            self,
            name=None,
            radius=1,
            tWidth=0.3,
            tLen=0.3,
            linkedGear=None,
            gearChain=None):

        name = name or self.genAutoName()

        self.shader_bk = None
        adjustedRadius = radius - tLen
        self.neighbours = []
        if linkedGear:
            self.neighbours.append(linkedGear)
            linkedGear.neighbours.append(self)

        self.tLen = tLen
        tNumber = Gear.calculateTNumber(tWidth, adjustedRadius)
        spans, sideFaces = Gear.getTeethInfo(tNumber)

        self.gearTransform, self.gearConstructor = pm.polyPipe(
            sa=spans,
            r=adjustedRadius,
            n=name)

        self.name = name

        extrudeArg = []
        for face in sideFaces:
            extrudeArg.append("{}.f[{}]".format(self.gearTransform, face))
        self.teethExtrude = pm.polyExtrudeFacet(*extrudeArg,
                                                localTranslateZ=self.tLen)[0]

        self.constraintsCircles = {}
        if linkedGear:
            self.initCircleConstraint(linkedGear)
            self.adjustGearToCircleConstraint(linkedGear)
            linkedGear.initCircleConstraint(self)

        self.gearChain = gearChain
        self.tWidth = tWidth
        self.circleConstraints = []
        self.parentConstraints = []

        self.lockTransform(True)

    # HANDLING NAME -----------------------------------------------------------

    def genAutoName(cls):
        name = "{}{}".format(cls.DEFAULT_PREFIX, cls.gearIdx)
        cls.gearIdx += 1
        return name

    @property
    def name(self):
        return str(self.gearTransform)

    @name.setter
    def name(self, name):
        pm.rename(self.name, name)

    # Redondant but used as signal callback for UI
    def setName(self, name):
        self.name = name

    # teeth width properties --------------------------------------------------

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

    # CALCULUS ----------------------------------------------------------------

    def calculateTNumber(tWidth, radius):
        tNumber = int(radius * math.pi / tWidth)
        return tNumber

    def getTeethInfo(tNumber):
        # teeth are every alternate face, so spans*2
        spans = tNumber * 2
        # pipe structure:
        # [0, subNumber]               : inside
        # [subNumber, 2x subNumber]    : top
        # [2x subNumber, 3x subNumber] : side face
        # [3x subNumber, 4x subNumber] : back face
        sideFaces = range(spans * 2, spans * 3, 2)
        return spans, sideFaces

    def calculateConstraintRadius(parentGear, childGear):
        return parentGear.gearConstructor.radius.get() \
            + (parentGear.tLen / 2) \
            + childGear.gearConstructor.radius.get() \
            + (childGear.tLen / 2)

    def calculateAdjustedRadius(self, radius):
        radius = radius or self.gearConstructor.radius.get()
        return radius - self.tLen

    # MODIFY ------------------------------------------------------------------

    def lockTransform(self, lock=True):
        for transform in ("translate", "rotate", "scale"):
            pm.setAttr(self.name + "." + transform, lock=lock)

    # TODO : Split in two?
    def changeTeeth(self, tNumber=None, tLen=None):

        minTeethNumber = 4
        minRadius = 0.01

        if not tNumber and not tLen : return 

        log_str = "changing gear {} : ".format(self.gearConstructor)
        if tNumber : log_str = "{} teeth number: {},".format(log_str, tNumber)
        if tLen    : log_str = "{} teeth lenght: {},".format(log_str, tLen)
        log.info(log_str[:-1] + ".")

        status = True
        if tNumber:

            if tNumber < minTeethNumber:
                log.error("minimal teeth number is {}, input is {}.".format(
                    minTeethNumber, tNumber))
                status = False

            spans, sideFaces = Gear.getTeethInfo(tNumber)
            pm.polyPipe(self.gearConstructor, edit=True, 
                        subdivisionsAxis=spans)
            faceNames = ["f[{}]".format(face) for face in sideFaces]
            pm.setAttr("{}.inputComponents".format(self.teethExtrude),
                len(faceNames),
                *faceNames,
                type="componentList")
        if tLen:
            adjustedRadius = self.calculateAdjustedRadius()
            if adjustedRadius < 0.01:
                log.error("teeth length {} is too high for current gear radius {}".format(
                    tLen, self.gearConstructor.radius.get()))
                status = False

            self.gearConstructor.radius.set(adjustedRadius)
            pm.polyExtrudeFacet(self.teethExtrude, edit=True, ltz=tLen)
        return True

    def changeTWidth(self, tWidth):
        tNumber = Gear.calculateTNumber(tWidth,
                                        self.gearConstructor.radius.get())
        self.changeTeeth(tNumber=tNumber)

    def changeRadius(self, radius, resizeNeighbour=False):
        adjustedRadius = self.calculateAdjustedRadius(radius)
        self.gearConstructor.radius.set(adjustedRadius)
        tNumber = Gear.calculateTNumber(self.tWidth, adjustedRadius)
        self.changeTeeth(tNumber=tNumber)

        # TODO : bugged!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Does not work with negative values (reducing radius)
        # shall calculate max value and refuse transformation if exceded
        if resizeNeighbour:
            delta = radius - self.gearConstructor.radius.get()
            for neighbour in self.neighbours:
                neighbourRadius = neighbour.gearConstructor.radius.get() - delta
                neighbour.changeRadius(neighbourRadius, resizeNeighbour=False)
        # TODO : bugged!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Lock CHAIN DOES NOT WORK..................................................................
        else:
            for neighbour in self.neighbours:
                toLock = [n for n in neighbour.neighbours if n != self]
                neighbour.lockChain(*toLock, lock=True)
                circleRadius = Gear.calculateConstraintRadius(self, neighbour)
                circle = neighbour.constraintsCircles[self][1]
                circle.radius.set(circleRadius)
                circle = self.constraintsCircles[neighbour][1]
                circle.radius.set(circleRadius)
                neighbour.adjustGearToCircleConstraint(self)
                neighbour.lockChain(*toLock, lock=False)

    def activateMoveMode(self, rootGear):
        # 1 define constraint to move along root gear
        self.moveMode = rootGear
        self.activateCircleConstraint(rootGear)
        # 2 lock the rest of the chain.
        self.lockChain(*[g for g in self.neighbours if g != rootGear])
        pm.setAttr(self.name + ".translate", lock=False)

        # 3 TODO: SHOW / HIDE CONSTRAINT CIRCLE.

    def desactivateMoveMode(self):
        if not self.moveMode: return
        self.desactivateCircleConstraint(self.moveMode)
        self.lockChain(*[g for g in self.neighbours if g != self], lock=False)
        self.lockTransform()

    def calculateMoveAlong(self):
        radius = self.gearConstructor.radius.get() + self.tLen / 2
        perimeter = 2 * math.pi * radius
        return perimeter
        # calculate radius + Tlen / 2 -> perimeter: max distance

    def moveAlong(self, distance):
        pm.move(self.gearTransform, [0, 0, distance], os=True, r=True, wd=True)
        pass

    # CONSTRAINTS -------------------------------------------------------------

    @transform
    def initCircleConstraint(self, neighbourGear):
        circle = pm.circle(
            nr=(0, 1, 0),  # axis is X-Y
            radius=Gear.calculateConstraintRadius(self, neighbourGear))
        pm.move(circle[0],
                neighbourGear.gearTransform.getTransform().translate.get())
        circle[0].visibility.set(False)
        self.constraintsCircles[neighbourGear] = circle
        pm.parentConstraint(neighbourGear.gearTransform, circle[0])

    @transform
    def activateCircleConstraint(self, neighbourGear):
        self.circleConstraints = [
            pm.geometryConstraint(self.constraintsCircles[neighbourGear],
                                  self.gearTransform),
            pm.aimConstraint(neighbourGear.gearTransform, self.gearTransform)
        ]

    def desactivateCircleConstraint(self, neighbourGear):
        for constraint in self.circleConstraints:
            pm.delete(constraint)
        self.circleConstraints = []

    def adjustGearToCircleConstraint(self, neighbourGear):
        self.activateCircleConstraint(neighbourGear)
        self.desactivateCircleConstraint(neighbourGear)

    def activateParentConstraint(self, *gears):
        for gear in gears:
            self.parentConstraints.append(
                pm.parentConstraint(self.gearTransform, gear.gearTransform,
                                    maintainOffset=True))

    def desactivateParentConstraint(self, *gears):
        for constraint in self.parentConstraints:
            pm.delete(constraint)
        self.parentConstraints = []

    def lockChain(self, *neighboursGear, lock=True):
        func = {
            True: Gear.activateParentConstraint,
            False: Gear.desactivateParentConstraint
        }
        for g in neighboursGear: g.lockTransform(not lock)
        func[lock](self, *neighboursGear)
        for gear in neighboursGear:
            newNeighboursGear= [g for g in gear.neighbours if g != self]
            if newNeighboursGear:
                gear.lockChain(*newNeighboursGear, lock=lock)
            else:
                gear.lockChain(*newNeighboursGear, lock=lock)

    def setTmpShader(self, sg):
        self.shader_bk = self._getCurrentShader()
        self._setShader(sg)
        pass

    def restorShader(self):
        if self.shader_bk:
            for s in self.shader_bk:
                pm.sets(s, forceElement=self.gearTransform)

    def _setShader(self, sg):
        pm.sets(sg, forceElement=self.gearTransform)

    def _getCurrentShader(self):
        shadeEng = pm.listConnections(self.gearTransform.getShape(),
                                      type="shadingEngine")
        return shadeEng
