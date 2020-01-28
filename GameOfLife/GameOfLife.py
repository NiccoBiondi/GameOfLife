from PyQt5 import QtGui, QtCore, QtWidgets
import sys
# sys.path.insert(1, os.path.dirname(os.path.abspath('__file__')))
from model import GameOfLife
from controller import GOL_Controller
from view import GOL_View

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    GOL_model = GameOfLife()
    GOL_controller = GOL_Controller(GOL_model)
    GOL_view = GOL_View(GOL_model, GOL_controller)

    """ Start Game of Life """
    GOL_model.init_board()

    GOL_view.show()
    sys.exit(app.exec_())