from functools import partial
import logging
import os
import json
import time
import pymel.core as pm
from maya import OpenMayaUI as omui
from maya import OpenMaya as om
from Qt import QtWidgets, QtCore, QtGui
from functools import partial
import Qt
import importlib

# -> WIDGET GENERIQUE: SLIDER / VALUE. 
# -> AC SETTER MAX VALUE / MIN VALUE. 
# -> EXTRNSIBLE pr MOVE ALONG WIDGET (color) et REZISE. 
# -> WIDGET SCROLL AREA? 

logging.basicConfig()
log = logging.getLogger("GearCreatorUI")
log.setLevel(logging.DEBUG)

import gearCreator.gearCreator_test3 as gearCreator
importlib.reload(gearCreator)
# RESOLVING IMPORT -------------------------------------------------------------

# importing wrapInstance, Signal
binding_version = Qt.__binding_version__
if binding_version == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal 
    log.debug("Using PySide with shiboken")
elif binding_version.startswith("PyQt"):
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
    log.debug("Using PyQt with sip")
else: 
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal 
    log.debug("Using PySide2 with shiboken")

# HELPERS ----------------------------------------------------------------------

def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(int(win), QtWidgets.QMainWindow) #???
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

# MAIN UI ----------------------------------------------------------------------

class GearCreatorUI(QtWidgets.QWidget):

    def __init__(self, dock=True):

        if dock: 
            parent = getDock()
        else: 
            deleteDock()
            try : 
                pm.deleteUI("GearCreatorUI")
            except : 
                log.debug("No previous UI exists")

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName("GearCreatorUI")
            parent.setWindowTitle("Gear Creator")
            layout = QtWidgets.QVBoxLayout(parent) #???, useless?

            self.selectionCallbackIdx = om.MEventMessage.addEventCallback(
                "SelectionChanged", partial(GearCreatorUI.selectCallback, self))

            def closeEvent(QWidget):
                if self.selectionCallbackIdx != None:
                    om.MMessage.removeCallback(self.selectionCallbackIdx)
                    self.selectionCallbackIdx = None
                #event.accept()
            parent.closeEvent = closeEvent

        super(GearCreatorUI, self).__init__(parent)

        self.gearWidget = GearWidget()
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.gearWidget, 1, 0)
        self.gearWidget.setVisible(False)

        self.newGearNetwork = QtWidgets.QPushButton("new gear network")
        self.layout.addWidget(self.newGearNetwork, 0, 0)
        self.newGearNetwork.clicked.connect(partial(GearCreatorUI.addGearNetwork, 
                                                    self))

        self.gearNetworkDict = {}

        #self.gearNetworkArea = QtWidgets.QScrollArea()
        #scrollArea.setWidgetResizable(True)
        

        self.buildUI()
        self.populate()
        self.parent().layout().addWidget(self)
        if not dock: parent.show()
        #self.show()

    def populate(self): pass
    def buildUI(self): pass

    #  TODO : HIDE IF THE SELECTION IS NOT FROM US.
    #  TODO : LIST ALL TRANSFORM IN A SINGLE TABLE TO BE FASTER? 
    def selectCallback(*args):
        selected = pm.selected()
        if len(selected) == 1 :
            gear = args[0].getGearFromTransform(selected[0])
            if gear: args[0].displayGear(gear)

    def getGearFromTransform(self, gearTransform):
        for network in self.gearNetworkDict.keys():
            gear = network.getGearFromTransform(gearTransform)
            if gear: return gear
        return None

    def displayGear(self, gear):
        self.gearWidget.populate(gear)
        self.gearWidget.setVisible(True)

    def addGearNetwork(*args):
        gearNetwork = gearCreator.GearNetwork()
        gearChain = gearNetwork.addChain()

        gear = gearNetwork.addGear(
            radius=GearWidget.DEFAULT_RADIUS, 
            gearChain=gearChain, 
            tLen=GearWidget.DEFAULT_TLEN, 
            linkedGear=None)
        args[0].gearNetworkDict[gearNetwork] = gear

        pm.select(clear=True)
        pm.select(gear.gearTransform)

# ON DESOLECT: HIDE WIDGET, RECOLOR EVERYTHING
# COLORISE TOUS LES VOISINS AC UNE COULEUR DIFF. 
# UN SLIDER MOVE ALONG POUR CHAQUE COULEUR. 
# ON SELECT: afficher les contraintes circulaires des voisins. 
# ON DESELECT: HIDE IT....

# GEAR SUB MENU  ---------------------------------------------------------------

class GearWidget(QtWidgets.QWidget):

    RADIUS_SLIDER_FACTOR = 10
    DEFAULT_RADIUS = 1
    DEFAULT_TLEN   = 0.3

    def __init__(self):
        super(GearWidget, self).__init__()
        self.buildUI()
        self.gear = None

    def convertRadiusToSlider(radius):
        return radius * GearWidget.RADIUS_SLIDER_FACTOR

    def convertSliderToFactor(sliderValue):
        return sliderValue / GearWidget.RADIUS_SLIDER_FACTOR

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)

        # NAME -----------------------------------------------------------------
        self.modifiableName = ModifiableName("", None)
        self.layout.addWidget(self.modifiableName, 0, 0, 1, 2)

        # Resize -----------------------------------------------------------------

        self.resizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.resizeSlider.setMinimum(GearWidget.convertRadiusToSlider(0.5))
        self.resizeSlider.setMaximum(GearWidget.convertRadiusToSlider(15))

        self.layout.addWidget(self.resizeSlider, 1, 0, 1, 2)

        self.resizeMode = QtWidgets.QCheckBox("resize neighbours")
        self.layout.addWidget(self.resizeMode, 1, 2)

        self.addGear = QtWidgets.QPushButton("Add Gear")
        self.layout.addWidget(self.addGear, 2, 0)

    def populate(self, gear):

        for widget in self.findChildren(MoveAlongWidget):
            widget.delete()

        self.gear = gear

        self.modifiableName.set(gear.name, 
                                gear.setName)

        try : self.resizeSlider.valueChanged.disconnect()
        except Exception: pass
        sliderVal = GearWidget.convertRadiusToSlider(
            self.gear.gearConstructor.radius.get())
        self.resizeSlider.setValue(sliderVal)
        self.resizeMode.setChecked(False)

        self.resizeSlider.valueChanged.connect(
            partial(GearWidget.changeRadiusCallback,gearWidget=self))

        try : self.addGear.clicked.disconnect()
        except Exception: pass
        self.addGear.clicked.connect(partial(GearWidget.addGear, self))

        # Calculation of max Radius shall be done at populate since radius could change.
        i = 3
        for neighbour in self.gear.neighbours: 
            widget = MoveAlongWidget(self.gear, neighbour)
            self.layout.addWidget(widget,i, 0)
            i = i+1

    def changeRadiusCallback(value, gearWidget=None):
        resizeNeighbour = bool(gearWidget.resizeMode.isChecked())
        radius = GearWidget.convertSliderToFactor(value)
        gearWidget.gear.changeRadius(radius, resizeNeighbour)

    def addGear(gearWidget=None):
        
        gear = gearWidget.gear
        gearChain = gear.gearChain
        gearNetwork = gearChain.gearNetwork

        gear = gearNetwork.addGear(
            radius=GearWidget.DEFAULT_RADIUS, 
            gearChain=gearChain, 
            tLen=GearWidget.DEFAULT_TLEN, 
            linkedGear=gear)

        pm.select(clear=True)
        pm.select(gear.gearTransform)

class MoveAlongWidget(QtWidgets.QWidget):

    def __init__(self, gearToMove, gearToMoveAlong):
        super(MoveAlongWidget, self).__init__()
        self.gearToMove = gearToMove
        self.gearToMoveAlong = gearToMoveAlong
        self.buildUI()
        self.populate()

    def delete(self): # why not __del__
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

    def buildUI(self) : 
        layout = QtWidgets.QHBoxLayout(self)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        layout.addWidget(self.slider)

    def populate(self):

        self.slider.setMaximum(self.gearToMoveAlong.calculateMoveAlong())

        self.slider.sliderPressed.connect(
            lambda : self.gearToMove.activateMoveMode(self.gearToMoveAlong))
        self.slider.sliderReleased.connect(
            lambda : self.gearToMove.desactivateMoveMode())
        self.slider.valueChanged.connect(
            lambda value : self.gearToMove.moveAlong(value))

# GEAR NETWORK SUB MENU  ------------------------------------------------------- 

class GearNetworkWidget(QtWidgets.QWidget):

    def __init__(self, gearNetwork):
        super(GearNetworkWidget, self).__init__()
        self.gearNetwork = gearNetwork
        self.buildUI()
        self.populate()

        self.gearChainDict = {}

    def buildUI(self):

        self.layout = QtWidgets.QGridLayout(self)

        self.modifiableName = ModifiableName("", None)
        self.layout.addWidget(self.modifiableName, 0, 0, 1, 2)        

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(scrollWidget)
        self.layout.addWidget(self.scrollArea, 0,2)

    def populate(self):

        self.modifiableName.set(gearNetwork.name, 
                                gearNetwork.setName)

        for gearChain in self.gearNetwork.chainList: 
            if not self.gearChainDict[gearChain]:
                widget = GearChainWidget(gearChain)
                self.scrollArea.addWidget(widget)
                self.gearChainDict[gearChain] = widget
            self.gearChainDict[gearChain].populate()

class GearChainWidget(QtWidgets.QWidget):

    def __init__(self, gearChain):
        super(GearChainWidget, self).__init__()
        self.gearChain = gearChain
        self.buildUI()
        self.populate()

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)
        
        self.modifiableName = ModifiableName("", None)
        self.layout.addWidget(self.modifiableName, 0, 0, 1, 2)

        # ADD : SET SOLO. 

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1)
        self.slider.valueChanged.connect(
            lambda value : self.gearChain.changeTWidth(value))
        self.layout.addWidget(self.slider, 1, 1,)

    def populate():
        self.modifiableName.set(gearChain.name, 
                                gearChain.setName)
        self.slider.setMinimum(self.gearChain.calculateMinTWidth())
        self.slider.setMaximum(self.gearChain.calculateMaxTWidth())

# BASE WIDGET ------------------------------------------------------------------

class ModifiableName(QtWidgets.QWidget):
    def __init__(self, name, func):
        super(ModifiableName, self).__init__()
        self.name = name
        self.func = func
        self.buildUI()
        self.populate()

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)

        # normal text
        self.nameButton = QtWidgets.QPushButton("caca")
        self.nameButton.setFlat(True)
        self.nameButton.clicked.connect(self._editName)
        self.layout.addWidget(self.nameButton, 0, 1, 0, 3)
        # ?? self.nameButton.setAutoFillBackground()

        self.nameEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.nameEdit, 0, 1)
        self.nameSave = QtWidgets.QPushButton("Save")
        self.layout.addWidget(self.nameSave, 0, 3, 0, 1)
        self.nameSave.clicked.connect(
            lambda value : self._saveNewName(value))

        self._showEditable(False)

    def populate(self):
        self.nameButton.setText(self.name)

    def set(self, name, func):
        try : self.nameSave.clicked.disconnect()
        except Exception: pass

        self.name = name
        self.func = func
        self.populate()

        self.nameSave.clicked.connect(self._saveNewName)

    def _saveNewName(self, value):
        self.name = self.nameEdit.text()
        self.func(self.name)
        self.nameButton.setText(self.name)
        self.nameEdit.setText(self.name)
        self._showEditable(False)

    def _editName(self, value):
        self.nameEdit.setText(self.name)
        self._showEditable(True)

    def _showEditable(self, bool):
        self.nameEdit.setVisible(bool)
        self.nameSave.setVisible(bool)
        self.nameButton.setVisible(not bool)
