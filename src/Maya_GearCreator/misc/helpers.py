import pymel.core as pm


# if group exist -> return group, otherwise create it and return it.
def createGroupSafe(groupName, parentObj=None):
    # FIXME: check may not be a group....
    # FIXME: check for parentObj existence.
    # check group existance:

    group = getGroup(groupName, parentObj)
    if group:
        return group

    group = pm.group(em=True, name=groupName)
    pm.parent(group, parentObj)
    return group


def getGroup(groupName, parentObj=None):
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


def hashable(v):
    """Determine whether `v` can be hashed."""
    try:
        hash(v)
    except TypeError:
        return False
    return True


def _formatMeshStr(transformName, meshType, *args):
    meshTypeDict = {
        "face": "f",
        "vertex": "vtx",
        "edge": "e"
    }
    str_list = []
    for arg in args:
        if type(arg) in (set, list, tuple):
            str_list.append("{}.{}[{}:{}]".format(
                transformName, meshTypeDict[meshType],
                arg[0], arg[1]))
        elif isinstance(arg, int):
            str_list.append("{}.{}[{}]".format(
                transformName, meshTypeDict[meshType], arg))
    return str_list


def ls(transformName, meshType, *args, **kargs):
    ret = []
    strs = _formatMeshStr(transformName, meshType, *args)
    for _tmp in strs:
        _ret = pm.ls(_tmp, **kargs)
        if _ret:
            ret += _ret
    return ret


def select(transformName, meshType, *args, **kargs):
    _tmp = _formatMeshStr(transformName, meshType, *args)
    for i in range(len(_tmp)):
        if i:
            kargs["add"] = True
        pm.select(_tmp[i], **kargs)
