import pymel.core as pm
import importlib

from Maya_GearCreator.misc import maya_obj_descriptor as mob
from Maya_GearCreator import consts

importlib.reload(mob)
importlib.reload(consts)


# TODO : CHANGING INTERNAL RADIUS of a gear ->
# if not rod -> just change raidus
# otherwise changing the radius of the rod
# rod -> change radius of all linked gears.

'''
cylinder faces:

"sub" -> SubdivisionsAxis

around  -> [0, sub -1 ]
bot     -> [sub, sub * 2 - 1]
top     -> [sub *2, sub *3 -1 ]

'''

class Rod(mob.MayaObjDescriptor):

    rodIdx = 0
    DEFAULT_PREFIX = "rod"

    def __init__(
            self, name=None,
            radius=consts.DEFAULT_ROD_RADIUS,
            height=consts.DEFAULT_ROD_LEN,
            linkedGear=None,
            gearNetwork=None,
            rodExists=False,
            rodData=None):

        if rodExists:
            rod_transform, rode_construct = rodData
        else:
            rod_transform, rode_construct = pm.polyCylinder()

        super(Rod, self).__init__(rod_transform, rode_construct, Rod, name)

        self.radius = radius
        self.height = height

        if linkedGear:
            self.translate = linkedGear.translate
        if gearNetwork:
            self.gearNetwork = gearNetwork

        self.lockTransform()

    def changeLen(self, newHeight, top=True):
        selection_bk = pm.ls(sl=True)
        pm.select(self.getFacesStr(top))
        pm.move(0, newHeight, 0, r=True, os=True, wd=True)  # TODO : checks keyswords.
        pm.select(clear=True)
        pm.select(selection_bk)  # ??

    def getFacesStr(self, top=True):
        faces_idx = {
            True: self.getTopFaces,
            False: self.getBotFaces
        }[top]()
        return "{}.f{}".format(self.name, list(faces_idx))

    def getTopFacesIdx(self):
        return (self.subdivisionsAxis * 2, self.subdivisionsAxis * 3 - 1)

    def getBotFacesIdx(self):
        return (self.subdivisionsAxis, self.subdivisionsAxis * 2 - 1)

    def getLen(self, top=True):
        faces = pm.ls(self.getFacesStr(top))
        point_pos = faces[0].getPoints()[0]
        height = point_pos[1]  # TODO: to change if multiple orientation.
        return height

    LEN_MARGIN = 3

    def getMinMaxTop(self):
        gearList = self.getGears()
        topHeight = self.getLen(top=True)
        _max = topHeight + Rod.LEN_MARGIN
        if not gearList:
            _min = self.height / 2
            return _min, _max
        else:
            _min = None
            for g in self.getGears():
                pos = g.translate[1]
                # TODO : Depends on orientation. !!!!!!!!!
                height = pos + g.height / 2
                if not _min or height > _min:
                    _min = height
        return _min, _max

    # INVERTED! so factor in slider shall be negative! probably in setter/getter !!!
    def getMinMaxBot(self):
        gearList = self.getGears()
        botHeight = self.getLen(top=False)
        _max = botHeight - Rod.LEN_MARGIN
        if not gearList:
            _min = self.height / 2
            return _min, _max
        else:
            _min = None
            for g in self.getGears():
                pos = g.translate[1]
                # TODO : Depends on orientation. !!!!!!!!!
                height = pos - g.height / 2
                if not _min or height < _min:
                    _min = height
        return _min, _max

    def changeRadius(self, newRadius):
        # CHECKERS....
        self.radius = newRadius
        for g in self.getGears():
            g.internalRadius = newRadius

    def _lockChain_recc(self, rootGear, lock=True):
        func = {
            True: mob.MayaObjDescriptor.activateParentConstraint,
            False: mob.MayaObjDescriptor.desactivateParentConstraint
        }
        gears = [g for g in self.getGears()
                    if g != rootGear]
        for g in gears:
            g.lockTransform(not lock)
            func[lock](self, *gears)
        for g in gears:
            new_gears, new_rod = g._find_children(self)
            g._lockChain_recc(*new_gears, lock=lock, rod=new_rod)

    def getGears(self):
        return self.gearNetwork.getGearsFromRod(self)
