import sys
import os
import importlib
import logging

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

    # 1 / USING THE API -------------------------------------------------------

    gearNetwork = gear_network.GearNetwork()
    gearChain0 = gearNetwork.addChain(tWidth=0.3)
    gear0 = gearNetwork.addGear(3, gearChain0, tLen=0.5)
    gear1 = gearNetwork.addGear(2.5, gearChain0, tLen=0.5, linkedGear=gear0)
    gear1.activateMoveMode(gear0)

    # pm.move(gear1.gearTransform, [0,0,6], os=True, r=True, wd=True)

    # Together
    # pm.polyExtrudeFacet( 'plg.f[17:18]', 'plg.f[27:28]', kft=True, ltz=2, ls=(.5, .5, 0) )
    # Facets are extruded then scaled together

    # 2 / USING THE IHM -------------------------------------------------------
    #ui = gearCreatorUi.GearCreatorUI(dock=False)
