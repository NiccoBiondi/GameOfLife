from PyQt5 import QtGui, QtCore, QtWidgets
from model import GameOfLife
from view import GOL_View

import sys

if __name__ == '__main__':
    gol = QtWidgets.QApplication(sys.argv)
    GOL_model = GameOfLife()
    GOL_view = GOL_View(GOL_model) 

    """ Start Game of Life engine """
    GOL_model.init_board()

    GOL_view.show()
    sys.exit(gol.exec_())