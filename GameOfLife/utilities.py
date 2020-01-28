############################ BOARD BEHAVIOR #####################################

def init_board(self):
    """Create an empty GOL grid, init the speedSlider and
    compute the GOL cells neighborhood
    """
    self.create_grid()
    self.ui.grid.centerOn(QtCore.QPointF(MAX_WINDOW_DIM[0]/2, MAX_WINDOW_DIM[1]/2))
    self.init_speedSlider()
    self.computeBoardNeighborhood()

def create_grid(self):
    """Create the Game of Life grid 
    """ 
    self._counterItems = 0
    for i in range(MAX_NUM_CELL_X):
        for j in range(MAX_NUM_CELL_Y):
            self.draw_cell(i,j)
            self._counterItems += 1

################################# SPEED SLIDER #################

def init_speedSlider(self):
    """Define behavior for the speed slider 
    """
    self.ui.speedSlider.setMinimum(400)
    self.ui.speedSlider.setMaximum(2000)
    self.ui.speedSlider.setValue(1200)
    self.ui.speedSlider.valueChanged.connect(self.change_speed)
    self.ui.speedSlider.sliderMoved.connect(self.change_speed)

def change_speed(self): 
    """Change cell evolution speed [ms]
    """
    self._speed = 2050 - self.ui.speedSlider.value()
    self._timer.setInterval(self._speed)

###################### GAME OF LIFE ENGINE ########################

def stop_evolution(self):
    """Stop the timer of GOL loop 
    """
    self._timer.stop()

def play_evolution(self):
    """Start the timer of GOL loop
    """
    if self._running:
        self._timer.start()

def play_stop_evolution(self):
    """Select the correct behavior according to the name of the pushButton
    """
    if (self.sender().objectName() == 'play') and (self._running==False):
        self._running = True
        self.play_evolution()
    else:
        self.stop_evolution()
        self._running = False
        self.ui.play.setChecked(False)


############################ CELL BEHAVIOR #####################################
def update_state(self):
    """Change view in order to the updated cell state
    """
    for cell in self._boardCell:
        if cell._nextState.isAlive():
            self.fill_cell(cell)
        else:
            self.clear_cell(cell)

def undo_state(self):
    """Change view in order to undo the last move
    """
    for cell in self._boardCell:
        last_state = cell._lastStates.pop() if len(cell._lastStates)>1 else cell._lastStates[-1]
        if last_state.isAlive():
            self.fill_cell(cell)
        else:
            self.clear_cell(cell)


def boardEvolution(self):
    """For each cell on the GOL grid is computed its evolution based on the rules game
    """
    for i in range(len(self._boardCell)):
        self._boardCell[i].computeNextState()
    self.finishUpdate.emit()


##################################### OTHER FUNCTIONALITIES ######################

def get_rectId(self, rect):
    """Get the int id of the cell from  the string obtained from rect.data()
    """
    return rect.data(GOL_View.NameItem)[0]

def save_csv(self, savepath):
    """Save the current state of the board in png img
    """
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    if self._running:
        self.play_stop_evolution()
    pixmap = QtGui.QPixmap(savepath)
    pixmap = self.ui.grid.grab(self.ui.grid.sceneRect().toRect())
    pixmap.save(savepath +'/board.png')
    savepath = savepath + '/board.csv'

    with open(savepath, 'w') as csvfile:
            filewriter = csv.writer(csvfile)
            for rect in self._scene.items():
                if self._boardCell[self.get_rectId(rect)]._state.isAlive():
                    filewriter.writerow(rect.data(GOL_View.NameItem))

