import logging
import importlib

from Maya_GearCreator.gears import gear_abstract
from Maya_GearCreator import consts

importlib.reload(gear_abstract)
importlib.reload(consts)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GearBasic(gear_abstract.GearAbstract):

    # TODO : IHM DESCRIPTOR OBJECT
    # categorie -> type of button (check / slider / button)
    # -> min / max / step / max of other input (if none: max)

    GUI_ATTRIBUTES = {
        "base": {
            # "internalRadius": (0, 5, 0.1, 15), <- TODO : shall call changeInternalRadius rather than directly access property.
            "height": (0, 5, 0.1, 15),
            "heightDivisions": (1, 10, 1, None)
        },
        "teeth": {
            "gearSpacing": (0, 1, 0.01, None),
            "gearOffset": (0, 1, 0.05, None),  #  <- to change ! shall update radius!!
            "gearTip": (0, 1, 0.05, None),
            "gearMiddle": (0, 1, 0.05, None)
        }
    }

    def __init__(
            self, name=None,
            radius=consts.DEFAULT_RADIUS,
            tWidth=consts.DEFAULT_TWIDTH,
            gearOffset=consts.DEFAULT_GEAR_OFFSET,
            linkedGear=None,
            gearChain=None,
            linkedRod=None,
            gearExists=False,
            gearTransform=None):

        if not gearExists:
            gearTransform, gearConstruct = GearBasic.instantiateGear()
        else:
            gearConstruct = None

        super().__init__(
            gearTransform, gearConstruct,
            name, radius,
            tWidth, gearOffset,
            linkedGear, gearChain,
            linkedRod,
            _class=GearBasic,
            objExists=gearExists)

    def changeRadius(self, radius, resizeNeighbour=False):

        delta = radius - self.gear.radius
        adjustedRadius = self.calculateAdjustedRadius(radius)
        self._changeRadius_basic(adjustedRadius)

        if resizeNeighbour:
            for neighbour in self.listNeigbours():
                neighbour._changeRadius_basic(neighbour.gear.radius - delta)
                self._adjustConstraintCircles(neighbour)

        else:
            move_self = len(self.listNeigbours()) == 1

            for neighbour in self.listNeigbours():

                if move_self:
                    arg = (self, neighbour)
                else:
                    arg = (neighbour, self)

                arg[0].lockChain(rootObj=arg[1], lock=True)

                self._adjustConstraintCircles(neighbour)

                # if only one neighbour, more handy to move current gear.
                # if multiple neighbours, not possible.
                if move_self:
                    self.adjustGearToCircleConstraint(neighbour)
                else:
                    neighbour.adjustGearToCircleConstraint(self)
                arg[0].lockChain(rootObj=arg[1], lock=False)
                # neighbour.lockChain(rootObj=self, lock=False)

    def getInternalRadius(self):
        return self.gear.internalRadius

    def changeInternalRadius(self, radius):
        self.gear.internalRadius = radius
