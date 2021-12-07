import logging
import importlib
import collections
from functools import partial
#
import pymel.core as pm
from maya import OpenMayaUI as omui
from maya import OpenMaya as om
#
from Maya_GearCreator.Qt import QtWidgets
from Maya_GearCreator import Qt
#
from Maya_GearCreator import consts
from Maya_GearCreator import rod
from Maya_GearCreator import gear_network
from Maya_GearCreator.misc import maya_helpers
from Maya_GearCreator.misc import py_helpers
from Maya_GearCreator.gui import base_widgets
from Maya_GearCreator.gui import gear_window
from Maya_GearCreator.gui import rod_window
from Maya_GearCreator.gui import gear_networks_window
from Maya_GearCreator.gui import gear_chains_window

importlib.reload(consts)
importlib.reload(rod)
importlib.reload(gear_network)
importlib.reload(base_widgets)
importlib.reload(gear_window)
importlib.reload(rod_window)
importlib.reload(gear_networks_window)
importlib.reload(maya_helpers)
importlib.reload(py_helpers)
importlib.reload(gear_chains_window)

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

        super(GearCreatorUI, self).__init__(parent)

        self.layout = QtWidgets.QGridLayout(self)

        self.selectionCallbackIdx = om.MEventMessage.addEventCallback(
            "SelectionChanged", self.selectCallback)

        def closeEvent(QWidget):
            if self.selectionCallbackIdx is not None:
                om.MMessage.removeCallback(self.selectionCallbackIdx)
                self.selectionCallbackIdx = None
            self.restoreShader()
        parent.closeEvent = closeEvent
        # TODO : backup shader.

        self.parent().layout().addWidget(self)
        if not dock:
            parent.show()

        self.gearToRestore = []
        self.currentItemPage = None
        self.currentItem = None

        self.buildUI()
        self.populate()

    def buildUI(self):

        pluginLabel = QtWidgets.QLabel("Gear Creator V1")
        self.layout.addWidget(pluginLabel, 0, 0)

        self.homeButton = QtWidgets.QPushButton("Home")
        self.layout.addWidget(self.homeButton, 0, 1)
        self.homeButton.clicked.connect(self.homeClicked)

        self.gearChains = QtWidgets.QPushButton("Gear Chains")
        self.layout.addWidget(self.gearChains, 0, 2)
        self.gearChains.setVisible(False)
        self.gearChains.clicked.connect(self.gearChainsPageClicked)

        self.currentItemButton = QtWidgets.QPushButton("caca")
        self.layout.addWidget(self.currentItemButton, 0, 3)
        self.currentItemButton.setVisible(False)
        self.currentItemButton.clicked.connect(self.gearPageClicked)

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.layout.addWidget(self.stackedWidget, 1, 0, 1, 3)

        self.networksPage = gear_networks_window.GearNetworksWidget()
        self.stackedWidget.addWidget(self.networksPage)

        self.gearPage = gear_window.GearWidget()
        self.stackedWidget.addWidget(self.gearPage)

        self.rodPage = rod_window.RodWidget()
        self.stackedWidget.addWidget(self.rodPage)

        self.gearChainsPage = gear_chains_window.GearChainsWidget(None)
        self.stackedWidget.addWidget(self.gearChainsPage)

        self.stackedWidget.setCurrentWidget(self.networksPage)

    def populate(self):
        self.networksPage.populate()

    def addExistingGearNetwork(self, *gearNetworks):
        self.networksPage.addGearNetworks(*gearNetworks)
        self.populate()

    def selectCallback(self, *args):

        self.restoreShader()
        selected = pm.selected()
        if len(selected) == 1 and py_helpers.hashable(selected[0]):
            # -- is gear selected? --
            g = self.getGearFromTransform(selected[0])
            if g:
                self.gearItemSelected(g, "gear")
                self.setGearsToRestore()
                return
            # -- is rod selected? --
            r = self.getRodFromTransform(selected[0])
            if r:
                self.gearItemSelected(r, "rod")
                self.setGearsToRestore()
                return
        # -- if neihter gear nor rod selected. --
        self.currentItemPage = None
        self.currentItem = None
        self.homeClicked()

    def gearItemSelected(self, objDescriptor, objType):
        self.currentItem = objDescriptor
        self.currentItemButton.setText(objType)
        self.gearChains.setVisible(True)
        self.currentItemButton.setVisible(True)

        if objType == "gear":
            self.gearChainsPage.gearNetwork = objDescriptor.gearChain.gearNetwork
        elif objType == "rod":
            self.gearChainsPage.gearNetwork = objDescriptor.gearNetwork
        page = {
            "gear": self.gearPage,
            "rod": self.rodPage
        }[objType]
        self.stackedWidget.setCurrentWidget(page)
        page.populate(objDescriptor)
        self.currentItemPage = page

    def homeClicked(self):
        self.restoreShader()
        if not self.currentItemPage:
            self.gearChains.setVisible(False)
            self.currentItemButton.setVisible(False)
        self.stackedWidget.setCurrentWidget(self.networksPage)

    def gearPageClicked(self):
        self.restoreShader()
        self.setGearsToRestore()
        self.stackedWidget.setCurrentWidget(self.currentItemPage)

    def gearChainsPageClicked(self):
        self.restoreShader()
        self.setGearsToRestore(allNetwork=True)
        self.gearChainsPage.populate()
        self.stackedWidget.setCurrentWidget(self.gearChainsPage)

    def getGearFromTransform(self, objTransform):
        for network in self.networksPage.gearNetworks:
            gear = network.getGearFromTransform(objTransform)
            if gear:
                return gear
        return None

    def getRodFromTransform(self, objTransform):
        for network in self.networksPage.gearNetworks:
            rod = network.getRodFromTransform(objTransform)
            if rod:
                return rod
        return None

    def restoreShader(self):
        if self.gearToRestore:
            for g in self.gearToRestore:
                g.restorShader()

    def setGearsToRestore(self, allNetwork=False):
        if not self.currentItem:
            return
        elif isinstance(self.currentItem, rod.Rod):
            if allNetwork:
                self.gearToRestore = self.currentItem.gearNetwork.listGears()
        # else : is gear.
        else:
            if allNetwork:
                gearNetwork = self.currentItem.gearChain.gearNetwork
                self.gearToRestore = gearNetwork.listGears()
            else:
                self.gearToRestore = self.currentItem.listNeigbours()
