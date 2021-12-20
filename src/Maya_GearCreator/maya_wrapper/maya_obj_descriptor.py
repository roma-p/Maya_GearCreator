import logging
import importlib
import pymel.core as pm

from Maya_GearCreator import consts
from Maya_GearCreator.maya_wrapper import children_manager as childrenM
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
            objTransform=None,
            name=None,
            objExists=False,
            _class=None,
            group=False,
            parentTransform=None):

        self.objTransform = objTransform
        self.parentConstraints = []

        # if descriptor is a group which does not exist: we create it.
        # name = name or str(objTransform) or self.genAutoName()

        if group and not objExists:
            name = name or self.genAutoName()
            self.objTransform = maya_helpers.createGroup(
                name,
                parentTransform)

        for attrName in MayaObjDescriptor.TRANSFORM_PRP_WHITE_LIST:
            self._addTransformProperty(attrName, _class)

        if objExists and not group:
            self.parseInput()

        if parentTransform and not objExists:
            pm.parent(self.objTransform, parentTransform)

    def _addTransformProperty(self, attrName, _class=None):
        _class = _class or MayaObjDescriptor
        if hasattr(_class, attrName):
            return

        def getter(self):
            return self.objTransform.getAttr(attrName)

        def setter(self, value):
            self.objTransform.setAttr(attrName, value)
        setattr(_class, attrName, property(getter, setter))

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

    def createChildrenM(self, tag):
        return childrenM.ChildrenManager(self.objTransform, tag)

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

    # ADD REFS SET ------------------------------------------------------------
    def addNodeRefHandler(self, refTag):
        return RefHandler(self, refTag)

    # ADD ATTRIBUTE -----------------------------------------------------------

    def addAttribute(self, name, type, defaultValue, _class=None):
        objTransform = self.objTransform
        if not objTransform.hasAttr(name):
            objTransform.addAttr(
                name,
                attributeType=type,
                hidden=True,
                keyable=True)
        self._addTransformProperty(name, _class=_class)
        setattr(self, name, defaultValue)

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

class RefHandler():

    def __init__(self, parentObj, name):
        self.name = name
        self.parentObj = parentObj
        self.transformToDescr = {}
        maya_helpers.addTag(parentObj.objTransform, name)

    def __len__(self):
        return len(self._listRefs())

    def __contains__(self, obj):
        return obj in self._listRefs()

    def __iter__(self):
        for item in self._listRefs():
            yield item

    def add(self, obj):
        maya_helpers.addTag(obj.objTransform, self.name)
        pm.connectAttr(self._formatConnection(self.parentObj),
                       self._formatConnection(obj))
        self.transformToDescr[obj.objTransform] = obj

    def discard(self, obj):
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print("alors?")
        print(self._listRefs())
        print(obj)
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        if obj in self._listRefs():
            print("bah oui?")
            pm.disconnectAttr(self._formatConnection(self.parentObj),
                              self._formatConnection(obj))
            self.transformToDescr.pop(obj.objTransform)

    def _listRefs(self):
        connectedTransform = pm.listConnections(
            self._formatConnection(self.parentObj),
            source=False)
        print('yyyyyyyyyyyyyyyyyyyyyyyy')
        print(connectedTransform)
        print('yyyyyyyyyyyyyyyyyyyyyyyy')
        return [self.transformToDescr[c] for c in connectedTransform]

    def _formatConnection(self, objDescriptor):
        return "{}.{}".format(str(objDescriptor.objTransform),
                              self.name)
