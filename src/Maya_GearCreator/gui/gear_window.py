import logging
import importlib
from functools import partial
#
import pymel.core as pm
from Maya_GearCreator.Qt import QtWidgets, QtCore, QtGui
#
from Maya_GearCreator.gui import base_widgets
importlib.reload(base_widgets)

from Maya_GearCreator.misc import color_shader
importlib.reload(color_shader)

log = logging.getLogger("gearWidget")
log.setLevel(logging.DEBUG)

# ON SELECT: afficher les contraintes circulaires des voisins.
# ON DESELECT: HIDE IT....


class GearWidget(QtWidgets.QWidget):

    RADIUS_SLIDER_FACTOR = 10
    DEFAULT_RADIUS = 1
    DEFAULT_TLEN = 0.3

    colorAutoShader = color_shader.ColorAutoShader()

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

        # NAME ----------------------------------------------------------------
        self.modifiableName = base_widgets.ModifiableName("", None)
        self.layout.addWidget(self.modifiableName, 0, 0, 1, 2)

        # Resize --------------------------------------------------------------

        self.resizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.resizeSlider.setMinimum(GearWidget.convertRadiusToSlider(0.5))
        self.resizeSlider.setMaximum(GearWidget.convertRadiusToSlider(15))

        self.layout.addWidget(self.resizeSlider, 1, 0, 1, 2)

        self.resizeMode = QtWidgets.QCheckBox("resize neighbours")
        self.layout.addWidget(self.resizeMode, 1, 2)

        self.addGear = QtWidgets.QPushButton("Add Gear")
        self.layout.addWidget(self.addGear, 2, 0)

    def populate(self, gear):

        for widget in self.findChildren(base_widgets.MoveAlongWidget):
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
            partial(GearWidget.changeRadiusCallback, gearWidget=self))

        try : self.addGear.clicked.disconnect()
        except Exception: pass
        self.addGear.clicked.connect(partial(GearWidget.addGear, self))

        # Calculation of max Radius shall be done at populate since radius could change.
        i = 3
        for neighbour in self.gear.neighbours:
            colorName, colorRGB, sg = next(self.colorAutoShader)
            neighbour.setTmpShader(sg)
            widget = base_widgets.MoveAlongWidget(self.gear, neighbour,
                                                  colorRGB)
            self.layout.addWidget(widget, i, 0,)
            i = i + 1

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
