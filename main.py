from ui.base_gui import BaseGUI
from PyQt5 import QtWidgets
from datetime import datetime
import sys
import traceback

log_file_name = 'labed.log'  # имя файла ведения лога при ошибках


# Ловчий ошибок
def excepthook_catcher(t, v, tb):
    with open(log_file_name, 'w') as file:
        file.write("\n-------------- Errors --------------\n")
        file.write("Time = %s\n" % datetime.now().strftime("%d.%m.%Y"))
        traceback.print_exception(t, v, tb, file=file)


# Стандартная инициализация
class MyWindow(BaseGUI):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Label Dataset Editor")


if __name__ == '__main__':
    try:
        file = open(log_file_name, 'r+')
    except IOError:
        file = open(log_file_name, 'w+')
    sys.excepthook = excepthook_catcher
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
