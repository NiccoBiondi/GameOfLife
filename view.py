from build.Ui_GameOfLife import Ui_GameOfLife
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, qApp, QGraphicsScene
from PyQt5 import QtGui, QtCore, QtWidgets
import sys, os, csv
import numpy as np

from Components.Cell import Cell

DIR_NAME = os.path.dirname(os.path.abspath('__file__'))

# Define RGB color intensity
GRAY = (150,150,161)
BLUE = (22,22,199)
ORANGE = (240,129,19)
YELLOW = (240,201,2)

HISTORY_1 = (224,157,1)     
HISTORY_2 = (191, 134, 0)
HISTORY_3 = (156,109,0)
HISTORY_4 = (133,93,0)
HISTORY_5 = (115,81,0)

CELL_ALIVE_COLOR = QtGui.QColor(240,201,2)
BACKGROUND_COLOR = CELL_DEAD_COLOR = QtGui.QColor(150,150,161)

class GOL_View(QMainWindow):

    # Signal definition
    speedChanged = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()

    def __init__(self, model):
        super().__init__()

        self.model = model

        # Set up the user interface from Designer.
        self.ui = Ui_GameOfLife()
        self._pen = QtGui.QPen(QtCore.Qt.lightGray)

        # Model signal 
        self.model.initViewSignal.connect(self.init_view)
        self.model.drawItemAtSingal.connect(self.draw_cell)
        self.model.fillCellSignal.connect(self.fill_cell)
        self.model.clearCellSignal.connect(self.clear_cell)
        self.model.historyFillSignal.connect(self.change_cell_intensity)
        self.model.resetSignal.connect(self.set_parBoard)

    def init_view(self):
        """ Disable scroll of the page and draw the entire GOL grid 
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
        """ Set the default scale to GOL view when it's cleared
        """
        scale_value = 0
        if self.model.zoom_count > 0:
            scale_value = 0.95 ** self.model.zoom_count
        elif self.model.zoom_count < 0:
            scale_value = 0.95 ** self.model.zoom_count
        else:
            scale_value = 1.0
        self.ui.grid.centerOn(QtCore.QPointF(self.model.max_window_dim[0]/2, self.model.max_window_dim[1]/2))
        self.ui.grid.scale(scale_value,scale_value)
        self.model.zoom_count = 0

    def connect(self):
        """ Connect push buttons to their functionality
        """
        # Add functionality when buttons are clicked
        self.ui.clear.clicked.connect(lambda : self.clear_pushed())
        self.ui.loadButton.clicked.connect(lambda : self.model.load_board_with_path())
        self.ui.zoomInButton.clicked.connect(lambda : self.model.zoom_view())
        self.ui.zoomOutButton.clicked.connect(lambda : self.model.zoom_view())
        self.ui.save.clicked.connect(lambda : self.model.save_board())
        self.ui.play.clicked.connect(lambda : self.model.play_stop_evolution())
        self.ui.play.setCheckable(True)

        # Add functionality when QActions are triggered
        self.ui.New.triggered.connect(lambda : self.clear_pushed())
        self.ui.Next_Move.triggered.connect(lambda : self.nextMove())
        self.ui.Open.triggered.connect(lambda : self.model.load_board_from_file())
        self.ui.Save.triggered.connect(lambda : self.model.save_board())
        self.ui.Save_As.triggered.connect(lambda : self.model.saveAs_board())
        self.ui.Zoom_In.triggered.connect(lambda : self.model.zoom_view())
        self.ui.Zoom_Out.triggered.connect(lambda : self.model.zoom_view())
        self.ui.History.triggered.connect(lambda : self.history_action())
        self.ui.History.setCheckable(True)

        self.ui.actionRandom.triggered.connect(lambda : self.model.set_pattern(text="Random"))
        self.ui.actionDie_Hard.triggered.connect(lambda : self.model.set_pattern(text="Die Hard"))
        self.ui.actionR_Pentomino.triggered.connect(lambda : self.model.set_pattern(text="R Pentomino"))
        self.ui.actionBlock_laying_Switch_Engine.triggered.connect(lambda : self.model.set_pattern(text="Block-laying Switch Engine"))
        self.ui.actionBlock_laying_Switch_Engine_v2.triggered.connect(lambda : self.model.set_pattern(text="Block-laying Switch Engine v2"))
        self.ui.actionGosper_GIlder_Gun.triggered.connect(lambda : self.model.set_pattern(text="Gosper Gilder Gun"))

        self.ui.Quit.triggered.connect(lambda : sys.exit())

        self.ui.historyCheckBox.stateChanged.connect(lambda : self.check_history())        
        self.ui.patternBox.activated.connect(lambda : self.model.set_pattern(self.ui.patternBox.currentText()))

        self.model.setCheckedSignal.connect(lambda : self.ui.play.setChecked(False))
        self.model.scaleValueSignal.connect(self.change_scaleView)


    def init_speedSlider(self):
        """ Define behavior for the speed slider 
        """
        self.ui.speedSlider.setMinimum(400)
        self.ui.speedSlider.setMaximum(2000)
        self.ui.speedSlider.setValue(1200)
        self.ui.speedSlider.valueChanged.connect(self.model.change_speed)
        self.ui.speedSlider.sliderMoved.connect(self.model.change_speed)

    def change_scaleView(self, value):
        """ Zooming the grid view according to the value 
        """
        self.ui.grid.centerOn(QtCore.QPointF(self.model.max_window_dim[0]/2, self.model.max_window_dim[1]/2)) 
        self.ui.grid.scale(value,value)

    def draw_cell(self, data):
        """ Draw cell in the grid at pos (list of coordinates of graphic scene)
        """
        i, j = data[1], data[2]
        rect = QtWidgets.QGraphicsRectItem(i*self.model.cell_size, j*self.model.cell_size, self.model.cell_size, self.model.cell_size)
        rect.setPen(self._pen)
        self.model.scene.addItem(rect)
        # Add functional data to GOL cell
        rect.setData(self.model.NameItem, data)

    def fill_cell(self, cell, color=CELL_ALIVE_COLOR):
        """ Fill the selected cell
        """
        cell.setBrush( QtGui.QBrush( color ) )

    def clear_cell(self, cell, color=CELL_DEAD_COLOR):
        """ Clear the selected cell 
        """
        cell.setBrush( QtGui.QBrush( color ) )

    def nextMove(self):
        """ When the Next action is triggered, that action will stop the board evolution
        """
        self.model.play_stop_evolution()
        self.model.boardEvolution()
    
    def change_cell_intensity(self, data):
        """ Change cell color intensity based on the decay index
        """
        rect = data[0]
        decay = data[1]
        if decay == 1:
            new_color_intensity = HISTORY_1
        elif decay == 2:
            new_color_intensity = HISTORY_2
        elif decay == 3:
            new_color_intensity = HISTORY_4
        elif decay == 4:
            new_color_intensity = HISTORY_4
        else:
            new_color_intensity = HISTORY_5
        color = QtGui.QColor(new_color_intensity[0], new_color_intensity[1], new_color_intensity[2])
        self.fill_cell(rect, color)

    def check_history(self):
        """ Set model attribute history running like the status of the check box
        """
        self.model.history_running = self.ui.historyCheckBox.isChecked()

    def history_action(self):
        """ Function called when History action is triggered. Here the user can observed
            the history of the previous state, and also stop the board evolution.
            If clicked twice, the history will be deleted from the grid
        """
        if not self.ui.History.isChecked():             
            self.ui.History.setChecked(False)
            self.model.clear_hist_board()

        elif self.ui.History.isChecked():
            self.ui.History.setChecked(True)
            self.model.play_stop_evolution()
            self.model.history()  

    def clear_pushed(self):
        """ Clear the GOL grid and set the pattern to Empty (default one)
        """
        self.model.clear_board()
        self.ui.patternBox.setCurrentIndex(0)

