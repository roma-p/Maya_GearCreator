import logging
import importlib
from functools import partial
#
import pymel.core as pm
from Maya_GearCreator.Qt import QtWidgets, QtCore, QtGui
#
from Maya_GearCreator.gui import base_widgets
from Maya_GearCreator.misc import color_shader
from Maya_GearCreator import consts

importlib.reload(base_widgets)
importlib.reload(color_shader)
importlib.reload(consts)

log = logging.getLogger("gearWidget")
log.setLevel(logging.DEBUG)

# ON SELECT: afficher les contraintes circulaires des voisins.
# ON DESELECT: HIDE IT....


class GearWidget(QtWidgets.QWidget):

    RADIUS_SLIDER_FACTOR = 10

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

        for widgetType in (base_widgets.MoveAlongWidget, GearSubSectionWidget):
            for widget in self.findChildren(widgetType):
                widget.delete()

        self.gear = gear

        self.modifiableName.set(gear.name,
                                gear.setName)

        try : self.resizeSlider.valueChanged.disconnect()
        except Exception: pass
        sliderVal = GearWidget.convertRadiusToSlider(
            self.gear.radius)
        self.resizeSlider.setValue(sliderVal)
        self.resizeMode.setChecked(False)

        self.resizeSlider.valueChanged.connect(
            partial(GearWidget.changeRadiusCallback, gearWidget=self))

        try : self.addGear.clicked.disconnect()
        except Exception: pass
        self.addGear.clicked.connect(partial(GearWidget.addGear, self))

        # Calculation of max Radius shall be done at populate since radius could change.
        i = 3

        for sectionId in gear.GUI_ATTRIBUTES.keys():
            self.layout.addWidget(GearSubSectionWidget(self.gear, sectionId), 
                                  i, 0)
            i = i + 1

        for neighbour in self.gear.listNeigbours():
            colorName, colorRGB, sg = next(self.colorAutoShader)
            neighbour.setTmpShader(sg)
            widget = base_widgets.MoveAlongWidget(self.gear, neighbour,
                                                  colorRGB)
            self.layout.addWidget(widget, i, 0)
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
            gearChain, 
            radius=consts.DEFAULT_RADIUS, 
            gearOffset=consts.DEFAULT_GEAR_OFFESET, 
            linkedGear=gear)

        pm.select(clear=True)
        pm.select(gear.objTransform)


class GearSubSectionWidget(QtWidgets.QWidget):

    def __init__(self, gear, sectionId):

        self.gear = gear
        self.sectionId = sectionId
        self.sliders = []
        super(GearSubSectionWidget, self).__init__()
        self.buildUI()

    def buildUI(self):

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(QtWidgets.QLabel(self.sectionId), 0, 0)

        i = 1
        for name, data in self.gear.GUI_ATTRIBUTES[self.sectionId].items():
            if len(data) == 3:
                min, max, step = data
                numberEditMax = None
            elif len(data) == 4:
                min, max, step, numberEditMax = data
            else:
                log.error("wrong data for GUI ATTRIBUTES")
                return

            gearSlider = base_widgets.GearSlider(
                self.gear, name,
                min, max, step,
                numberEditMax)
            self.layout.addWidget(gearSlider, i, 0)
            self.sliders.append(gearSlider)
            i = i + 1

    def populate(self):
        for slider in self.sliders:
            slider.populate()

    def delete(self):  # TODO: why not __del__
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()
