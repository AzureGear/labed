from PyQt5 import QtWidgets, QtGui, QtCore


class PageMNIST(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)

        # Создаем текстовое поле для примера
        self.text_field = QtWidgets.QTextEdit(self)
        self.name = "MNIST"
        # Устанавливаем разметку для виджетов на вкладке
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text_field)
