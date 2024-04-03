from ui.base_gui import BaseGUI
from PyQt5 import QtWidgets
import sys


# Base class for Application
class MyWindow(BaseGUI):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ML Editor")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())