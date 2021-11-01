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
from Maya_GearCreator.gui import base_widgets
importlib.reload(base_widgets)
from Maya_GearCreator import gear_network
importlib.reload(gear_network)
from Maya_GearCreator.gui import gear_window
importlib.reload(gear_window)

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

        self.gearWidget = gear_window.GearWidget()
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.gearWidget, 1, 0)
        self.gearWidget.setVisible(False)

        self.newGearNetwork = QtWidgets.QPushButton("new gear network")
        self.layout.addWidget(self.newGearNetwork, 0, 0)
        self.newGearNetwork.clicked.connect(
            partial(GearCreatorUI.addGearNetwork, self))

        self.gearNetworkDict = {}

        self.scrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scrollArea, 1, 0, 1, 3)

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
            for n in args[0].previousGear.neighbours:
                n.restorShader()
        selected = pm.selected()
        if len(selected) == 1:
            gear = args[0].getGearFromTransform(selected[0])
            # -- if gear selected. --
            if gear:
                args[0].displayGear(True, gear)
                args[0].previousGear = gear
                return
        # -- if no gear selected. --
        args[0].displayGear(False)

    def getGearFromTransform(self, gearTransform):
        for network in self.gearNetworkDict.keys():
            gear = network.getGearFromTransform(gearTransform)
            if gear: return gear
        return None

    def displayGear(self, bool, gear=None):
        if bool:
            self.gearWidget.populate(gear)
        self.gearWidget.setVisible(bool)
        self.scrollArea.setVisible(not bool)

    def addGearNetwork(*args):
        gearNetwork = gear_network.GearNetwork()
        gearChain = gearNetwork.addChain()

        gear = gearNetwork.addGear(
            radius=gear_window.GearWidget.DEFAULT_RADIUS,
            gearChain=gearChain,
            tLen=gear_window.GearWidget.DEFAULT_TLEN,
            linkedGear=None)
        gearNetworkWidget = GearNetworkWidget(gearNetwork)
        args[0].gearNetworkDict[gearNetwork] = gearNetworkWidget
        args[0].scrollLayout.addWidget(gearNetworkWidget)

        pm.select(clear=True)
        pm.select(gear.gearTransform)

class GearNetworkWidget(QtWidgets.QWidget):

    def __init__(self, gearNetwork):
        super(GearNetworkWidget, self).__init__()
        self.gearNetwork = gearNetwork
        self.gearChainDict = {}
        self.buildUI()
        self.populate()

    def buildUI(self):

        self.layout = QtWidgets.QVBoxLayout(self)
        self.modifiableName = base_widgets.ModifiableName("", None)
        self.layout.addWidget(self.modifiableName)

    def populate(self):

        self.modifiableName.set(self.gearNetwork.name,
                                self.gearNetwork.setName)

        for gearChain in self.gearNetwork.chainList:
            if gearChain not in self.gearChainDict.keys():
                widget = GearChainWidget(gearChain)
                self.layout.addWidget(widget)
                self.gearChainDict[gearChain] = widget
            self.gearChainDict[gearChain].populate()

class GearChainWidget(QtWidgets.QWidget):

    T_WIDTH_SLIDER_FACTOR = 100

    def __init__(self, gearChain):
        super(GearChainWidget, self).__init__()
        self.gearChain = gearChain
        self.buildUI()
        self.populate()

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)

        self.modifiableName = base_widgets.ModifiableName("", None)
        self.layout.addWidget(self.modifiableName, 0, 0, 1, 2)

        # ADD : SET SOLO.

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1)
        self.slider.valueChanged.connect(
            lambda value: self.gearChain.changeTWidth(
                value / self.T_WIDTH_SLIDER_FACTOR))
        self.layout.addWidget(self.slider, 1, 1,)

    def populate(self):
        self.modifiableName.set(self.gearChain.name,
                                self.gearChain.setName)
        self.slider.setMinimum(self.gearChain.calculateMinTWidth()
            * self.T_WIDTH_SLIDER_FACTOR)
        self.slider.setMaximum(self.gearChain.calculateMaxTWidth()
            * self.T_WIDTH_SLIDER_FACTOR)
