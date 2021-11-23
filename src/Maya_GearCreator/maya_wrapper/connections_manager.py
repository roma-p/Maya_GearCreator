import logging
import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor
from Maya_GearCreator.misc import maya_helpers


importlib.reload(maya_obj_descriptor)
importlib.reload(maya_helpers)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ConnectionsManager():

    def __init__(self, connection_name):
        self.const2Descriptor = {}
        self.connection_name = connection_name

    def connect(self, objDescriptorA, objDescriptorB):
        for obj in (objDescriptorA, objDescriptorB):
            transform = obj.objTransform
            self.const2Descriptor[transform] = obj
            maya_helpers.addTag(transform, self.connection_name)
        pm.connectAttr(self._formatConnection(objDescriptorB),
                       self._formatConnection(objDescriptorA))
        return True

    def disconnect(self, objDescriptorA, objDescriptorB):
        if not self.isConnected(objDescriptorA, objDescriptorB):
            return
        pm.disconnectAttr(self._formatConnection(objDescriptorA),
                          self._formatConnection(objDescriptorB))
        for obj in (objDescriptorA, objDescriptorB):
            maya_helpers.delTag(obj, self.connection_name)

    def isConnected(self, objDescriptorA, objDescriptorB):
        connections = self.listConnections(objDescriptorA)
        return objDescriptorB in connections

    def listConnections(self, objDescriptor):
        if not self._checkHasTag(objDescriptor):
            return []
        connected_constr = pm.listConnections(
            self._formatConnection(objDescriptor))
        return [self.const2Descriptor[c] for c in connected_constr]

    def _formatConnection(self, objDescriptor):
        return "{}.{}".format(str(objDescriptor.objTransform),
                              self.connection_name)

    def _checkHasTag(self, objDescriptor):
        return objDescriptor.objTransform.hasAttr(self.connection_name)

    def hasConnection(self, objDescriptor):
        if self.listConnections(objDescriptor):
            return True
        else:
            return False

    def _hasConstructorConnection(self, transform):
        if not transform.hasAttr(self.connection_name):
            return False
        connectionList = pm.listConnections("{}.{}".format(
            str(transform), self.connection_name))
        return bool(connectionList)

    def getDescriptor(self, transform):
        if transform in self.const2Descriptor:
            return self.const2Descriptor[transform]

    def parse(self, *objDescriptors):
        for objDescr in objDescriptors:
            if self._hasConstructorConnection(objDescr.objTransform):
                self.const2Descriptor[objDescr.objTransform] = objDescr
