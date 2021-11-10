import logging
import importlib
import pymel.core as pm


from Maya_GearCreator.misc import helpers
from Maya_GearCreator.misc import children_manager as childrenM

importlib.reload(helpers)
importlib.reload(childrenM)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class MayaGrpDescriptor():

    DEFAULT_PREFIX = "group"
    groupIdx = 0

    def __init__(self, name=None, parentObj=None):

        name = name or self.genAutoName()
        self.group = helpers.createGroup(name, parentObj)
        self.name = name

    def createGrpChildrenM(self, tag):
        return childrenM.ChildrenManager_GrpDescriptor(self.group, tag)

    def createObjChildrenM(self, tag):
        return childrenM.ChildrenManager_ObjDescriptor(self.group, tag)

    # HANDLING NAME -----------------------------------------------------------

    def genAutoName(cls):
        name = "{}{}".format(cls.DEFAULT_PREFIX, cls.groupIdx)
        cls.groupIdx += 1
        return name

    # Redondant but used as signal callback for UI
    def setName(self, name):
        self.name = name

    @property
    def name(self):
        return str(self.group)

    @name.setter
    def name(self, name):
        pm.rename(self.group, name)
