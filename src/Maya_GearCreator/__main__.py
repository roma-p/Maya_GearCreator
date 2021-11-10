import sys
import os
import logging
import importlib

from Maya_GearCreator.misc import helpers
from Maya_GearCreator import parser
from Maya_GearCreator import consts

importlib.reload(helpers)
importlib.reload(parser)
importlib.reload(consts)


DEBUG_PATH = "D:/dev/Maya_GearCreator/src/"


def addToPyPath(path):
    if not os.path.exists(path):
        return False
    if path not in sys.path:
        sys.path.append(path)
    return True

# def registerPlugin(): pass
# def unRegisterPlugin(): pass


if __name__ == "__main__":
    # launching plugin --------------------------------------------------------
    if DEBUG_PATH:
        addToPyPath(os.path.dirname(DEBUG_PATH))
        from Maya_GearCreator.gui import main_window
        importlib.reload(main_window)

    logging.basicConfig()
    log = logging.getLogger("GearCreator")
    log.setLevel(logging.DEBUG)

    helpers.TAG_CATEGORY = consts.TAG_CATEGORY

    ui = main_window.GearCreatorUI(dock=False)
    #ui.addExistingGearNetwork(*parser.parse())

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

* change radius: 
    - si un voisin seuelement, c' le gear actuel qui se décale, pas les voisins....
      (plus sympa à l'utilisation).
* Change teeth:
    -automatically adjust neighbours? 
    - some of gearSpacing of two neighbours = 1 ? 
prio list:
    - bug parent constraint
    - bug resize neighbour
    - nettoyage des duplicat d'information
    - refacto en utilisant le gear primitive
    (debug le deplacement)

!!
* calculate min/max for ihm either from fix values or from function... 
* recalculated at every populate.
* gearOffset property and internal radius to ovveride.

* function "AD TAG" ds misc... (hidden not keyable)
* not used str on transform so can have multiple gears with same name.
"""
