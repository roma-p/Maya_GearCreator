import logging
import pymel.core as pm


# if group exist -> return group, otherwise create it and return it.
def createGroup(groupName, parentObj=None):
    # FIXME: check may not be a group....
    # FIXME: check for parentObj existence.
    # check group existance:
    for child in pm.listRelatives(parentObj, children=True):
        if child.name == groupName:
            return child
    group = pm.group(em=True, name=groupName)
    pm.parent(group, parentObj)
    return group


TAG_CATEGORY = None


# create a hidden immutable attribute to obj (if does not already exists)
def addTag(obj, tagName, category=TAG_CATEGORY):
    if not obj.hasAttr(tagName):
        obj.addAttr(
            tagName,
            attributeType="bool",
            category=category,
            hidden=True,
            keyable=True)


def delTag(obj, tagName):
    if not obj.hasAttr(tagName):
        obj.deleteAttr(tagName)
