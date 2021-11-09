import logging
import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor
importlib.reload(maya_obj_descriptor)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class CircleDescriptor(maya_obj_descriptor.MayaObjDescriptor):

    DEFAULT_PREFIX = "circle"
    gearIdx = 0

    def __init__(self, nr, radius):

        circle_shape, circle_construct = pm.circle(radius=radius, nr=nr)
        super(CircleDescriptor, self).__init__(
            circle_shape,
            circle_construct,
            CircleDescriptor)
