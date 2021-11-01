import importlib
import logging

from gearCreator.src import gear_chain
importlib.reload(gear_chain)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GearNetwork():
    DEFAULT_PREFIX = "gearNetwork"
    gearNetworkIdx = 0

    def __init__(self, name=None):
        self.name = name or self.genAutoName()
        self.gearDict = {}
        self.chainList = []
        self.multiChainGear = {}

    def genAutoName(cls):
        name = "{}{}".format(cls.DEFAULT_PREFIX, cls.gearNetworkIdx)
        cls.gearNetworkIdx += 1
        return name

    # Redondant but used as signal callback for UI
    def setName(self, name):
        self.name = name

    def addChain(self, tWidth=0.3):
        chain = gear_chain.GearChain(self, tWidth)
        self.chainList.append(chain)
        return chain

    def addGear(self, radius, gearChain,
                tLen=None, linkedGear=None,
                name=None):
        gear = gearChain.addGear(radius, tLen, linkedGear, name)
        self.gearDict[gear.gearTransform] = (gear, gearChain)
        return gear

    def getGearFromTransform(self, transform):
        gearInfo = self.gearDict.get(transform)
        if gearInfo : return gearInfo[0]
        else : return None

    def delGear(self, gear):
        pass
