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
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None,
            gearChain=None,
            linkedRod=None,
            gearExists=False,
            gearData=None):

        if gearExists:
            gear_transform, gear_construct = gearData
        else:
            gear_transform, gear_construct = GearBasic.instantiateGear()

        super().__init__(
            gear_transform, gear_construct,
            name, radius,
            tWidth, gearOffset,
            linkedGear, gearChain,
            linkedRod,
            _class=GearBasic)

    def changeRadius(self, radius, resizeNeighbour=False):
        adjustedRadius = self.calculateAdjustedRadius(radius)
        self.radius = adjustedRadius
        self.sides = GearBasic.calculateTNumber(self.tWidth, adjustedRadius)

        if resizeNeighbour:
            pass
            # TODO : NOT IMPLEMENTED.
        else:
            move_self = len(self.listNeigbours()) == 1

            for neighbour in self.listNeigbours():

                if move_self:
                    arg = (self, neighbour)
                else:
                    arg = (neighbour, self)

                arg[0].lockChain(rootObj=arg[1], lock=True)

                # neighbour.lockChain(rootObj=self, lock=True)
                new_radius = GearBasic.calculateConstraintRadius(
                    self, neighbour)

                neighbour.getRelatedConstraintCircle(self).radius = new_radius
                self.getRelatedConstraintCircle(neighbour).radius = new_radius

                # if only one neighbour, more handy to move current gear.
                # if multiple neighbours, not possible.
                if move_self:
                    self.adjustGearToCircleConstraint(neighbour)
                else:
                    neighbour.adjustGearToCircleConstraint(self)
                arg[0].lockChain(rootObj=arg[1], lock=False)
                # neighbour.lockChain(rootObj=self, lock=False)
