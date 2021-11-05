import logging
from Maya_GearCreator.Qt import QtWidgets, QtCore, QtGui
from functools import partial

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# TODO : BACKUP NAME!
# IF NAME EMPTY -> cancel
# IF TRANSFORM WITH THIS NAME ALREADY EXISTS SAME.
# HOOVER.


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

        self.nameEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.nameEdit, 0, 1)
        self.nameSave = QtWidgets.QPushButton("Save")
        self.layout.addWidget(self.nameSave, 0, 3, 0, 1)
        self.nameSave.clicked.connect(
            lambda value: self._saveNewName(value))

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

    def delete(self):  # TODO: why not __del__
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

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

        stepNumber = self.gearToMoveAlong.tNumber
        max_distance = self.gearToMoveAlong.calculateMoveAlong()  # FIXME! NO REASON FOR THAT *2
        self.ratio = max_distance / stepNumber
        self.slider.setMaximum(stepNumber)
        self.previousPos = self._getGearPos()
        self.previousCursorVal = 0
        self.slider.setValue(0)

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
        pos = self.gearToMove.gearTransform.getTransform().translate.get()
        return pos[2]  # NB : to change whern allowing multiple orientation.
