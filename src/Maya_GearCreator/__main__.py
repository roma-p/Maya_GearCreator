import sys
import os
import json
import logging
import importlib

CUSTOM_PATH = None

def addToPyPath(path):
    if not os.path.exists(path):
        return False
    if path not in sys.path:
        sys.path.append(path)
    return True

def parseJson(path):


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

prio list:
- Comment fr un bon parser automatique? 

!!
* calculate min/max for ihm either from fix values or from function... 
* On exit: change back colors... maybe on del? 

"""
