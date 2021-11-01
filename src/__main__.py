import sys
import os
import inspect
import logging
import importlib

MODULE_PATH = "D:\dev\Maya_GearCreator\src"

def addToPyPath(path):
    if not os.path.exists(path):
        return False
    if path not in sys.path:
        sys.path.append(path)
    return True

print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
print (os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
print(inspect.getfile(inspect.currentframe()))
print(os.path.dirname(__file__))
print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

addToPyPath(os.path.dirname(__file__))
from gearCreator.src.gui import mainWindow
importlib.reload(mainWindow)

#def registerPlugin(): pass
#def unRegisterPlugin(): pass

if __name__ == "__main__":
    # launching plugin --------------------------------------------------------

    logging.basicConfig()
    log = logging.getLogger("GearCreator")
    log.setLevel(logging.DEBUG)

    ui = mainWindow.GearCreatorUI(dock=False)

