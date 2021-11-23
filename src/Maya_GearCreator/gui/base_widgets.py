import logging
import numbers
import importlib
from collections import defaultdict

from Maya_GearCreator.Qt import QtWidgets, QtCore, QtGui
from Maya_GearCreator.misc import py_helpers

importlib.reload(py_helpers)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# TODO : BACKUP NAME!
# IF NAME EMPTY -> cancel
# IF TRANSFORM WITH THIS NAME ALREADY EXISTS SAME.
# HOOVER.

class ModifiableName(QtWidgets.QWidget):

    def __init__(self, getter, setter):
        super(ModifiableName, self).__init__()

        self.getter = getter
        self.setter = setter

        self.buildUI()
        self.populate()

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)

        # normal text
        self.nameButton = QtWidgets.QPushButton("caca")
        self.nameButton.setFlat(True)
        self.nameButton.clicked.connect(self._editName)
        self.layout.addWidget(self.nameButton, 0, 1, 0, 3)

        self.nameEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.nameEdit, 0, 1)
        self.nameEdit.returnPressed.connect(self._saveNewName)

        self._showEditable(False)

    def populate(self):
        if self.getter:
            txt = self.getter()
        else:
            txt = "default"
        self.nameButton.setText(txt)

    def set(self, getter, setter):

        py_helpers.disconnectSignals(self.nameEdit.returnPressed)

        self.setter = setter
        self.getter = getter
        self.populate()
        self.nameEdit.returnPressed.connect(self._saveNewName)

    def _saveNewName(self):
        name = self.nameEdit.text()
        self.setter(name)
        self.nameButton.setText(name)
        self.nameEdit.setText(name)
        self._showEditable(False)

    def _editName(self, value):
        self.nameEdit.setText(self.getter())
        self._showEditable(True)

    def _showEditable(self, bool):
        self.nameEdit.setVisible(bool)
        self.nameButton.setVisible(not bool)

class MoveAlongWidget(QtWidgets.QWidget):

    # TODO : NO FIX STEP NUMBER! CALCULATED BASED ON NEIGHBOURS TEETH NUMBER
    STEP_NUMBER = 100

    def __init__(self, gearToMove, gearToMoveAlong, color):
        super(MoveAlongWidget, self).__init__()
        self.gearToMove = gearToMove
        self.gearToMoveAlong = gearToMoveAlong

        self.color = color
        self.ratio = None
        self.previousPos = None
        self.previousCursorVal = None

        self.buildUI()
        self.populate()

    def buildUI(self):
        layout = QtWidgets.QHBoxLayout(self)
        pixmap = QtGui.QPixmap(15, 15)
        pixmap.fill(QtGui.QColor(*self.color))

        btNew = QtWidgets.QToolButton()
        btNew.setIcon(QtGui.QIcon(pixmap))
        layout.addWidget(btNew)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        layout.addWidget(self.slider)

    def populate(self):

        stepNumber = self.gearToMoveAlong.gear.sides
        max_distance = self.gearToMove.calculateMoveAlong(self.gearToMoveAlong)
        # FIXME! NO REASON FOR THAT *2
        self.ratio = max_distance / stepNumber
        self.slider.setMaximum(stepNumber)
        self.previousPos = self._getGearPos()
        self.previousCursorVal = 0
        self.slider.setValue(0)

        py_helpers.disconnectSignals(
            self.slider.sliderPressed,
            self.slider.sliderReleased,
            self.slider.valueChanged)

        self.slider.sliderPressed.connect(
            lambda: self.gearToMove.activateMoveMode(self.gearToMoveAlong))
        self.slider.sliderReleased.connect(
            lambda: self.gearToMove.desactivateMoveMode())
        self.slider.valueChanged.connect(self._moveAlong)

    # FIXME!
    def _moveAlong(self, cursorVal):
        distance = (cursorVal - self.previousCursorVal) * self.ratio
        self.previousCursorVal = cursorVal
        self.gearToMove.moveAlong(distance)

    def _getGearPos(self):
        return self.gearToMove.translate[2]
        # NB : to change whern allowing multiple orientation.

class EnhancedSlider(QtWidgets.QWidget):

    SLIDER_STEP = 1
    MIN_MAX_FUNC_PREFIX = "calculate_"

    def __init__(
            self, label,
            min, max, step,
            getter, setter,
            numberEditMax=None):

        super(EnhancedSlider, self).__init__()

        self.label = label

        # TODO : if min or max ar functions: populate will be different !!!!!
        # automatically handled.

        self._setMinMaxStep(min, max, step)

        self.ratio = 0
        self.sliderMin = 0
        self.sliderMax = 0
        self.numberEditMax = numberEditMax

        #self._calculateData()

        self.getter = getter
        self.setter = setter

        self.val_bk = None

        self.buildUI()
        self.populate()

    def buildUI(self):
        self.layout = QtWidgets.QGridLayout(self)

        labelW = QtWidgets.QLabel(self.label)
        self.layout.addWidget(labelW, 0, 0)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.slider, 0, 1)
        # TODO : MAYBE A PUSHBUTTON HIDING NUMBER EDIT RAHTER THAN MODIFIABLE NAME.

        self.numberEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.numberEdit, 0, 2)

    def populate(self):
        currentVal = self.getter()
        self._calculateData()
        self.slider.setMinimum(self.sliderMin)
        self.slider.setMaximum(self.sliderMax)

        self.val_bk = currentVal
        self.numberEdit.setText(self._convToNumberEdit(currentVal))

        self.slider.setValue(self._convToSlider(currentVal))

        py_helpers.disconnectSignals(
            self.numberEdit.returnPressed,
            self.slider.valueChanged)

        self.numberEdit.returnPressed.connect(
            lambda: self._callback_numberEdit())
        self.slider.valueChanged.connect(
            lambda value: self._callback_slider(value))

    # Handling min max that can be either be number of func to calculate it.
    # *************************************************************************

    def _getMinMaxFuncName(arg):
        if arg not in ("min", "max"):
            return
        return EnhancedSlider.MIN_MAX_FUNC_PREFIX + arg

    def _getMinMaxFunc(self, arg):
        if arg not in ("min", "max"):
            return
        attrName = EnhancedSlider._getMinMaxFuncName(arg)
        if not hasattr(self, attrName):
            setattr(self, attrName, None)
        return getattr(self, attrName)

    def _setMinMaxStep(self, min=None, max=None, step=None):
        if step:
            self.step = step
        for argName, argValue in {
                "min": min,
                "max": max}.items():
            if argValue is None:
                pass
            elif py_helpers.isFuncOrMethod(argValue):
                setattr(self,
                        EnhancedSlider._getMinMaxFuncName(argName),
                        argValue)
            elif isinstance(argValue, numbers.Number):
                setattr(self, argName, argValue)
            else:
                log.error("{} is neither a number nor a function".format(
                    argName))

    def setMinMaxStep(self, min=None, max=None, step=None):
        self._setMinMaxStep(min, max, step)
        self._calculateData()

    def _calculateMinMaxFunc(self):
        for arg in ("min", "max"):
            func = self._getMinMaxFunc(arg)
            if func:
                setattr(self, arg, func())

    def disconnectSignals(*signals):
        for sig in signals:
            try : sig.disconnect()
            except Exception: pass

    # Actual calculation ******************************************************
    # TODO : BUG HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def _calculateData(self):

        self._calculateMinMaxFunc()

        step_number = (self.max - self.min) / self.step

        self.ratio = EnhancedSlider.SLIDER_STEP / step_number
        self.sliderMin = 0
        self.sliderMax = (self.max - self.min) / self.ratio

    # Callbacks ***************************************************************

    def _callback_numberEdit(self):
        value = self.numberEdit.text()
        try:
            value = float(value)
        except ValueError:
            self.numberEdit.setText(self._convToNumberEdit(value))
            return

        if self.numberEditMax:
            if value > self.numberEditMax:
                value = self.numberEditMax

        slider_val = self._convToSlider(value)
        if slider_val > self.sliderMax:
            slider_val = self.sliderMax

        self.slider.setValue(slider_val)
        self.setter(value)
        self.val_bk = value

    def _callback_slider(self, slider_value):
        value = self._convFromSlider(slider_value)
        self.numberEdit.setText(self._convToNumberEdit(value))
        self.setter(value)
        self.val_bk = value

    # Conversion **************************************************************

    def _convToSlider(self, val):
        return (val - self.min) / self.ratio

    def _convFromSlider(self, val):
        return round(((val * self.ratio) + self.min), 2)

    def _convToNumberEdit(self, val):
        return str(round(val, 2))

class GearSlider(EnhancedSlider):

    def __init__(
            self, gear,
            attributeName,
            min, max, step,
            numberEditMax=None):

        def getter(): return getattr(gear.gear, attributeName)
        def setter(value): setattr(gear.gear, attributeName, value)

        super(GearSlider, self).__init__(
            attributeName,
            min, max, step,
            getter, setter,
            numberEditMax)

class ItemWidget(QtWidgets.QWidget):

    _instancesByType = defaultdict(set)

    def __init__(
            self,
            itemType,
            objDescriptor):
        super(ItemWidget, self).__init__()
        self.__class__._instancesByType[itemType].add(self)
        self.itemType = itemType
        self.objDescriptor = objDescriptor
        self.buildUI()
        self.populate()

    def buildUI(self):

        self.layout = QtWidgets.QHBoxLayout(self)
        self.modifiableName = ModifiableName(
            self.objDescriptor.getName,
            self.objDescriptor.setName)
        self.layout.addWidget(self.modifiableName)

        self.visibleBtn = QtWidgets.QCheckBox("visible")
        self.layout.addWidget(self.visibleBtn)

        self.soloBtn = QtWidgets.QPushButton("solo")
        self.soloBtn.setCheckable(True)
        self._connectSolo()
        self.layout.addWidget(self.soloBtn)

        self.visibleBtn.toggled.connect(self._setObjVisible)

    def populate(self):
        self.visibleBtn.setChecked(self.objDescriptor.visibility)

    def _setSolo(self, visibility):

        if not visibility:
            self._safeSetVisibility(True)
            for itemWidget in self._listInstanceByItemType():
                if itemWidget != self:
                    itemWidget._safeSetVisibility(False)
        else:
            for itemWidget in self._listInstanceByItemType():
                itemWidget._safeSetVisibility(True)

    def _safeSetVisibility(self, visibility):
        self.objDescriptor.visibility = visibility
        py_helpers.disconnectSignals(self.visibleBtn.toggled)
        self.visibleBtn.setChecked(visibility)
        self.visibleBtn.toggled.connect(self._setObjVisible)

        if not visibility:
            self._safedesactivateSolo()

    def _setObjVisible(self, val):
        if val:
            for widget in self._listInstanceByItemType():
                widget._safedesactivateSolo()
        self.objDescriptor.visibility = val

    def _safedesactivateSolo(self):
        py_helpers.disconnectSignals(self.soloBtn.toggled)
        self.soloBtn.setChecked(False)
        self._connectSolo()

    def _connectSolo(self):
        try:
            self.soloBtn.toggled.connect(
                lambda val: self._setSolo(not val))
        except Exception:
            pass

    def listInstanceByItemType(itemType):
        return ItemWidget._instancesByType[itemType]

    def _listInstanceByItemType(self):
        return ItemWidget.listInstanceByItemType(self.itemType)

    def cleanByType(itemType):
        for instance in ItemWidget._instancesByType[itemType]:
            instance.setParent(None)
            instance.setVisible(False)
            instance.deleteLater()
        ItemWidget._instancesByType[itemType] = set()
