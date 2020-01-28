from build.Ui_GameOfLife import Ui_GameOfLife
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, qApp, QGraphicsScene
from PyQt5 import QtGui, QtCore, QtWidgets
import sys, time, os, csv
import numpy as np

from Cell import Cell, AliveState, DeadState

DIR_NAME = os.path.dirname(os.path.abspath('__file__'))

# Define RGB color intensity
GRAY = (150,150,161)
BLUE = (22,22,199)
ORANGE = (240,129,19)
YELLOW = (240,201,2)
YELLOW_1 = (224, 187, 0)
YELLOW_2 = (207, 173, 0)
YELLOW_3 = (179,149,0)
YELLOW_4 = (152,132,0)
YELLOW_5 = (130,108,0)

CELL_ALIVE_COLOR = QtGui.QColor(240,201,2)
BACKGROUND_COLOR = CELL_DEAD_COLOR = QtGui.QColor(150,150,161)

class GOL_View(QMainWindow):

    # Signal definition
    # finishUpdate = QtCore.pyqtSignal()
    speedChanged = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()

    def __init__(self, model, controller):
        super().__init__()

        self.model = model
        self.controller = controller

        # Set up the user interface from Designer.
        self.ui = Ui_GameOfLife()
        self._pen = QtGui.QPen(QtCore.Qt.lightGray)

        # Model signal 
        self.model.initViewSignal.connect(self.init_view)
        self.controller.drawItemAtSingal.connect(self.draw_cell)
        self.controller.fillCellSignal.connect(self.fill_cell)
        self.controller.clearCellSignal.connect(self.clear_cell)
        self.controller.historyFillSignal.connect(self.change_cell_intensity)
        self.controller.resetSignal.connect(self.set_parBoard)

    def init_view(self):
        """Disable scroll of the page and draw the entire GOL grid 
        """
        # Inizialize the QDesigner view
        self.ui.setupUi(self)
        self.ui.grid.setScene(self.model.scene)
        self.ui.grid.setBackgroundBrush( QtGui.QBrush(BACKGROUND_COLOR, QtCore.Qt.SolidPattern))        
        # Disabling scroll area and scroll bar for the view.
        self.ui.grid.verticalScrollBar().blockSignals(True)
        self.ui.grid.horizontalScrollBar().blockSignals(True)
        self.ui.grid.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ui.grid.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ui.grid.centerOn(QtCore.QPointF(self.model.max_window_dim[0]/2, self.model.max_window_dim[1]/2))
        self.ui.grid.scale(self.model.initialScale, self.model.initialScale)

        self.init_speedSlider()
        self.connect()
    
    def set_parBoard(self):
        """Set the default scale to GOL view when it's cleared
        """
        scale_value = 0
        if self.model.zoom_count > 0:
            scale_value = 0.95 ** self.model.zoom_count
        elif self.model.zoom_count < 0:
            scale_value = 1.05 ** self.model.zoom_count
        else:
            scale_value = 1.0
        self.ui.grid.centerOn(QtCore.QPointF(self.model.max_window_dim[0]/2, self.model.max_window_dim[1]/2))
        self.ui.grid.scale(scale_value,scale_value)

    def connect(self):
        """Connect push buttons to their functionality
        """
        self.ui.clear.clicked.connect(lambda : self.controller.clear_board())
        self.ui.loadButton.clicked.connect(lambda : self.controller.load_board_with_path())
        self.ui.zoomInButton.clicked.connect(lambda : self.controller.zoom_view())
        self.ui.zoomOutButton.clicked.connect(lambda : self.controller.zoom_view())
        self.ui.save.clicked.connect(lambda : self.controller.save_board())
        self.ui.play.clicked.connect(lambda : self.controller.play_stop_evolution())
        self.ui.play.setCheckable(True)

        # Add functionality where QActions are triggered
        self.ui.New.triggered.connect(lambda : self.controller.clear_board())
        self.ui.Next_Move.triggered.connect(lambda : self.nextMove())
        self.ui.History.triggered.connect(lambda : self.controller.history())
        self.ui.Open.triggered.connect(lambda : self.controller.load_board_from_file())
        self.ui.Save.triggered.connect(lambda : self.controller.save_board())
        self.ui.Save_As.triggered.connect(lambda : self.controller.saveAs_board())
        self.ui.Zoom_In.triggered.connect(lambda : self.controller.zoom_view())
        self.ui.Zoom_Out.triggered.connect(lambda : self.controller.zoom_view())

        self.ui.historyCheckBox.stateChanged.connect(lambda : self.check_history())
        
        self.ui.patternBox.activated.connect(lambda : self.controller.set_pattern(self.ui.patternBox.currentText()))

        self.controller.setCheckedSignal.connect(lambda : self.ui.play.setChecked(False))
        self.controller.scaleValueSignal.connect(self.change_scaleView)


    def init_speedSlider(self):
        """Define behavior for the speed slider 
        """
        self.ui.speedSlider.setMinimum(400)
        self.ui.speedSlider.setMaximum(2000)
        self.ui.speedSlider.setValue(1200)
        self.ui.speedSlider.valueChanged.connect(self.controller.change_speed)
        self.ui.speedSlider.sliderMoved.connect(self.controller.change_speed)

    def change_scaleView(self, value):
        """Zooming the grid view according to the value 
        """
        self.ui.grid.centerOn(QtCore.QPointF(self.model.max_window_dim[0]/2, self.model.max_window_dim[1]/2)) 
        self.ui.grid.scale(value,value)

    def draw_cell(self, data):
        """Draw cell in the grid at pos (list of coordinates of graphic scene)
        """
        i, j = data[1], data[2]
        rect = QtWidgets.QGraphicsRectItem(i*self.model.cell_size, j*self.model.cell_size, self.model.cell_size, self.model.cell_size)
        rect.setPen(self._pen)
        self.model.scene.addItem(rect)
        # Add functional data to GOL cell
        rect.setData(self.model.NameItem, data)

    def fill_cell(self, cell, color=CELL_ALIVE_COLOR):
        """Fill the cell 
        """
        cell.setBrush( QtGui.QBrush( color ) )

    def clear_cell(self, cell, color=CELL_DEAD_COLOR):
        """Kill the cell 
        """
        cell.setBrush( QtGui.QBrush( color ) )

    def nextMove(self):
        """When the Next action is triggered, 
        """
        self.controller.play_stop_evolution()
        self.controller.boardEvolution()
    
    def change_cell_intensity(self, data):
        """Change cell color intensity based on the decay index
        """
        rect = data[0]
        decay = data[1]
        if decay == 1:
            new_color_intensity = YELLOW_1
        elif decay == 2:
            new_color_intensity = YELLOW_2
        elif decay == 3:
            new_color_intensity = YELLOW_4
        elif decay == 4:
            new_color_intensity = YELLOW_4
        else:
            new_color_intensity = YELLOW_5
        color = QtGui.QColor(new_color_intensity[0], new_color_intensity[1], new_color_intensity[2])
        self.fill_cell(rect, color)

    def check_history(self):
        """
        """
        self.model.history_running = self.ui.historyCheckBox.isChecked()
        # self.controller.play_stop_evolution()