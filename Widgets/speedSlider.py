from PyQt5 import QtCore, QtGui, QtWidgets

class SpeedSlider(QtWidgets.QSlider):

    pointClicked = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        QtWidgets.QSlider.__init__(self, parent)
        self._value = 0
    
    def mousePressEvent(self, event):
        """Set the slider value to the clicked value and emit signal
        """
        self._value = self.maximum() * event.x() // self.width()
        self.setValue(self._value)
        # self.valueChanged.emit(self._speed)
        # # self.pointClicked.emit(self._value)

    def mouseMoveEvent(self, event):
        self._value = self.maximum() * event.x() // self.width()
        self.setValue(self._value)
        if self._value % 100 == 0:
            self.valueChanged.emit(self._value)

    def mouseReleaseEvent(self, event):
        """Function called when the muose was released 
        """
        self.valueChanged.emit(self._value)