import logging
import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor
from Maya_GearCreator.misc import helpers


importlib.reload(maya_obj_descriptor)
importlib.reload(helpers)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ConnectionsManager():

    def __init__(self, connection_name):
        self.const2Descriptor = {}
        self.connection_name = connection_name

    def connect(self, objDescriptorA, objDescriptorB):
        for obj in (objDescriptorA, objDescriptorB):
            constructor = obj.objConstructor
            self.const2Descriptor[constructor] = obj
            helpers.addTag(constructor, self.connection_name)
        pm.connectAttr(self._formatConnection(objDescriptorB),
                       self._formatConnection(objDescriptorA))
        return True

    def disconnect(self, objDescriptorA, objDescriptorB):
        if not self.isConnected(objDescriptorA, objDescriptorB):
            return
        pm.disconnectAttr(self._formatConnection(objDescriptorA),
                          self._formatConnection(objDescriptorB))
        for obj in (objDescriptorA, objDescriptorB):
            helpers.delTag(obj, self.connection_name)

    def isConnected(self, objDescriptorA, objDescriptorB):
        connections = self.listConnections(objDescriptorA)
        return objDescriptorB in connections

    def listConnections(self, objDescriptor):
        if not self._checkNeighbourExists(objDescriptor):
            return []
        connected_constr = pm.listConnections(
            self._formatConnection(objDescriptor))
        return [self.const2Descriptor[c] for c in connected_constr]

    def _formatConnection(self, objDescriptor):
        return "{}.{}".format(str(objDescriptor.objConstructor),
                              self.connection_name)

    def _checkNeighbourExists(self, objDescriptor):
        return objDescriptor.objConstructor.hasAttr(self.connection_name)

    def hasConnection(self, objDescriptor):
        if self.listConnections(objDescriptor):
            return True
        else:
            return False

    def getDescriptor(self, constructor):
        if constructor in self.const2Descriptor:
            return self.const2Descriptor[constructor]
