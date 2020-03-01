
from PyQt5 import QtCore, QtGui, QtWidgets

class GOL_Board(QtWidgets.QGraphicsScene):

    # Signal definition
    aliveCellSignal = QtCore.pyqtSignal(object)
    deadCellSignal = QtCore.pyqtSignal(object)

    def __init__(self):
        QtWidgets.QGraphicsScene.__init__(self)

    def mousePressEvent(self, event):
        """Function called when the user click one GOL cell
        """
        try:
            ep = event.scenePos()

            # left click fill cell
            if event.button() == QtCore.Qt.LeftButton:
                self.aliveCellSignal.emit([ep.x(), ep.y()])

            #rigth click clear cell
            elif event.button() == QtCore.Qt.RightButton:
                self.deadCellSignal.emit([ep.x(), ep.y()])

        except Exception:
            pass

    def mouseMoveEvent(self, event):
        """Function called when the user move the mouse after one click 
        """
        try:
            ep = event.scenePos()

            if event.buttons() == QtCore.Qt.LeftButton:
                self.aliveCellSignal.emit([ep.x(), ep.y()])
            
            elif event.buttons() == QtCore.Qt.RightButton:
                self.deadCellSignal.emit([ep.x(), ep.y()])

        except Exception as e:
            pass