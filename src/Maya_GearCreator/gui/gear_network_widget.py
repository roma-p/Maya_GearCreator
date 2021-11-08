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
from Maya_GearCreator import consts

importlib.reload(gear_network)
importlib.reload(base_widgets)
importlib.reload(gear_window)
importlib.reload(rod_window)
importlib.reload(consts)

log = logging.getLogger("GearCreatorUI")
log.setLevel(logging.DEBUG)


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

    def delete(self):  # TODO: why not __del__
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

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
        self.slider.setValue(self.gearChain.tWidth
            * self.T_WIDTH_SLIDER_FACTOR)
        self.slider.setMinimum(self.gearChain.calculateMinTWidth()
            * self.T_WIDTH_SLIDER_FACTOR)
        self.slider.setMaximum(self.gearChain.calculateMaxTWidth()
            * self.T_WIDTH_SLIDER_FACTOR)
