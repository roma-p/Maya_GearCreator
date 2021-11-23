import logging
import collections
import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_helpers

importlib.reload(maya_helpers)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ChildrenManager(collections.MutableSet):

    def __init__(self, parentObj, tag):
        self.childrenManger = ChildrenManagerTransform(parentObj, tag)
        self.transformToDescr = {}

    def __len__(self):
        return len(self.childrenManger)

    def __contains__(self, gearChain):
        return gearChain in self._list_children()

    def __iter__(self):
        for item in (
                self.transformToDescr[obj] for obj in self.childrenManger
                if obj in self.transformToDescr):
            yield item

    def add(self, objDescriptor):
        self.childrenManger.add(objDescriptor.objTransform)
        self.transformToDescr[objDescriptor.objTransform] = objDescriptor

    def discard(self, objDescriptor):
        if objDescriptor in self._list_children():
            self.childrenManger.discard(objDescriptor.objTransform)
            self.transformToDescr.pop(objDescriptor.objTransform)

    def _list_children(self):
        return [self.transformToDescr[obj] for obj in self.childrenManger
                if obj in self.transformToDescr]

    def getDescriptor(self, constructor):
        if constructor in self.transformToDescr:
            return self.transformToDescr[constructor]

    def parse(self, *objDescriptors):
        for objDescr in objDescriptors:
            if objDescr.objTransform in self.childrenManger:
                self.transformToDescr[objDescr.objTransform] = objDescr


class ChildrenManagerTransform(collections.MutableSet):

    def __init__(self, parentObj, childrenTag):
        self.parentObj = parentObj
        self.childrenTag = childrenTag

    def __len__(self):
        return len(self._listChildren())

    def __contains__(self, obj):
        return obj in self._listChildren()

    def __iter__(self):
        for item in (
                obj for obj in pm.listRelatives(self.parentObj, c=True)
                if self._isChildrenTransform(obj)):
            yield item

    def add(self, obj):

        maya_helpers.addTag(obj, self.childrenTag)
        pm.parent(obj, self.parentObj)

    def discard(self, obj):
        if obj in self:
            maya_helpers.delTag(self.childrenTag)
            pm.parent(obj, world=True)

    # PRIVATE -----------------------------------------------------------------

    def _listChildren(self):
        return [
            obj for obj in pm.listRelatives(self.parentObj, c=True)
            if self._isChildrenTransform(obj)]

    def _isChildrenTransform(self, obj):
        return (obj.hasAttr(self.childrenTag))
