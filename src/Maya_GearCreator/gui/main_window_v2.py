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
from Maya_GearCreator import gear_network
from Maya_GearCreator.gui import base_widgets
from Maya_GearCreator.gui import gear_window
from Maya_GearCreator.gui import rod_window
from Maya_GearCreator.gui import gear_networks_window
from Maya_GearCreator.gui import gear_networks_window_v2
from Maya_GearCreator import consts
from Maya_GearCreator.misc import maya_helpers
from Maya_GearCreator.misc import py_helpers

importlib.reload(gear_network)
importlib.reload(base_widgets)
importlib.reload(gear_window)
importlib.reload(rod_window)
importlib.reload(consts)
importlib.reload(gear_networks_window)
importlib.reload(gear_networks_window_v2)
importlib.reload(maya_helpers)
importlib.reload(py_helpers)

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
        parent.closeEvent = closeEvent

        self.parent().layout().addWidget(self)
        if not dock:
            parent.show()

        self.gearTorestore = []
        self.currentItemPage = None

        self.buildUI()
        self.populate()

    def buildUI(self):

        pluginLabel = QtWidgets.QLabel("Gear Creator V1")
        self.layout.addWidget(pluginLabel, 0, 0)

        self.homeButton = QtWidgets.QPushButton("Home")
        self.layout.addWidget(self.homeButton, 0, 1)
        self.homeButton.clicked.connect(self.home)

        self.networkButton = QtWidgets.QPushButton("Gear Network")
        self.layout.addWidget(self.networkButton, 0, 2)
        self.networkButton.setVisible(False)

        self.currentItemButton = QtWidgets.QPushButton("caca")
        self.layout.addWidget(self.currentItemButton, 0, 3)
        self.currentItemButton.setVisible(False)
        self.currentItemButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.currentItemPage))

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.layout.addWidget(self.stackedWidget, 1, 0, 1, 3)

        self.networksPage = gear_networks_window_v2.GearNetworksWidget()
        self.stackedWidget.addWidget(self.networksPage)

        self.gearPage = gear_window.GearWidget()
        self.stackedWidget.addWidget(self.gearPage)

        self.rodPage = rod_window.RodWidget()
        self.stackedWidget.addWidget(self.rodPage)

        self.stackedWidget.setCurrentWidget(self.networksPage)

    def populate(self):
        self.networksPage.populate()

    def addExistingGearNetwork(self, *gearNetworks):
        self.networksPage.addGearNetworks(*gearNetworks)
        self.populate()

    def selectCallback(self, *args):
        if self.gearTorestore:
            for g in self.gearTorestore:
                g.restorShader()

        selected = pm.selected()
        if len(selected) == 1 and py_helpers.hashable(selected[0]):
            gear = self.getGearFromTransform(selected[0])
            # -- if gear selected. --
            if gear:
                self.gearTorestore += gear.listNeigbours()
                self.gearItemSelected(gear, "gear")
                return
            r = self.getRodFromTransform(selected[0])
            if r:
                self.gearItemSelected(r, "rod")
                return
        # -- if no gear selected. --
        self.currentItemPage = None
        self.home()

    def gearItemSelected(self, objDescriptor, objType):
        self.currentItemButton.setText(objType)
        self.networkButton.setVisible(True)
        self.currentItemButton.setVisible(True)
        page = {
            "gear": self.gearPage,
            "rod": self.rodPage
        }[objType]
        self.stackedWidget.setCurrentWidget(page)
        page.populate(objDescriptor)
        self.currentItemPage = page

    def home(self):
        if not self.currentItemPage:
            self.networkButton.setVisible(False)
            self.currentItemButton.setVisible(False)
        self.stackedWidget.setCurrentWidget(self.networksPage)

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
