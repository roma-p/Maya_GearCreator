import pymel.core as pm


# if group exist -> return group, otherwise create it and return it.
def createGroupSafe(groupName, parentObj=None):
    # FIXME: check may not be a group....
    # FIXME: check for parentObj existence.
    # check group existance:

    def _get_group(groupName, parentObj=None):
        if parentObj:
            for child in pm.listRelatives(parentObj, children=True):
                if str(child) == groupName:
                    return child
        else:
            allNameMatched = pm.ls(groupName)
            allTopLevel = [grp for grp in allNameMatched
                           if not pm.listRelatives(grp, parent=True)]
            if allTopLevel:
                return allTopLevel[0]

    group = _get_group(groupName, parentObj)
    if group:
        return group

    group = pm.group(em=True, name=groupName)
    pm.parent(group, parentObj)
    return group


def createGroup(groupName, parentObj=None):
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


def safeAddAttr(obj, attrName, attributeType, keyable=True,):
    if not obj.hasAttr(attrName):
        obj.addAttr(attrName, attributeType=attributeType, keyable=keyable)
