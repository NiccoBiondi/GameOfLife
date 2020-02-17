class CellState(object):
    """Abstract CellState class
    """
    def isAlive(self):
        """Checks whether the state is Live
        """
        raise NotImplementedError


class DeadState(CellState):
    """State representing a Dead Cell
    """
    def __init__(self):
        self.state = False

    def isAlive(self):
        """Checks whether the state is LiveState
        """
        return self.state

    def __nonzero__(self):
        return False


class AliveState(CellState):
    """State representing Live Cell
    """
    def __init__(self):
        self.state = True

    def isAlive(self):
        """Checks whether the state is LiveState
        """
        return self.state

    def __nonzero__(self):
        return True


class Cell(object):
    """Represents a Cell. Either DeadState or AliveState.
    """
    def __init__(self, x, y, state=DeadState(), historical=False):
        super().__init__()

        self._posx = x
        self._posy = y
        self._state = state
        self._nextState = self._state
        self._lastStates = []
        self._neighbors = []
        self._historical = historical

    def setNeighbor(self, cell):
        """Add neighbor cells.
        """
        self._neighbors.append(cell)

    def numOfLiveNeighbors(self):
        """Find the number of live neighbors for this cell.
        """
        return len(list(filter(lambda x: x.isAlive(), self._neighbors)))

    def computeNextState(self):
        """Determines whether this cell should live or die based on the
        number of live neighbors.
        """
        aliveNeighbors = self.numOfLiveNeighbors()
        if aliveNeighbors < 2 or aliveNeighbors > 3:
            self.setNextToDead()

        if not self.isAlive() and aliveNeighbors == 3:
            self.setNextToAlive()

    def isAlive(self):
        """Checks whether this cell is alive.
        """
        return self._state.isAlive()
    
    def setToDead(self, state=DeadState()):
        """Set cell state to dead
        """
        if len(self._lastStates) > 5:
            self._lastStates.pop(0)
        self._lastStates.append(self._state)
        self._state = state
        self._nextState = self._state
        return self._state
    
    def setToAlive(self, state=AliveState()):
        """Set cell state to alive
        """
        if len(self._lastStates) > 5:
            self._lastStates.pop(0)
        self._lastStates.append(self._state)
        self._state = state
        self._nextState = self._state
        return self._state

    def setNextToAlive(self, nextState=AliveState()):
        """Set future cell state to alive
        """
        self._nextState = nextState
        return self._nextState

    def setNextToDead(self, nextState=DeadState()):
        """Set future cell state to dead
        """
        self._nextState = nextState
        return self._nextState

    def set_historical(boolean):
        self._historical = boolean
