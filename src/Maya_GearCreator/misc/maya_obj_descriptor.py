import logging
import pymel.core as pm

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class MayaObjDescriptor():

    DEFAULT_PREFIX = "obj"
    gearIdx = 0

    CONSTRUCT_PRP_BLACK_LIST = [
        'message',
        'caching',
        'frozen',
        'isHistoricallyInteresting',
        'nodeState',
        'binMembership',
        'output'
    ]

    TRANSFORM_PRP_WHITE_LIST = [
        'translate',
        'rotate',
        'scale',
        'visibility'
    ]

    def __init__(self, objTransform, objConstructor, _class=None, name=None):
        self.objTransform = objTransform
        self.objConstructor = objConstructor
        self.name = name or self.genAutoName()

        for attrName in pm.listAttr(self.objConstructor):
            if attrName not in MayaObjDescriptor.CONSTRUCT_PRP_BLACK_LIST:
                self._createProperty("objConstructor", attrName, _class)
        for attrName in MayaObjDescriptor.TRANSFORM_PRP_WHITE_LIST:
            self._createProperty("objTransform", attrName, _class)

    def __eq__(self, another):
        if not hasattr(another, "objTransform") \
                or hasattr(another, "objConstructor"):
            return False
        return (self.objTransform == another.objTransform) \
                and (self.objConstructor == another.objConstructor)

    def __hash__(self):
        return hash(self.objTransform)

    def _createProperty(self, mayaObjAttrName, attrName, _class):
        if hasattr(_class, attrName): return    
        _class = _class or MayaObjDescriptor
        def getter(self):
            return getattr(self, mayaObjAttrName).getAttr(attrName)
        def setter(self, value):
            #TODO : protect setter! (by type?)
            getattr(self, mayaObjAttrName).setAttr(attrName, value)
        # self.attrName = property(getter, setter)
        setattr(_class, attrName, property(getter, setter))
        # TODO: MAYBE SETTER FOR EVERY PROPErTY.

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

    # GLOBAL SETTER -----------------------------------------------------------

    def setAttr(self, *kargs):
        for attrName, attrValue in kargs.items():
            if hasattr(self, attrName):
                setattr(self, attrName, attrValue)
            else:
                log.error("{} has no attribute: {}.".format(self.name,
                                                            attrName))
