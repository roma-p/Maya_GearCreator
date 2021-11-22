import logging
import importlib
#
import pymel.core as pm
from Maya_GearCreator.Qt import QtWidgets
#
from Maya_GearCreator.gui import base_widgets
from Maya_GearCreator.misc import color_shader
from Maya_GearCreator import consts
from Maya_GearCreator.misc import py_helpers

importlib.reload(base_widgets)
importlib.reload(color_shader)
importlib.reload(consts)
importlib.reload(py_helpers)

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
        self.modifiableName = base_widgets.ModifiableName(None, None)
        self.layout.addWidget(self.modifiableName, 0, 0, 1, 2)


        self.addGearBtn = QtWidgets.QPushButton("Add Gear")
        self.layout.addWidget(self.addGearBtn, 4, 0)

    def populate(self, rod):

        self.rod = rod
        self.modifiableName.set(rod.getName,
                                rod.setName)

        def _getRadius(): return self.rod.radius
        def _setRadius(val): self.rod.changeRadius(val)

        py_helpers.deleteSubWidgetByType(self, base_widgets.EnhancedSlider)

        self.radiusSlider = base_widgets.EnhancedSlider(
            "radius",
            min=0.1,
            max=self.rod.getMaxRadius(),
            step=0.005,
            getter=_getRadius,
            setter=_setRadius)
        self.layout.addWidget(self.radiusSlider, 1, 0)
        self.radiusSlider.populate()

        def _getTop(): return self.rod.getLen(top=True)
        def _setTop(val): self.rod.changeLen(val, top=True)
        def _getTopMin(): return self.rod.getMinMaxTop()[0]
        def _getTopMax(): return self.rod.getMinMaxTop()[1]


        # create slider.
        self.topSlider = base_widgets.EnhancedSlider(
            "top",
            min=_getTopMin,
            max=_getTopMax,
            step=0.05,
            getter=_getTop,
            setter=_setTop)
        self.layout.addWidget(self.topSlider, 2, 0)

        def _getBot(): return - self.rod.getLen(top=False)
        def _setBot(val): self.rod.changeLen(val, top=False)
        def _getBotMin(): return self.rod.getMinMaxBot()[0]
        def _getBotMax(): return self.rod.getMinMaxBot()[1]

        # create other slider.
        self.botSlider = base_widgets.EnhancedSlider(
            "bot",
            min=_getBotMin,
            max=_getBotMax,
            step=0.05,
            getter=_getBot,
            setter=_setBot)
        self.layout.addWidget(self.botSlider, 3, 0)

        try : self.addGearBtn.clicked.disconnect()
        except Exception: pass
        self.addGearBtn.clicked.connect(lambda: self.addGear())

    def addGear(self):
        rod = self.rod
        gearNetwork = rod.gearNetwork
        chain = gearNetwork.addChain()
        gear = gearNetwork.addGearOnRod(rod, chain)
        pm.select(clear=True)
        pm.select(gear.objTransform)
