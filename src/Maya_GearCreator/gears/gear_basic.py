import math
import logging
import collections
import pymel.core as pm
import importlib

from Maya_GearCreator.gears import gear_abstract
from Maya_GearCreator import consts

importlib.reload(gear_abstract)
importlib.reload(consts)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GearBasic(gear_abstract.GearAbstract):

    def __init__(
            self, name=None,
            radius=consts.DEFAULT_RADIUS,
            tWidth=consts.DEFAULT_TWIDTH,
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None,
            gearChain=None):

        gear_shape, gear_construct = GearBasic.instantiateGear()

        super(GearBasic, self).__init__(
            gear_shape, gear_construct,
            name, radius, 
            tWidth, gearOffset, 
            linkedGear, gearChain)

    def changeRadius(self, radius, resizeNeighbour=False):
        adjustedRadius = self.calculateAdjustedRadius(radius)
        self.radius = adjustedRadius
        self.sides = GearBasic.calculateTNumber(self.tWidth, adjustedRadius)

        if resizeNeighbour: 
            pass 
            # TODO : NOT IMPLEMENTED.
        else: 
            for neighbour in self.listNeigbours():
                toLock = [n for n in neighbour.listNeigbours() if n!= self]
                neighbour.lockChain(*toLock, lock=True)
                new_radius = GearBasic.calculateConstraintRadius(
                    self,neighbour)
                neighbour.constraintsCircles[self].radius = new_radius
                self.constraintsCircles[neighbour].radius = new_radius
                neighbour.adjustGearToCircleConstraint(self)
                neighbour.lockChain(*toLock, lock=False)
