import sys
import os
import json
import logging
import importlib

CUSTOM_PATH = ""

def addToPyPath(path):
    if not os.path.exists(path):
        return False
    if path not in sys.path:
        sys.path.append(path)
    return True

if CUSTOM_PATH:
    addToPyPath(os.path.dirname(CUSTOM_PATH))

from Maya_GearCreator.gui import main_window
from Maya_GearCreator import parser
from Maya_GearCreator import consts
from Maya_GearCreator.misc import maya_helpers

importlib.reload(main_window)
importlib.reload(maya_helpers)
importlib.reload(parser)
importlib.reload(consts)

# def registerPlugin(): pass
# def unRegisterPlugin(): pass


if __name__ == "__main__":
    # launching plugin --------------------------------------------------------

    logging.basicConfig()
    log = logging.getLogger("GearCreator")
    log.setLevel(logging.DEBUG)

    maya_helpers.TAG_CATEGORY = consts.TAG_CATEGORY

    ui = main_window.GearCreatorUI(dock=False)
    ui.addExistingGearNetwork(*parser.parse())

"""
TODO LIST:
* init:
    - placer le gear au bon endroit (attendre refacto ac gear).
* resize:
    - resize neigbours fix.
*!! multi forme. -> différentes formes de gear possibles
- mayaObjDescriptor -> not 'addInput', just 'addRef' (no need for it to be an input?).
prio list:
- Comment fr un bon parser automatique? 

!!
* calculate min/max for ihm either from fix values or from function... 
* On exit: change back colors... maybe on del? 

adjust gear: iteration :

1) current gear -> get all teeth left point 
find the one closer to the center of parent gear -> "A"
2) parent gear -> get all hole right point
find the one closer to "A", "B"
3) by iretation -> rotate current gear until 


- BUTTON "ADJUST ROD": make the rod the smaller possible given the linked gears.
- WHEN changing radius up: adjusting internal radius too? 

- REFACTO "MOVEALONG":
    - activate mode along:
        create a null object at center of root gear, whith gear as child
    - during move along:
        this nul rotate (so we can use the slider as angles)
        we rotate the gear so it is always ajusted (and we count rotate the other neigbour gears)

    - desactivate mode along:
        we restore previous archi
    therefore:
        - snapping on 90° degres (or already used degres on X / Y ) is easy.
        - we use the "ajust teeth" method once: at gear creation.


AIM CONSTRAINT: TO CONSTRAINT CIRCLE AND NOT THE GEAR ITSELF, WILL WORK
MORE CASE THAT I EXPECTED.

"""
