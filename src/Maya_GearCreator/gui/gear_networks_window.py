import logging
import importlib
#
from Maya_GearCreator.Qt import QtWidgets
#
from Maya_GearCreator.gui import gear_network_widget

importlib.reload(gear_network_widget)

log = logging.getLogger("gearWidget")
log.setLevel(logging.DEBUG)

class GearNetworksWidget(QtWidgets.QWidget):

    def __init__(self, *gearNetworks):
        super(GearNetworksWidget, self).__init__()
        self.gearNetworks = set(gearNetworks) or set()
        # self.gnWidgets = []
        self.buildUI()
        self.populate()

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scrollArea, 1, 0, 3, 5)

    def populate(self):
        for widget in self.findChildren(gear_network_widget.GearNetworkWidget):
            widget.delete()
        for gn in self.gearNetworks:
            self.scrollLayout.addWidget(
                gear_network_widget.GearNetworkWidget(gn))

    def addGearNetwork(self, gn):
        self.gearNetworks.add(gn)
