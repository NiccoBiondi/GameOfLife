
from PyQt5 import QtCore, QtGui, QtWidgets

class GOL_Board(QtWidgets.QGraphicsScene):

    # Signal definition
    # eventPosSignal = QtCore.pyqtSignal(list)
    aliveCellSignal = QtCore.pyqtSignal(object)
    deadCellSignal = QtCore.pyqtSignal(object)

    def __init__(self):
        QtWidgets.QGraphicsScene.__init__(self)

    def mousePressEvent(self, event):
        """Function called when the user click one GOL cell
        """
        try:
            ep = event.scenePos()
            # self.eventPosSignal.emit([ep.x(), ep.y()])
            # rect, idx, currentState = self.view.controller.get_rect(ep.x(), ep.y())

            # left click fill cell
            if event.button() == QtCore.Qt.LeftButton:
                # if not currentState:
                #     self.view.fill_cell(rect)
                self.aliveCellSignal.emit([ep.x(), ep.y()])

            #rigth click clear cell
            elif event.button() == QtCore.Qt.RightButton:
                # if currentState:
                #     self.view.clear_cell(rect)
                self.deadCellSignal.emit([ep.x(), ep.y()])

        except Exception:
            pass

    def mouseMoveEvent(self, event):
        """Function called when the user move the mouse after one click 
        """
        try:
            ep = event.scenePos()
            # self.eventPosSignal.emit([ep.x(), ep.y()])
            # rect, idx, currentState = self.view.get_rect(ep.x(), ep.y())

            if event.buttons() == QtCore.Qt.LeftButton:
                # if not currentState:
                #     self.view.fill_cell(rect)
                self.aliveCellSignal.emit([ep.x(), ep.y()])
            
            elif event.buttons() == QtCore.Qt.RightButton:
                # if currentState:
                #     self.view.clear_cell(rect)
                self.deadCellSignal.emit([ep.x(), ep.y()])

        except Exception as e:
            pass
        
    def mouseReleaseEvent(self, event):
        """Function called when the muose was released 
        """
        pass