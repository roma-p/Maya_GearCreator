import sys
import os
import logging
import importlib

DEBUG_PATH = "D:/dev/Maya_GearCreator/src/"


def addToPyPath(path):
    if not os.path.exists(path):
        return False
    if path not in sys.path:
        print("pas deja la")
        sys.path.append(path)
    else:
        print('déja laaa')
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
