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

    ui = main_window.GearCreatorUI(dock=False)


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
*! Refacto en utilisant le gear primitive.
*! Save des données:
    - faire le mengge ds les duplications: uniquement sur les transform et contruct si necessaire.
    - faire un générateur de propriété pr les attr du contructor.
    - Trouver comment sauver les
        - neighbours
        - données des chaines / network.
* gestion de la géométrie:
    - controler par chaine
    - override partiel possible par gear.
*!! multi forme. -> différentes formes de gear possibles
*!! multi chain.

prio list:
    - bug parent constraint
    - bug resize neighbour
    - nettoyage des duplicat d'information
    - refacto en utilisant le gear primitive
    (debug le deplacement)
"""
