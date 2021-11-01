import sys, os, math
import importlib
import pymel.core as pm
import logging

logging.basicConfig()
log = logging.getLogger("GearCreatorUI")
log.setLevel(logging.DEBUG)

PATH = "path/to/src/"

def addToPyPath(path):
    if not os.path.exists(path): 
        return False
    if not path in sys.path:
        sys.path.append(path)
    return True

addToPyPath(PATH)
# ---------------------------------------------------------------

from gearCreator import gearCreator_test3 as gearCreator
importlib.reload(gearCreator)

from gearCreator import gearCreatorUi_test3 as gearCreatorUi
importlib.reload(gearCreatorUi)



# 1 / USING THE API ------------------------------------------------------------

#gearNetwork = gearCreator.GearNetwork()
#gearChain0  = gearNetwork.addChain(tWidth=0.3)
#gear0 = gearNetwork.addGear(3, gearChain0, tLen=0.5)
#gear1 = gearNetwork.addGear(2.5, gearChain0, tLen=0.5, linkedGear=gear0)

#gear1.activateMoveMode(gear0)
#pm.move(gear1.gearTransform, [0,0,6], os=True, r=True, wd=True)


# with 2 gear only, not a network. 
#gearNetwork.changeTWidth(0.25) -> OK 
#gear1.changeRadius(5)          -> OK
#gear1.changeRadius(4, False)   -> OK 
#gear1.activateMoveMode(gear0) -> OK

# Together
# pm.polyExtrudeFacet( 'plg.f[17:18]', 'plg.f[27:28]', kft=True, ltz=2, ls=(.5, .5, 0) )
# Facets are extruded then scaled together

# 2 / USING THE IHM ------------------------------------------------------------

ui = gearCreatorUi.GearCreatorUI(dock=False)
#ui.gearNetworks.append(gearNetwork)
