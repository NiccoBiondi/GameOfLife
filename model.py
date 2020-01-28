from PyQt5 import QtCore, QtGui
from Cell import Cell
from GOL_Board import GOL_Board
import os, sys
import numpy as np

DIR_NAME = os.path.dirname(os.path.abspath('__file__'))

class GameOfLife(QtCore.QObject):

    NameItem = 1

    # Signal definition
    initViewSignal = QtCore.pyqtSignal()
    createGridSignal = QtCore.pyqtSignal()
    drawItemAtSingal = QtCore.pyqtSignal(list)
    boardEvolutionSignal = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()

        """ Model attribute """ 

        self._cell_size = 20
        self._max_window_dim = (800, 600)
        self._max_num_cell_x = int(self.max_window_dim[0]*2/self.cell_size)
        self._max_num_cell_y = int(self.max_window_dim[1]*2/self.cell_size)

        self._scene = GOL_Board()
        self._initialScale = 0.7

        self._running = False
        self._counterItems = 0 
        self._boardDim = self.max_window_dim       
        self._boardCell = np.zeros((self.max_window_dim[0]//10)*(self.max_window_dim[1]//10)).tolist()

        self._speed = 500       # to memorize speed of update of GOL view
        self._zoom_count = 0    # to memorize the number of zoom on the board

        # Timer     
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.speed)
        self.timer.timeout.connect(lambda : self.boardEvolutionSignal.emit())

        self._history_running = False

    """ Getter methods for model attributes """
    @property
    def cell_size(self):
        return self._cell_size

    @property
    def max_window_dim(self):
        return self._max_window_dim
    
    @property
    def max_num_cell_x(self):
        return self._max_num_cell_x
    
    @property
    def max_num_cell_y(self):
        return self._max_num_cell_y

    @property
    def speed(self):
        return self._speed
    
    @property
    def zoom_count(self):
        return self._zoom_count

    @property
    def running(self):
        return self._running

    @property
    def counterItems(self):
        return self._counterItems
    
    @property
    def boardCell(self):
        return self._boardCell
    
    @property
    def boardDim(self):
        return self._boardDim

    @property
    def scene(self):
        return self._scene
    
    @property
    def history_running(self):
        return self._history_running

    @property
    def hist_view(self):
        return self._hist_view

    @property
    def initialScale(self):
        return self._initialScale

    """ Setter methods for model attributes """
    @speed.setter
    def speed(self, slot):
        self._speed = slot
    
    @zoom_count.setter
    def zoom_count(self, slot):
        self._zoom_count = slot
    
    @running.setter
    def running(self, slot):
        self._running = slot

    @counterItems.setter
    def counterItems(self, slot):
        self._counterItems = slot

    @boardCell.setter
    def boardCell(self, slot):
        self._boardCell[slot[0]] = Cell(slot[1]*self.cell_size, slot[2]*self.cell_size)

    @history_running.setter
    def history_running(self, slot):
        self._history_running = slot

    @hist_view.setter
    def hist_view(self, slot):
        self._hist_view = slot
    
    def init_board(self):
        """Create an empty GOL grid, init the speedSlider and
        compute the GOL cells neighborhood
        """
        self.initViewSignal.emit()
        self.createGridSignal.emit()

    