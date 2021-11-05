import sys
import os
import importlib
import logging
import pymel.core as pm
from maya import cmds


logging.basicConfig()
log = logging.getLogger("GearCreatorUI")
log.setLevel(logging.DEBUG)

PATH = "path/to/src/"

DEBUG_PATH = "D:/dev/Maya_GearCreator/src/"


def addToPyPath(path):
    if not os.path.exists(path):
        return False
    if path not in sys.path:
        sys.path.append(path)
    return True


if __name__ == "__main__":
    addToPyPath(os.path.dirname(DEBUG_PATH))
    from Maya_GearCreator import gear_network
    importlib.reload(gear_network)

    from Maya_GearCreator.misc import maya_obj_descriptor
    importlib.reload(maya_obj_descriptor)
    from Maya_GearCreator.gears import gear_abstract
    importlib.reload(gear_abstract)

    from Maya_GearCreator.gears import gear_basic
    importlib.reload(gear_basic)



    # 1 / USING THE API -------------------------------------------------------

    gearNetwork = gear_network.GearNetwork()
    gearChain0 = gearNetwork.addChain(tWidth=0.3)
    gear0 = gearNetwork.addGear(3, gearChain0, tLen=0.5)
    gear1 = gearNetwork.addGear(2.5, gearChain0, tLen=0.5, linkedGear=gear0)
    gear1.activateMoveMode(gear0)
    print("aaaaaaaaaaaaa")
    #print(gear0.gearTransform.__dict__.keys())
    print("aaaaaaaaaaaaa")
    #print(gear0.gearConstructor.__dict__.keys())
    #print(gear0.gearConstructor.__dict__)
    #print(gear0.gearConstructor.__dict__["__apiobjects__"])
    #print(pm.listAttr("gear0"))
    print(gear0.gearConstructor)
    print(pm.listAttr(gear0.gearConstructor))
    

    # pm.move(gear1.gearTransform, [0,0,6], os=True, r=True, wd=True)

    # Together
    # pm.polyExtrudeFacet( 'plg.f[17:18]', 'plg.f[27:28]', kft=True, ltz=2, ls=(.5, .5, 0) )
    # Facets are extruded then scaled together

    # 2 / USING THE IHM -------------------------------------------------------
    #ui = gearCreatorUi.GearCreatorUI(dock=False)
    #gearTransform, gearConstructor = pm.polyGear(sides=16, radius=1, internalRadius=0.3, height=1, heightDivisions=10, gearSpacing=0.6 )
    
    # print(pm.polyCube(name="truc"))
    # print(pm.polyPipe())
    #print(pm.polyGear(name="caca"))

    # how to make gear works __________________________________________________

    #print(cmds.polyGear())
    #gear_shape = pm.ls( selection=True)[0]
    #pm.rename(gear_shape, "bijour")
    #print(gear_shape)
    #for node in pm.listHistory(gear_shape):
    #    if isinstance(node,pm.nodetypes.PolyGear):
    #        construct = node
    #        break    
    #print(pm.nodetypes.PolyGear)
    #print(construct)
    #print(pm.listAttr(construct))
    
    # NO ARGUMENT FOR POLYGEAR, need to set after in constructor.
    # how to make gear works __________________________________________________

    # RUNTIME PROPERTIES--------------------------------------------------------

    class Foo():
      pass
    
    def get_x(self):
      return 3
    
    def set_x(self, value):
      print("set x on %s to %d" % (self, value))
    
    setattr(Foo, 'x', property(get_x, set_x))
    
    #foo1 = Foo()
    #foo1.x = 12
    #print(foo1.x)

    
    class Foot():
        
        def __init__(self):

            def get_x(self):
              return 3
            
            def set_x(self, value):
              print("set x on %s to %d" % (self, value))

            setattr(Foot, 'x', property(get_x, set_x))

    #foo1 = Foot()
    #foo1.x = 12
    #print(foo1.x)

    class Foot2():
        
        def __init__(self, prpName, className=None):
            self._createProperty(prpName, className)

        def _createProperty(self, name, className=None):
            def get(self):
              return self.__dict__[name]
              return 3
            def set(self, value):
                self.__dict__[name] = value
            if not className: className=Foot2
            setattr(className, name, property(get, set))

    class Foot2Rue(Foot2):
        def __init__(self):
            super(Foot2Rue, self).__init__("bisous", Foot2Rue)

    #class Foot2Rue

    #foo1 = Foot2("lul")
    #foo1.lul = 12
    #print(foo1.lul)

    #foo2 = Foot2Rue()
    #foo3 = Foot2Rue()
    #foo2.bisous = 5
    #foo3.bisous = 4
    #print(foo2.bisous)
    #print(foo3.bisous)


    # CLASS MERE OK. 

    # print(cmds.polyGear())
    # gear_shape = pm.ls( selection=True)[0]
    # pm.rename(gear_shape, "bijour")
    # print(gear_shape)
    # for node in pm.listHistory(gear_shape):
        # if isinstance(node,pm.nodetypes.PolyGear):
            # construct = node
            # break    

    # descriptor = maya_obj_descriptor.MayaObjDescriptor(gear_shape, construct, _class=None, name="caca")
    # print("-------------------")
    # print(descriptor.__dict__)
    # print(descriptor.radius)
    # descriptor.radius = 2
    # print(descriptor.radius)
    # print(descriptor.name)
    # descriptor.name = "violencePolicière."
    # print(descriptor.name)

    # RUNTIME PROPERTIES--------------------------------------------------------
    newGearDescription1 = gear_basic.GearBasic("troutrou")
    newGearDescription1.radius = 5
    newGearDescription1.sides = 50
    print(newGearDescription1.name)
    newGearDescription1.name = "haha"
    print(newGearDescription1.name)

    newGearDescription2 = gear_basic.GearBasic(
        name="bijour",
        linkedGear=newGearDescription1)
    print(newGearDescription2.listNeigbours()[0].name)
    print(newGearDescription1.listNeigbours()[0].name)
    #newGearDescription2 = maya_obj_descriptor.NewGear("bouh")
    #newGearDescription2.radius = 2
    #newGearDescription2.sides = 15
    #newGearDescription2.name = "caca"



