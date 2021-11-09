import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor
from Maya_GearCreator import consts

importlib.reload(maya_obj_descriptor)
importlib.reload(consts)


# TODO : CHANGING INTERNAL RADIUS of a gear ->
# if not rod -> just change raidus
# otherwise changing the radius of the rod
# rod -> change radius of all linked gears.

class Rod(maya_obj_descriptor.MayaObjDescriptor):

    rodIdx = 0
    DEFAULT_PREFIX = "rod"

    def __init__(
            self, name=None,
            radius=consts.DEFAULT_ROD_RADIUS,
            height=consts.DEFAULT_ROD_LEN,
            linkedGear=None,
            gearNetwork=None):

        rod_shape, rode_construct = pm.polyCylinder()

        super(Rod, self).__init__(rod_shape, rode_construct, Rod, name)

        self.radius = radius
        self.height = height

        if linkedGear: self.translate = linkedGear.translate
        if gearNetwork: self.gearNetwork = gearNetwork

        #lock transform.

    def moveTop(self): pass

    def moveBot(self): pass
