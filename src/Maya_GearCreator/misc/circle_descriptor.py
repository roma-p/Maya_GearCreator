import logging
import pymel.core as pm
import importlib

from Maya_GearCreator.maya_wrapper import maya_obj_descriptor as mob
importlib.reload(mob)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class CircleDescriptor(mob.MayaObjDescriptor):

    DEFAULT_PREFIX = "circle"
    gearIdx = 0

    def __init__(
            self,
            nr=None,
            radius=None,
            objExists=False,
            objTransform=None):

        if not objExists:
            objTransform, objConstructor = pm.circle(radius=radius, nr=nr)
        super(CircleDescriptor, self).__init__(objTransform,
                                               objExists=objExists)
        if not objExists:
            self.addInput(objConstructor, "circle")
