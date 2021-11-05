import logging
import collections
import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor

importlib.reload(maya_obj_descriptor)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ConnectionsManager():

    def __init__(self, connection_name):
        self.const2Descriptor = {}
        self.connection_name = connection_name

    def connect(self, objDescriptorA, objDescriptorB):
        for obj in (objDescriptorA, objDescriptorB):
            if not issubclass(type(obj),
                              maya_obj_descriptor.MayaObjDescriptor):
                return False
            
            constructor = obj.objConstructor
            
            self.const2Descriptor[constructor] = obj
            
            if not constructor.hasAttr(self.connection_name):
                constructor.addAttr(
                    self.connection_name, 
                    keyable=True,
                    attributeType="bool")

        pm.connectAttr(self._formatConnection(objDescriptorB), 
                       self._formatConnection(objDescriptorA))
        return True

    def disconnect(self, objDescriptorA, objDescriptorB):
        if not self.hasConnection(objDescriptorA, objDescriptorB): return
        pm.disconnectAttr(self._formatConnection(objDescriptorA),
                       self._formatConnection(objDescriptorB))

    def hasConnection(self, objDescriptorA, objDescriptorB):
        connections = self.listConnections(objDescriptorA)
        return objDescriptorB in connections

    def listConnections(self, objDescriptor):
        if not self._checkNeighbourExists(objDescriptor): return []
        connected_constr = pm.listConnections(
            self._formatConnection(objDescriptor))
        return [self.const2Descriptor[c] for c in connected_constr]

    def _formatConnection(self, objDescriptor):
        return "{}.{}".format(str(objDescriptor.objConstructor),
                              self.connection_name)

    def _checkNeighbourExists(self, objDescriptor):
        return objDescriptor.objConstructor.hasAttr(self.connection_name)