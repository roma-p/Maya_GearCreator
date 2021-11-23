import logging
import importlib
import pymel.core as pm
#
from Maya_GearCreator.Qt import QtWidgets
#
from Maya_GearCreator import consts
from Maya_GearCreator import gear_network
from Maya_GearCreator.gui import gear_network_widget
from Maya_GearCreator.gui import base_widgets
from Maya_GearCreator.misc import py_helpers

importlib.reload(consts)
importlib.reload(gear_network)
importlib.reload(gear_network_widget)
importlib.reload(base_widgets)
importlib.reload(py_helpers)

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
        # ????????????????
        # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        # print(QtWidgets.QSizePolicy)
        # print(QtWidgets.QSizePolicy.Maximum)
        # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        # self.scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum)
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scrollArea, 1, 0)

        self.addNetworkButton = QtWidgets.QPushButton("Create Gear Network.")
        self.addNetworkButton.clicked.connect(self.createGearNetwork)
        self.layout.addWidget(self.addNetworkButton, 0, 0, 1, 1)

    def populate(self):
        base_widgets.ItemWidget.cleanByType("gearNetwork")
        for gn in self.gearNetworks:
            self.scrollLayout.addWidget(
                base_widgets.ItemWidget("gearNetwork", gn))

    def addGearNetworks(self, *gearNetworks):
        for gn in gearNetworks:
            self.gearNetworks.add(gn)

    def createGearNetwork(self):
        gearNetwork = gear_network.GearNetwork()
        gearChain = gearNetwork.addChain()

        gear = gearNetwork.addGear(
            gearChain,
            radius=consts.DEFAULT_RADIUS,
            gearOffset=consts.DEFAULT_GEAR_OFFESET,
            linkedGear=None)

        self.gearNetworks.add(gearNetwork)
        self.populate()

        pm.select(clear=True)
        pm.select(gear.objTransform)
