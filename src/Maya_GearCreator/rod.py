import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor as mob
from Maya_GearCreator import consts

importlib.reload(mob)
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
            gearNetwork=None,
            rodExists=False,
            rodData=None):

        if rodExists:
            rod_transform, rode_construct = rodData
        else:
            rod_transform, rode_construct = pm.polyCylinder()

        super(Rod, self).__init__(rod_transform, rode_construct, Rod, name)

        self.radius = radius
        self.height = height

        if linkedGear:
            self.translate = linkedGear.translate
        if gearNetwork:
            self.gearNetwork = gearNetwork

        #lock transform.

    def moveTop(self): pass

    def moveBot(self): pass

    def _lockChain_recc(self, rootGear, lock=True):
        func = {
            True: mob.MayaObjDescriptor.activateParentConstraint,
            False: mob.MayaObjDescriptor.desactivateParentConstraint
        }
        gears = [g for g in self.gearNetwork.getGearsFromRod(self)
                if g != rootGear]
        for g in gears:
            g.lockTransform(not lock)
            func[lock](self, *gears)
        for g in gears:
            new_gears, new_rod = g._find_children(self)
            g._lockChain_recc(*new_gears, lock=lock, rod=new_rod)
