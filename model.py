from PyQt5 import QtCore, QtGui, QtWidgets
from Components.Cell import Cell
from Components.GOL_Board import GOL_Board
import os, sys, csv
import numpy as np

DIR_NAME = os.path.dirname(os.path.abspath('__file__'))

class GameOfLife(QtCore.QObject):

    NameItem = 1

    # Signal definition
    initViewSignal = QtCore.pyqtSignal()
    clearCellSignal = QtCore.pyqtSignal(object)
    fillCellSignal = QtCore.pyqtSignal(object)
    drawItemAtSingal = QtCore.pyqtSignal(list)
    finishUpdate = QtCore.pyqtSignal()
    setCheckedSignal = QtCore.pyqtSignal(bool)
    resetSignal = QtCore.pyqtSignal()
    scaleValueSignal = QtCore.pyqtSignal(float)
    historyFillSignal = QtCore.pyqtSignal(list)

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

        self._speed = 500       # evolution speed of GOL view
        self._zoom_count = 0    # number of zoom on the board

        # Timer     
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.speed)
        self.timer.timeout.connect(lambda : self.boardEvolution())

        self._history_running = False

        self._last_pattern = 'Empty'

        """ Model Signal """
        self.scene.aliveCellSignal.connect(self.fill_cell)
        self.scene.deadCellSignal.connect(self.clear_cell)
        self.finishUpdate.connect(self.update_state)
        self.resetSignal.connect(self.play_stop_evolution)

    # Getter methods for model attributes
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

    @property
    def last_pattern(self):
        return self._last_pattern

    # Setter methods for model attributes
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
    
    @last_pattern.setter
    def last_pattern(self, slot):
        self._last_pattern = slot


    # Init methods
    def init_board(self):
        """ Create an empty GOL grid, init the speedSlider and
            compute the GOL cells neighborhood
        """
        self.initViewSignal.emit()
        # self.createGridSignal.emit()
        self.create_grid()

    def create_grid(self):
        """ Create the Game of Life grid 
        """ 
        self.counterItems = 0
        for i in range(self.max_num_cell_x):
            for j in range(self.max_num_cell_y):
                self.drawItemAtSingal.emit([self.counterItems,i,j])
                self.boardCell = [self.counterItems, i, j]
                self.counterItems = self.counterItems + 1
        self.computeBoardNeighborhood()


    # Methods for cell neighborhood computation
    def computeBoardNeighborhood(self):
        [self.computeCellNeighborhood(self.scene.items()[i]) for i in range(len(self.scene.items()))]

    def computeCellNeighborhood(self, rect):
        """ Compute the cell neighborhood for a cell. That will be computed
            the first time that the cell is set to Alive. 
        """
        delta = int(self.scene.height()/self.cell_size)
        idx = self.get_rectId(rect)
        for x in range(-1,2):
            if idx-delta+x > 0:
                self.boardCell[idx].setNeighbor(self.boardCell[idx-delta+x])
            if x != 0 and idx+x < len(self.boardCell):
                self.boardCell[idx].setNeighbor(self.boardCell[idx+x])
            if idx+delta+x < len(self.boardCell):
                self.boardCell[idx].setNeighbor(self.boardCell[idx+delta+x])


    # Game Of Life engine methods
    def update_state(self):
        """ Change view in order to the updated cell state
        """
        for cell in self.boardCell:
            if cell._nextState.isAlive():
                self.fill_cell([cell._posx, cell._posy])
            else:
                self.clear_cell([cell._posx, cell._posy])

    def undo_state(self):
        """ Change view in order to undo the last move
        """
        for cell in self.boardCell:
            last_state = cell._lastStates.pop() if len(cell._lastStates)>1 else cell._lastStates[-1]
            if last_state.isAlive():
                self.fill_cell([cell._posx, cell._posy])
            else:
                self.clear_cell([cell._posx, cell._posy])

    def boardEvolution(self):
        """ For each cell on the GOL grid is computed its evolution based on the rules game
            If history_running is True, the last 5 states for each board cell is shown
            If history_running is False, the app will clear all the histrory cells
        """
        for i in range(len(self.boardCell)):
            self.boardCell[i].computeNextState()
        self.finishUpdate.emit()
        # show the history after the computation of new states
        if self.history_running:
            self.history()
        elif not self.history_running:
            self.clear_hist_board()
        
    def stop_evolution(self):
        """ Stop the timer of GOL loop 
        """
        self.timer.stop()

    def play_evolution(self):
        """ Start the timer of GOL loop
        """
        if self.running:
            self.timer.start()
            self.show_hist()

    def play_stop_evolution(self):
        """ Select the correct behavior according to the name of the pushButton that call this method
        """
        if (self.sender().objectName() == 'play') and (self.running==False):
            self.running = True
            self.play_evolution()
            
        else:
            self.stop_evolution()
            self.running = False
            self.setCheckedSignal.emit(False)


    # Getter for GOL cell info
    def get_rectId(self, rect):
        """ Get the int id of the cell from the string obtained from rect.data()
            position 0 correspond to the cell id
        """
        try:
            idx = rect.data(self.NameItem)[0]
        except Exception:
            pass
        return idx

    def get_rect(self, x, y):
        """ Return the item at the position (x,y) of the GOL board 
        """
        rect = self.scene.itemAt(x, y, QtGui.QTransform())
        idx = self.get_rectId(rect)
        currentState = self.boardCell[idx].isAlive()
        return rect, idx, currentState


    #  Methods for cell state management
    def fill_cell(self, pos):
        """ Fill the cell at current position (pos list of coordinates)
        """
        try:
            cell, idx, currentState = self.get_rect(pos[0], pos[1])
            self.boardCell[idx]._historical = False
            self.boardCell[idx].setToAlive()
            self.fillCellSignal.emit(cell)
        except Exception as e:
            pass
        
    def clear_cell(self, pos):
        """ Kill the cell at current position (pos list of coordinates)
        """
        try:
            cell, idx, currentState = self.get_rect(pos[0], pos[1])
            self.boardCell[idx]._historical = False
            self.boardCell[idx].setToDead()
            self.clearCellSignal.emit(cell)
        except Exception:
            pass
        
    def clear_board(self):
        """ Clear the GOL grid
        """
        self.resetSignal.emit()
        for i, cell in enumerate(self.boardCell):
            if cell.isAlive():
                self.clear_cell([cell._posx, cell._posy])
        self.clear_hist_board(resetting=True)

    def clear_hist_board(self, resetting=False):
        """ Clear all filled cell of history
            The cell last 5 states are resetted only when the user clear the board (clear button)
        """
        for cell in self.boardCell:
            if resetting:
                cell._lastStates = []
            if cell._historical and not cell.isAlive():
                rect, _, _ = self.get_rect(cell._posx, cell._posy)
                self.clearCellSignal.emit(rect)
    

    # Zoom buttons methods
    def zoom_view(self):
        """ Zooming the grid view according to the slider value
            The zoom count stores the number of user click:
                0 means no zoom; +5 is the max zoom in; -4 the min one
            "value" is the zoom factor, it's an empirical factor
        """
        if self.sender().objectName() == 'zoomOutButton' or self.sender().objectName() == 'Zoom_Out':
            self.zoom_count = self.zoom_count - 1
            value = 0.95 if self.zoom_count >=-4 else 1
            if self.zoom_count <= -4:
                self.zoom_count = -4
        else:
            self.zoom_count = self.zoom_count + 1
            value = 1.05 if self.zoom_count <= 5 else 1
            if self.zoom_count >= 5:
                self.zoom_count = 5
        self.scaleValueSignal.emit(value)


    # Saving Grid methods
    def saveAs_board(self):
        """ Save method where the user can choose where to save his results
        """
        try:
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            path = QtWidgets.QFileDialog.getSaveFileName(caption="Choose save folder", directory=DIR_NAME, options=options)
            if path != '':
                self.save_csv(str(path[0]))
        except Exception:
            pass

    def save_board(self):
        """ Autosave method for backup saving
        """
        savepath = DIR_NAME + "/backup-folder/autosave/"
        self.save_csv(savepath)

    def save_csv(self, savepath):
        """ Save the current state of the board in img
        """
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        if self.running:
            self.play_stop_evolution()
        savepath = savepath + '/board.csv'

        with open(savepath, 'w') as csvfile:
                filewriter = csv.writer(csvfile)
                for rect in self.scene.items():
                    if self.boardCell[self.get_rectId(rect)]._state.isAlive():
                        filewriter.writerow(rect.data(self.NameItem))
    

    # Loading Grid methods
    def load_board_with_path(self):
        """ Load a board from a folder
        """
        self.clear_board()
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        path = QtWidgets.QFileDialog.getExistingDirectory(caption="Choose folder to load", directory=DIR_NAME, options=options)
        if path != '':
            self.read_csv(path)

    def load_board_from_file(self):
        """ Load GOL board from file
        """
        try:
            self.clear_board()
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            file_path = QtWidgets.QFileDialog.getOpenFileName(caption="Choose csv file to load", directory=DIR_NAME, options=options)
            if file_path != '':
                self.read_csv(file_path[0])
        except Exception:
            pass
    
    def read_csv(self, file):
        """ Utility function from read alive cell to draw
        """
        if not os.path.isfile(file):
            file = file + '/board.csv'
        with open(file, 'r') as csvfile:
            for line in csvfile.readlines():
                line = line.replace('\n', '').split(',')
                self.fill_cell( [self.boardCell[int(line[0])]._posx, self.boardCell[int(line[0])]._posy] )


    #  Speed Slider methords
    def change_speed(self, value): 
        """ Change cell evolution speed [ms]
        """
        self.speed = (2002 - value)
        if self.speed <= 0:
            self.speed = 2
        self.timer.setInterval(self.speed)


    # History methods
    def show_hist(self):
        """ Show history while the timer is running or clear the history board
        """ 
        if self.history_running and self.timer.isActive():
            self.history()
        elif not self.history_running:
            self.clear_hist_board()
    
    def history(self):
        """Show the last 5 alive states before the present one
        """
        for cell in self.boardCell:
            rect,_,currentState = self.get_rect(cell._posx, cell._posy)
            for i,ls in enumerate(cell._lastStates):
                 if ls.isAlive() and not currentState:
                    cell._historical = True
                    decay = len(cell._lastStates) - i
                    self.historyFillSignal.emit([rect,decay])


    # Grid pattern methods
    def set_pattern(self, pattern=None, text=None):
        """ Set the pattern selected by the user 
        """
        self.clear_board()
        if pattern == 'Empty' or text == 'Empty':
            self.last_pattern = 'Empty'
        elif pattern == 'Random' or text == 'Random':
            self.last_pattern = 'Random'
            self.random_board()
        elif pattern == 'Die Hard' or text == 'Die Hard':
            self.last_pattern = 'Die Hard'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Die Hard')
        elif pattern == 'R Pentomino' or text == 'R Pentomino':
            self.last_pattern = 'R Pentomino'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/R-Pentomino')
        elif pattern == 'Block-laying Switch Engine' or text == 'Block-laying Switch Engine':
            self.last_pattern = 'Block-laying Switch Engine'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Block-laying Switch Engine')
        elif pattern == 'Block-laying Switch Engine v2' or text == 'Block-laying Switch Engine v2':
            self.last_pattern = 'Block-laying Switch Engine v2'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Block-laying Switch Engine v2')
        elif pattern == 'Gosper Gilder Gun' or text == 'Gosper Gilder Gun':
            self.last_pattern = 'Gosper Gilder Gun'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Gosper Gilder Gun')
        else:
            self.load_board_from_file()


    def random_board(self):
        """ Inizialize random state for all cells in the GOL board
        """
        for cell in self.boardCell:
            # 0.7 because we don't want to fill to much cells (empirical value)
            if np.random.random() > 0.7:
                self.fill_cell([cell._posx, cell._posy])