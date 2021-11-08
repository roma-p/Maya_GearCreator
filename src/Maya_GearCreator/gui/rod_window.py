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

class RodWidget(QtWidgets.QWidget):

    def __init__(self):
        super(RodWidget, self).__init__()
        self.buildUI()
        self.rod = None


    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.modifiableName = base_widgets.ModifiableName("", None)
        self.layout.addWidget(self.modifiableName, 0, 0, 1, 2)

        self.addGearBtn = QtWidgets.QPushButton("Add Gear")
        self.layout.addWidget(self.addGearBtn, 2, 0)

    def populate(self, rod):

        self.rod = rod
        self.modifiableName.set(rod.name,
                                rod.setName)

        try : self.addGearBtn.clicked.disconnect()
        except Exception: pass
        self.addGearBtn.clicked.connect(lambda: self.addGear())

    def addGear(self):
        rod = self.rod
        gearNetwork = rod.gearNetwork
        chain = gearNetwork.addChain(rod=rod)
        gear  = gearNetwork.addGearOnRod(rod, chain)
        pm.select(clear=True)
        pm.select(gear.objTransform)


