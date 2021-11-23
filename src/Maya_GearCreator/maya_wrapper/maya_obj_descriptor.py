import logging
import importlib
import pymel.core as pm

from Maya_GearCreator import consts
from Maya_GearCreator.misc import children_manager as childrenM
from Maya_GearCreator.misc import maya_helpers

importlib.reload(childrenM)
importlib.reload(maya_helpers)
importlib.reload(consts)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class MayaObjDescriptor():

    DEFAULT_PREFIX = "obj"
    gearIdx = 0

    TRANSFORM_PRP_WHITE_LIST = [
        'translate',
        'rotate',
        'scale',
        'visibility'
    ]

    inputDescriptorClass = {}

    def __init__(
            self,
            objTransform,
            name=None,
            objExists=False):

        self.objTransform = objTransform
        self.name = name or str(objTransform)
        self.parentConstraints = []

        for attrName in MayaObjDescriptor.TRANSFORM_PRP_WHITE_LIST:
            self._addTransformProperty(attrName)

        if objExists:
            self.parseInput()

    def _addTransformProperty(self, attrName):
        if hasattr(MayaObjDescriptor, attrName):
            return

        def getter(self):
            return self.objTransform.getAttr(attrName)

        def setter(self, value):
            self.objTransform.setAttr(attrName, value)
        setattr(MayaObjDescriptor, attrName, property(getter, setter))

    # HANDLING NAME -----------------------------------------------------------

    def genAutoName(cls):
        name = "{}{}".format(cls.DEFAULT_PREFIX, cls.gearIdx)
        cls.gearIdx += 1
        return name

    @property
    def name(self):
        return str(self.objTransform)

    @name.setter
    def name(self, name):
        pm.rename(self.objTransform, name)

    # Redondant but used as signal callback for UI
    # TODO ; but redundant avec setAttr?
    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    # CHILDREN MANAGEMENT------------------------------------------------------

    # TODO : TO MERGE INTO ONE.

    def createGrpChildrenM(self, tag):
        return childrenM.ChildrenManager_GrpDescriptor(self.objTransform, tag)

    def createObjChildrenM(self, tag):
        return childrenM.ChildrenManager_ObjDescriptor(self.objTransform, tag)

    # MODIFY ------------------------------------------------------------------

    def lockTransform(self, lock=True):
        for transform in ("translate", "rotate", "scale"):
            pm.setAttr(self.name + "." + transform, lock=lock)

    # CONSTRAINT --------------------------------------------------------------

    def activateParentConstraint(self, *gears):
        for gear in gears:
            self.parentConstraints.append(
                pm.parentConstraint(self.objTransform, gear.objTransform,
                                    maintainOffset=True))

    def desactivateParentConstraint(self, *gears):
        for constraint in self.parentConstraints:
            pm.delete(constraint)
        self.parentConstraints = []

    # ADD INPUT ---------------------------------------------------------------

    def addInput(self, inputNode, inputName):
        _class = MayaObjDescriptor.getInputDescriptorClass(inputNode)
        setattr(self, inputName, _class(inputName, inputNode))

    def getInputDescriptorClass(inputNode):
        key = type(inputNode)
        if key in MayaObjDescriptor.inputDescriptorClass:
            return MayaObjDescriptor.inputDescriptorClass[key]
        else:
            class TMP(InputDescriptor):
                def __init__(self, name, inputNode):
                    super(TMP, self).__init__(name, inputNode, TMP)
            MayaObjDescriptor.inputDescriptorClass[key] = TMP
            return TMP

    def parseInput(self):
        for inputNode in self.objTransform.getShape().inputs():
            attrList = inputNode.listAttr(ct=consts.TAG_CATEGORY)
            if attrList:
                attrName = attrList[0].attrName()
                self.addInput(inputNode, attrName)

class InputDescriptor():

    INPUT_PRP_BLACK_LIST = [
        'message',
        'caching',
        'frozen',
        'isHistoricallyInteresting',
        'nodeState',
        'binMembership',
        'output'
    ]

    def __init__(self, name, inputNode, _class):
        self.inputNode = inputNode
        maya_helpers.addTag(
            self.inputNode,
            tagName=name,
            category=consts.TAG_CATEGORY)

        for attrName in pm.listAttr(self.inputNode):
            if attrName not in InputDescriptor.INPUT_PRP_BLACK_LIST:
                self.addProperty(attrName, _class)

    def addProperty(self, attrName, _class):
        if hasattr(_class, attrName):
            return

        def getter(self):
            return self.inputNode.getAttr(attrName)

        def setter(self, value):
            self.inputNode.setAttr(attrName, value)
        setattr(_class, attrName, property(getter, setter))
