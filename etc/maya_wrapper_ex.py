import sys
import os
import importlib
import logging
import pymel.core as pm

from Maya_GearCreator.maya_wrapper import maya_obj_descriptor as mob
from Maya_GearCreator.maya_wrapper import connections_manager

"""
    1 Basics ------------------------------------------------------------------

"waya wrapper" library is to easily build pymel "objTransform" wrappers / descriptors
in order to define custom methods / behaviour for those transform inside the wrapper.
"""

# using a sphere as example.
sphereTransform, sphereConstructor = pm.polySphere()

# to declare a wrapper:
sphereWrapper = mob.MayaObjDescriptor(sphereTransform)

# transform node can be accessed:
sphereTransform = sphereWrapper.objTransform

'''
Wrapper automatically declares properties for following Transform attributes:
- translate
- rotate
- scale
- visibility
- name
(since they are properties, maya_wrapper does not cache any data, 
 transform attributes are beeing directly accessed / modified)
'''

# so rather than typing: 
visibility = objTransform.visibility.get()
objTransform.visibility.set(True)

# you can type:
visibility = sphereWrapper.visibility
sphereWrapper.visibility = True

# modifying name as follow will modify it instantly in the DAG view: 
sphereWrapper.name = "test0"



'''
    2 Input nodes. ------------------------------------------------------------

You can add an "input node" to the wrapper. 
You will be able to access the node attributes the same way you did for the
transform node.
'''

# For instance: referencing the sphere constructor node:
sphereWrapper.addInput(sphereConstructor, "constructor")

# so rather than typing something like:
inputNode = next((i for i in objTransform.inputs() 
                 if isinstance(i, SomeDataType))) # some code to get the constructor.
currentRadius = inputNode.radius.get()            # accessing its attributes.
inputNode.radius.set(newRadius)

# you can type:
currentRadius = sphereWrapper.constructor.radius
sphereWrapper.constructor.radius = newRadius

# same here: we extrude a sphere then reference its node.
_, extrudeInput = pm.polyExtrudeFacet(
    "{}.f[1]".format(sphereWrapper.name), 
    localTranslateZ=0.5)
sphereWrapper.addInput(extrudeInput, "extrude")

# so edition becomes:
sphereWrapper.extrude.localTranslateZ = 0.5

# this is espacially useful when parsing an alreaydy existing scene
# when you may not have easily the reference to the input node in your code. 



'''
    3 Groups. -----------------------------------------------------------------

you can wrap groups too. 
If the group does not yet exist, it can be created automatically.
'''

# will create a new group called "myGroup" as child of sphereTransform
newGroup = mob.MayaObjDescriptor(
    name="myGroup",
    group=True,
    parentTransform=sphereTransform)

# will create a wrapper for the groupTransform object.
groupTransform = pm.group(em=True, name="myGroup2")
mob.MayaObjDescriptor(
    group=True,
    objExists=True,
    objTransform=groupTransform)



'''
    4 Parsing basics ----------------------------------------------------------
All references to other nodes (parent / children / connections / input nodes),
are stored within the scene, NOTHING is stored in code so that no information
is lost between mutliple code execution. 
'''

# at new code execution: 
sphereTransform = userDefinedParseMethod() # a custom method to get objTransform
sphereWrapper = mob.MayaObjDescriptor(
    sphereTransform, 
    objExists=True)

# then, "constructor" and "extrude" will be accessable again:
currentRadius = sphereWrapper.constructor.radius



'''
    5 inheriting MayaObjDescriptor --------------------------------------------
you can inherit MayaObjDescriptor to add custom method for a given 
transform type, to add other properties etc...
'''

class SphereWrapper(mob.MayaObjDescriptor):
    '''
    A basic sphere wrapper: 
    - if not objExists, will create a sphere
    - radius can be controlled using "radius" attribute
    - ensure that radius is between min and max attributes
    '''

    def __init__(self,
        objExists=False, 
        sphereTransform=None):

        # if we aren't parsing existing scene but creating a new object/wrapper
        # then we first create the mesh.
        if not objExists:
            sphereTransform, sphereConstructor = pm.polySphere()

        super(SphereWrapper, self).__init__(
            objTransform=sphereTransform,
            _class=SphereWrapper,
            objExists=objExists)
        # "_class" has to be an argument of __init__ 
        # (since you can add properties only to a class and not to an instance).

        # if we are only parsing, we don't need the addInput method as the 
        # connection between transform node and objConstructor have already
        # been declared.
        if not objExists:
            self.addInput(objConstructor, "constructor")

        self.min = 1
        self.max = 5

    @property
    def radius(self):
        return self.constructor.radius

    @radius.setter
    def radius(self, newRadius):
        newRadius = min(newRadius, self.max)
        newRadius = max(newRadius, self.min)
        self.constructor.radius = newRadius

    def otherCustomMethod(self):
        pass


# A) To create a new sphere using SphereWrapper:
sphereWrapper = SphereWrapper()
sphereWrapper.radius = 7
print(sphereWrapper.radius) # shall be 5
sphereWrapper.visibility = True

# B) To parse the scene to recreate the sphereWrapper objects:
sphereTransform = userDefinedParseMethod()
sphereWrapper = SphereWrapper(objExists=True,
                              sphereTransform=sphereTransform)
print(sphereWrapper.radius)     # shall be 5
sphereWrapper.radius = 0
print(sphereWrapper.radius)     # shall be 1
print(sphereWrapper.visibility) # shall be True


'''
    6 Children manager --------------------------------------------------------
MayaObjDescriptor also offers a simplified children manager system.
using MayaObjDescriptor.createChildrenM method:
- the object return can be manipulated as a python 'set' type.
- but the data will be acquired from the scene and modify the scene.
- you can sort children by 'tag'
'''

class GroupWrapper(mob.MayaObjDescriptor):
    '''
    a basic group wrapper, parent of two kinds of spheres: "typeA" and "typeB".
    '''
    def __init__(self, name=None, objExists=False, objTransform=None):
        super(GroupWrapper, self).__init__(
            objTransform=objTransform, 
            name=name,
            objExists=objExists)
        self.typeA_Children = self.createChildrenM(tag="typeA")
        self.typeB_Children = self.createChildrenM(tag="typeB")

myGroup = GroupWrapper("myGroup")

sphere1 = SphereWrapper(name="sphere1")
sphere2 = SphereWrapper(name="sphere2")
sphere3 = SphereWrapper(name="sphere3")


# A) To add / remove / iter children:

# childrenManager "add" method: will set "GroupWrapper" as parent obj in DAG:
myGroup.typeA_Children.add(sphere1)
myGroup.typeA_Children.add(sphere2)
myGroup.typeB_Children.add(sphere3)
# "myGroup" obj shall have as children the objTransfrom: sphere1, sphere2, sphere3.

for sphere in myGroup.typeA_Children:
    print(sphere.name)
# shall print "sphere1" and "sphere2", not "sphere3"

print(sphere3 in myGroup.typeA_Children)  # shall print False

myGroup.typeA_Children.discard(sphere2)
# "discard" method will parent the objTransform of sphere2 directly to the world.

print(sphere2 in myGroup.typeA_Children)  # shall print False


# B) To parse existing scene:

sphereTransform = customParseMethod_Sphere()
myGroupTransform = customParseMethod_Group()

# this part does not change
sphereWrappers = [SphereWrapper(objExists=True, sphereTransform=transform)
                    for transform in sphereTransform]
myGroup = GroupWrapper(objExists=True, objTransform=myGroupTransform)

# but we need to call the method ChildrenManager.parse(*objDescriptors)
# (to feed a internal map 'objTransform'>'objWrapper')
myGroup.typeA_Children.parse(*sphereWrappers)
myGroup.typeB_Children.parse(*sphereWrappers)

print(sphere1 in myGroup.typeB_Children) # shall be False
print(sphere3 in myGroup.typeB_Children) # shall be True



'''
    7 Connection Manger -------------------------------------------------------
maya wrapper lib can also store references between multiple transform nodes.
(it does so by creating a connection between the nodes).
This is useful to keep a list a reference between some wrappers
(a "neighbour list" for example).
'''

# A) Add and use a connectionManager object:

sphere1 = SphereWrapper(name="sphere1")
sphere2 = SphereWrapper(name="sphere2")
sphere3 = SphereWrapper(name="sphere3")

neighbourManager = connections_manager.ConnectionsManager("NEIGHBOUR")

neighbourManager.connect(sphere1, sphere2)
neighbourManager.connect(sphere1, sphere3)

print(neighbourManager.isConnected(sphere1, sphere2))  # shall print True
print(neighbourManager.isConnected(sphere2, sphere3))  # shall print False

for sphereWrappers in neighbourManager.listConnections(sphere1):
    sphereWrappers.visibility = False
# shall hide sphere2 and sphere3.

sphere2.visibility = True
sphere3.visibility = True

neighbourManager.disconnect(sphere1, sphere2)
print(neighbourManager.hasConnection(sphere2))  # shall print False

# B) Parse an existing scene:

sphereTransform = customParseMethod_Sphere()
sphereWrappers = [SphereWrapper(objExists=True, sphereTransform=transform)
                    for transform in sphereTransform]

# similar to childrenManager parsing.
neighbourManager = connections_manager.ConnectionsManager("NEIGHBOUR")
neighbourManager.parse(*sphereWrappers)

sphere1 = next((s for s in sphereWrappers
                if s.name ="sphere1"))  # getting sphere1 wrapper.
print(neighbourManager.hasConnection(sphere1))  # shall print True
