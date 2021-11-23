import logging
import importlib
#
from Maya_GearCreator.Qt import QtWidgets, QtCore, QtGui
#
from Maya_GearCreator import gear_network
from Maya_GearCreator.gui import base_widgets
from Maya_GearCreator.gui import gear_window
from Maya_GearCreator.gui import rod_window
from Maya_GearCreator.misc import color_shader
from Maya_GearCreator import consts
from Maya_GearCreator.misc import py_helpers

importlib.reload(gear_network)
importlib.reload(base_widgets)
importlib.reload(gear_window)
importlib.reload(rod_window)
importlib.reload(color_shader)
importlib.reload(consts)
importlib.reload(py_helpers)

log = logging.getLogger("GearCreatorUI")
log.setLevel(logging.DEBUG)


class GearChainsWidget(QtWidgets.QWidget):

    def __init__(self, gearNetwork):
        super(GearChainsWidget, self).__init__()
        self.gearNetwork = gearNetwork
        # self.gearChainDict = {}
        self.buildUI()
        # self.populate()

    def buildUI(self):

        self.layout = QtWidgets.QGridLayout(self)
        self.modifiableName = base_widgets.ModifiableName(None, None)
        self.layout.addWidget(self.modifiableName)

        self.scrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scrollArea)

    def populate(self):
        base_widgets.ItemWidget.cleanByType("gearChain")
        py_helpers.deleteSubWidgetByType(self, GearChainWidget)
        if self.gearNetwork:
            for gearChain in self.gearNetwork.chainManager:
                self.scrollLayout.addWidget(GearChainWidget(gearChain))
            self.modifiableName.set(self.gearNetwork.getName,
                                    self.gearNetwork.setName)

        # for gearChain in self.gearNetwork.chainManager:
        #     if gearChain not in self.gearChainDict.keys():
        #         widget = GearChainWidget(gearChain)
        #         self.layout.addWidget(widget)
        #         self.gearChainDict[gearChain] = widget
        #     self.gearChainDict[gearChain].populate()


class GearChainWidget(QtWidgets.QWidget):

    T_WIDTH_SLIDER_FACTOR = 100

    colorAutoShader = color_shader.ColorAutoShader()

    def __init__(self, gearChain):
        super(GearChainWidget, self).__init__()
        self.gearChain = gearChain
        self.buildUI()
        self.populate()

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)

        self.btNew = QtWidgets.QToolButton()
        self.layout.addWidget(self.btNew, 0, 0, 1, 1)

        # self.modifiableName = base_widgets.ModifiableName(None, None)

        self.gearChainName = base_widgets.ItemWidget("gearChain",
                                                     self.gearChain)

        # self.layout.addWidget(self.modifiableName, 0, 1, 1, 2)
        self.layout.addWidget(self.gearChainName, 0, 1, 1, 2)

        # TODO : chnge slider with EnhancedSlider

        def _getTWidth(): return self.gearChain.tWidth
        def _setTWidth(val): return self.gearChain.changeTWidth(val)

        self.tWidthSlider = base_widgets.EnhancedSlider(
            "Teeth Width",
            min=self.gearChain.calculateMinTWidth,
            max=self.gearChain.calculateMaxTWidth,
            step=0.05,
            getter=_getTWidth,
            setter=_setTWidth)
        self.layout.addWidget(self.tWidthSlider, 1, 1, 1, 2)

        def _getHeight(): return self.gearChain.height
        def _setHeight(val): self.gearChain.changeHeight(val)
        def _getMinHeight(): return self.gearChain.calculateMinMaxHeight()[0]
        def _getMaxHeight(): return self.gearChain.calculateMinMaxHeight()[1]

        self.heightslider = base_widgets.EnhancedSlider(
            "height",
            min=_getMinHeight,
            max=_getMaxHeight,
            step=0.05,
            getter=_getHeight,
            setter=_setHeight)
        self.layout.addWidget(self.heightslider, 2, 1, 1, 2)
        self.heightslider.setVisible(False)

    def populate(self):
        # self.modifiableName.set(self.gearChain.getName,
        #                         self.gearChain.setName)

        self.tWidthSlider.populate()
        self.heightslider.populate()
        if self.gearChain.listRod(): show = True
        else: show = False

        colorName, colorRGB, sg = next(self.colorAutoShader)
        pixmap = QtGui.QPixmap(15, 15)
        pixmap.fill(QtGui.QColor(*colorRGB))
        self.btNew.setIcon(QtGui.QIcon(pixmap))
        for g in self.gearChain.gearList:
            g.setTmpShader(sg)

        self.heightslider.setVisible(show)
        if show:
            # _min, _max = self.gearChain.calculateMinMaxHeight()
            # self.heightslider.changeMinMaxStep(min=_min, max=_max)
            self.heightslider.populate()
