from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys, csv
import numpy as np

DIR_NAME = os.path.dirname(os.path.abspath('__file__'))

class GOL_Controller(QtCore.QObject):

    # Signal definition
    clearCellSignal = QtCore.pyqtSignal(object)
    fillCellSignal = QtCore.pyqtSignal(object)
    drawItemAtSingal = QtCore.pyqtSignal(list)
    finishUpdate = QtCore.pyqtSignal()
    setCheckedSignal = QtCore.pyqtSignal(bool)
    resetSignal = QtCore.pyqtSignal()
    scaleValueSignal = QtCore.pyqtSignal(float)
    historyFillSignal = QtCore.pyqtSignal(list)
    
    def __init__(self, model):
        super().__init__()

        self.model = model

        # Signal connecting
        self.model.createGridSignal.connect(self.create_grid)
        self.model.scene.aliveCellSignal.connect(self.fill_cell)
        self.model.scene.deadCellSignal.connect(self.clear_cell)
        self.model.boardEvolutionSignal.connect(self.boardEvolution)

        self.finishUpdate.connect(self.update_state)
        self.resetSignal.connect(self.play_stop_evolution)

    def create_grid(self):
        """Create the Game of Life grid 
        """ 
        self.counterItems = 0
        for i in range(self.model.max_num_cell_x):
            for j in range(self.model.max_num_cell_y):
                self.drawItemAtSingal.emit([self.model.counterItems,i,j])
                self.model.boardCell = [self.model.counterItems, i, j]
                self.model.counterItems = self.model.counterItems + 1
        self.computeBoardNeighborhood()

    def computeBoardNeighborhood(self):
        [self.computeCellNeighborhood(self.model.scene.items()[i]) for i in range(len(self.model.scene.items()))]

    def computeCellNeighborhood(self, rect):
        """Compute the cell neighborhood for a cell. That will be computed
        the first time that the cell is set to Alive. 
        """
        delta = int(self.model.scene.height()/self.model.cell_size)
        idx = self.get_rectId(rect)
        for x in range(-1,2):
            if idx-delta+x > 0:
                self.model.boardCell[idx].setNeighbor(self.model.boardCell[idx-delta+x])
            if x != 0 and idx+x < len(self.model.boardCell):
                self.model.boardCell[idx].setNeighbor(self.model.boardCell[idx+x])
            if idx+delta+x < len(self.model.boardCell):
                self.model.boardCell[idx].setNeighbor(self.model.boardCell[idx+delta+x])

    def get_rectId(self, rect):
        """Get the int id of the cell from  the string obtained from rect.data()
        """
        try:
            idx = rect.data(self.model.NameItem)[0]
        except Exception:
            pass
        return idx

    def get_rect(self, x, y):
        """Return the item at the position (x,y) of the GOL board 
        """
        rect = self.model.scene.itemAt(x, y, QtGui.QTransform())
        idx = self.get_rectId(rect)
        currentState = self.model.boardCell[idx].isAlive()
        return rect, idx, currentState

    def fill_cell(self, pos):
        """Fill the cell at current position (pos list of coordinates)
        """
        try:
            cell, idx, currentState = self.get_rect(pos[0], pos[1])
            self.model.boardCell[idx]._historical = False
            self.model.boardCell[idx].setToAlive()
            self.fillCellSignal.emit(cell)
        except Exception:
            pass
    def clear_cell(self, pos):
        """Kill the cell at current position (pos list of coordinates)
        """
        try:
            cell, idx, currentState = self.get_rect(pos[0], pos[1])
            self.model.boardCell[idx]._historical = False
            self.model.boardCell[idx].setToDead()
            self.clearCellSignal.emit(cell)
        except Exception:
            pass
        
    def clear_board(self):
        """Clear the GOL grid
        """
        self.resetSignal.emit()
        for i, cell in enumerate(self.model.boardCell):
            if cell._state.isAlive():
                self.clear_cell([cell._posx, cell._posy])
        self.clear_hist_board(resetting=True)
        
    def clear_hist_board(self, resetting=False):
        """Clear all filled cell of history
        """
        for cell in self.model.boardCell:
            if resetting:
                cell._lastStates = []
            if cell._historical and not cell._state.isAlive():
                rect, _, _ = self.get_rect(cell._posx, cell._posy)
                self.clearCellSignal.emit(rect)
    
    def zoom_view(self):
        """Zooming the grid view according to the value 
        """
        if self.sender().objectName() == 'zoomOutButton' or self.sender().objectName() == 'Zoom_Out':
            self.model.zoom_count = self.model.zoom_count - 1
            value = 0.95 if self.model.zoom_count >=-5 else 1
            if self.model.zoom_count <= -5:
                self.model.zoom_count = -5
        else:
            self.model.zoom_count = self.model.zoom_count + 1
            value = 1.05 if self.model.zoom_count <= 5 else 1
            if self.model.zoom_count >= 5:
                self.model.zoom_count = 5
        self.scaleValueSignal.emit(value)

    def saveAs_board(self):
        """Save method where the user can choose where to save his results
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
        """Autosave method for backup saving
        """
        savepath = DIR_NAME + "/backup-folder/autosave/"
        self.save_csv(savepath)

    def load_board_with_path(self):
        """Load a board from a folder
        """
        self.clear_board()
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        path = QtWidgets.QFileDialog.getExistingDirectory(caption="Choose folder to load", directory=DIR_NAME, options=options)
        if path != '':
            self.read_csv(path)

    def load_board_from_file(self):
        """Load GOL board from file
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
    
    def change_speed(self, value): 
        """Change cell evolution speed [ms]
        """
        self.model.speed = (2002 - value)
        if self.model.speed <= 0:
            self.model.speed = 2
        self.model.timer.setInterval(self.model.speed)

    ###################### GAME OF LIFE ENGINE ########################
    def update_state(self):
        """Change view in order to the updated cell state
        """
        for cell in self.model.boardCell:
            if cell._nextState.isAlive():
                self.fill_cell([cell._posx, cell._posy])
            else:
                self.clear_cell([cell._posx, cell._posy])

    def undo_state(self):
        """Change view in order to undo the last move
        """
        for cell in self.model.boardCell:
            last_state = cell._lastStates.pop() if len(cell._lastStates)>1 else cell._lastStates[-1]
            if last_state.isAlive():
                self.fill_cell([cell._posx, cell._posy])
            else:
                self.clear_cell([cell._posx, cell._posy])

    def boardEvolution(self):
        """For each cell on the GOL grid is computed its evolution based on the rules game
        """
        for i in range(len(self.model.boardCell)):
            self.model.boardCell[i].computeNextState()
        self.finishUpdate.emit()
        # show the history after the computation of new states
        if self.model.history_running:
            self.history()
        elif not self.model.history_running:
            self.clear_hist_board()
        
    def stop_evolution(self):
        """Stop the timer of GOL loop 
        """
        self.model.timer.stop()

    def play_evolution(self):
        """Start the timer of GOL loop
        """
        if self.model.running:
            self.model.timer.start()
            self.show_hist()
    
    def show_hist(self):
        # show history while the timer is running
        if self.model.history_running and self.model.timer.isActive():
            self.history()
        elif not self.model.history_running:
            self.clear_hist_board()


    def play_stop_evolution(self):
        """Select the correct behavior according to the name of the pushButton
        """
        if (self.sender().objectName() == 'play') and (self.model.running==False):
            self.model.running = True
            self.play_evolution()
            
        else:
            self.stop_evolution()
            self.model.running = False
            self.setCheckedSignal.emit(False)

    def history(self):
        """Show the last 5 alive states before the present one
        """
        for cell in self.model.boardCell:
            rect,_,currentState = self.get_rect(cell._posx, cell._posy)
            for i,ls in enumerate(cell._lastStates):
                 if ls.isAlive() and not currentState:
                    cell._historical = True
                    decay = len(cell._lastStates) - i
                    self.historyFillSignal.emit([rect,decay])

    def save_csv(self, savepath):
        """Save the current state of the board in img
        """
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        if self.model.running:
            self.play_stop_evolution()
        savepath = savepath + '/board.csv'

        with open(savepath, 'w') as csvfile:
                filewriter = csv.writer(csvfile)
                for rect in self.model.scene.items():
                    if self.model.boardCell[self.get_rectId(rect)]._state.isAlive():
                        filewriter.writerow(rect.data(self.model.NameItem))

    def read_csv(self, file):
        """Utility function from read alive cell to draw
        """
        if not os.path.isfile(file):
            file = file + '/board.csv'
        with open(file, 'r') as csvfile:
            for line in csvfile.readlines():
                line = line.replace('\n', '').split(',')
                self.fill_cell( [self.model.boardCell[int(line[0])]._posx, self.model.boardCell[int(line[0])]._posy] )
                    
    def set_pattern(self, pattern=None, text=None):
        """Set the pattern choosed by the user 
        """
        self.clear_board()
        if pattern == 'Empty' or text == 'Empty':
            self.model.last_pattern = 'Empty'
        elif pattern == 'Random' or text == 'Random':
            self.model.last_pattern = 'Random'
            self.random_board()
        elif pattern == 'Die Hard' or text == 'Die Hard':
            self.model.last_pattern = 'Die Hard'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Die Hard')
        elif pattern == 'R Pentomino' or text == 'R Pentomino':
            self.model.last_pattern = 'R Pentomino'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/R-Pentomino')
        elif pattern == 'Block-laying Switch Engine' or text == 'Block-laying Switch Engine':
            self.model.last_pattern = 'Block-laying Switch Engine'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Block-laying Switch Engine')
        elif pattern == 'Block-laying Switch Engine v2' or text == 'Block-laying Switch Engine v2':
            self.model.last_pattern = 'Block-laying Switch Engine v2'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Block-laying Switch Engine v2')
        elif pattern == 'Gosper Gilder Gun' or text == 'Gosper Gilder Gun':
            self.model.last_pattern = 'Gosper Gilder Gun'
            self.read_csv(DIR_NAME+'/backup-folder/pattern/Gosper Gilder Gun')
        else:
            self.load_board_from_file()


    def random_board(self):
        """Inizialize random state for all cells in the GOL board
        """
        for cell in self.model.boardCell:
            # 0.7 because we don't want to fill to much cells
            if np.random.random() > 0.7:
                self.fill_cell([cell._posx, cell._posy])