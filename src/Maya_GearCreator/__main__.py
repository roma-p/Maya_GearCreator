import sys
import os
import logging
import importlib

DEBUG_PATH = "D:/dev/Maya_GearCreator/src/"


def addToPyPath(path):
    if not os.path.exists(path):
        return False
    if path not in sys.path:
        sys.path.append(path)
    return True


if DEBUG_PATH:
    addToPyPath(os.path.dirname(DEBUG_PATH))

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

    # ui = main_window.GearCreatorUI(dock=False)
    ui = main_window.GearCreatorUI(dock=False)
    ui.addExistingGearNetwork(*parser.parse())

"""
TODO LIST:
* deplacement:
    - corriger la translation: trouver les bon chiffres
    - se demerder pour la rotation aussi
* init:
    - placer le gear au bon endroit (attendre refacto ac gear).
* resize:
    - bug du reset contraintes (peut être un signal pas disconnect ou un leak).
    - resize neigbours fix.
* gestion de la géométrie:
    - controler par chaine
    - override partiel possible par gear.
*!! multi forme. -> différentes formes de gear possibles
*!! multi chain.

* Change teeth:
    -automatically adjust neighbours? 
    - some of gearSpacing of two neighbours = 1 ? 
prio list:
    - bug parent constraint
    - bug resize neighbour
    - nettoyage des duplicat d'information
    - refacto en utilisant le gear primitive
    (debug le deplacement)
- REFACTO DES DESCRIPTOR. 
    - only add properties for transform, no input in __init__
    - add a "addInput" method name, input. 
    - (add an attr to the input or a connection to be easily parsed.)
- Comment fr un bon parser automatique? 

!!
* calculate min/max for ihm either from fix values or from function... 
* recalculated at every populate.
* gearOffset property and internal radius to ovveride.

* function "AD TAG" ds misc... (hidden not keyable)
* not used str on transform so can have multiple gears with same name.


* better if new gears don't collide with other gears....
easy to do for rode. 
* On exit: change back colors... maybe on del? 

"""
