import logging
import importlib
from functools import partial
#
import pymel.core as pm
from maya import OpenMayaUI as omui
from maya import OpenMaya as om
#
from Maya_GearCreator.Qt import QtWidgets, QtCore, QtGui
from Maya_GearCreator import Qt
#
from Maya_GearCreator import gear_network
from Maya_GearCreator.gui import base_widgets
from Maya_GearCreator.gui import gear_window
from Maya_GearCreator.gui import rod_window
from Maya_GearCreator.gui import gear_networks_window
from Maya_GearCreator import consts

importlib.reload(gear_network)
importlib.reload(base_widgets)
importlib.reload(gear_window)
importlib.reload(rod_window)
importlib.reload(consts)
importlib.reload(gear_networks_window)

log = logging.getLogger("GearCreatorUI")
log.setLevel(logging.DEBUG)

# RESOLVING IMPORT ------------------------------------------------------------

# importing wrapInstance, Signal
binding_version = Qt.__binding_version__
if binding_version == "PySide":
    from shiboken import wrapInstance
    from Maya_GearCreator.Qt.QtCore import Signal 
    log.debug("Using PySide with shiboken")
elif binding_version.startswith("PyQt"):
    from sip import wrapinstance as wrapInstance
    from Maya_GearCreator.Qt.QtCore import pyqtSignal as Signal
    log.debug("Using PyQt with sip")
else:
    from shiboken2 import wrapInstance
    from Maya_GearCreator.Qt.QtCore import Signal 
    log.debug("Using PySide2 with shiboken")

# HELPERS ---------------------------------------------------------------------

def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(int(win), QtWidgets.QMainWindow)
    return ptr


def getDock(name="GearCreatorDock"):
    deleteDock(name)
    ctrl = pm.workspaceControl(name,
                               dockToMainWindow=("right", 1),
                               label="GearCreatorUI")
    qtControl = omui.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(int(qtControl), QtWidgets.QWidget)
    return ptr


def deleteDock(name="GearCreatorDock"):
    if pm.workspaceControl(name, query=True, exists=True):
        pm.deleteUI(name)

# MAIN UI ---------------------------------------------------------------------

class GearCreatorUI(QtWidgets.QWidget):

    def __init__(self, dock=True):

        if dock:
            parent = getDock()
        else:
            deleteDock()
            try:
                pm.deleteUI("GearCreatorUI")
            except:
                log.debug("No previous UI exists")

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName("GearCreatorUI")
            parent.setWindowTitle("Gear Creator")
            layout = QtWidgets.QVBoxLayout(parent)  #???, useless?

            self.selectionCallbackIdx = om.MEventMessage.addEventCallback(
                "SelectionChanged",
                partial(GearCreatorUI.selectCallback, self))

            def closeEvent(QWidget):
                if self.selectionCallbackIdx is not None:
                    om.MMessage.removeCallback(self.selectionCallbackIdx)
                    self.selectionCallbackIdx = None
            parent.closeEvent = closeEvent

        super(GearCreatorUI, self).__init__(parent)

        self.layout = QtWidgets.QGridLayout(self)
        
        self.newGearNetwork = QtWidgets.QPushButton("new gear network")
        self.layout.addWidget(self.newGearNetwork, 0, 0)
        self.newGearNetwork.clicked.connect(
            partial(GearCreatorUI.addGearNetwork, self))
        
        # hidden gear widget.
        self.gearWidget = gear_window.GearWidget()
        self.layout.addWidget(self.gearWidget, 1, 0)
        self.gearWidget.setVisible(False)

        # hidden rod widget
        self.rodWidget = rod_window.RodWidget()
        self.layout.addWidget(self.rodWidget, 1, 0)
        self.rodWidget.setVisible(False)

        # visible (default) rod gearNetworksWidget
        self.gearNetworksWidget = gear_networks_window.GearNetworksWidget()
        self.layout.addWidget(self.gearNetworksWidget, 1, 0)
        self.gearNetworksWidget.setVisible(True)

        self.gearNetworkDict = {}

        self.buildUI()
        self.populate()
        self.parent().layout().addWidget(self)
        if not dock: parent.show()

        self.previousGear = None

    def populate(self): pass
    def buildUI(self): pass

    #  TODO : LIST ALL TRANSFORM IN A SINGLE TABLE TO BE FASTER?
    #  TODO: IF SELECTION IS THE SAME OBJECT, DONT POPULATE....

    def selectCallback(*args):

        # -- setting original shader for colored gears --
        if args[0].previousGear:
            for n in args[0].previousGear.listNeigbours():
                n.restorShader()
        selected = pm.selected()
        if len(selected) == 1:
            gear = args[0].getGearFromTransform(selected[0])
            # -- if gear selected. --
            if gear:
                args[0].displayGear(True, gear)
                args[0].previousGear = gear
                return
            rod = args[0].getRodFromTransform(selected[0])
            if rod : 
                args[0].displayRod(True, rod)
                args[0].previousGear = gear
                return
        # -- if no gear selected. --
        args[0].displayGN(True)

    def getGearFromTransform(self, objTransform):
        for network in self.gearNetworkDict.keys():
            gear = network.getGearFromTransform(objTransform)
            if gear: return gear
        return None

    def getRodFromTransform(self, objTransform):
        for network in self.gearNetworkDict.keys():
            rod = network.getRodFromTransform(objTransform)
            if rod: return rod
        return None

    def displayGear(self, bool, gear=None):
        if bool:
            self.gearWidget.populate(gear)
        self.gearWidget.setVisible(bool)
        self.gearNetworksWidget.setVisible(not bool)
        self.rodWidget.setVisible(not bool)

    def displayRod(self, bool, rod=None):
        if bool:
            self.rodWidget.populate(rod)
        self.rodWidget.setVisible(bool)
        self.gearNetworksWidget.setVisible(not bool)
        self.gearWidget.setVisible(not bool)

    def displayGN(self, bool):
        if bool: 
            self.gearNetworksWidget.populate()
        self.rodWidget.setVisible(not bool)
        self.gearWidget.setVisible(not bool)
        self.gearNetworksWidget.setVisible(bool)

    def addGearNetwork(*args):
        gearNetwork = gear_network.GearNetwork()
        gearChain = gearNetwork.addChain()

        gear = gearNetwork.addGear(
            gearChain, 
            radius=consts.DEFAULT_RADIUS, 
            gearOffset=consts.DEFAULT_GEAR_OFFESET, 
            linkedGear=None)

        args[0].gearNetworksWidget.addGearNetwork(gearNetwork)
        args[0].gearNetworkDict[gearNetwork] = "bijour"

        pm.select(clear=True)
        pm.select(gear.objTransform)
